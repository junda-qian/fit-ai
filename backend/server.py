from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import os
from dotenv import load_dotenv
from typing import Optional, List, Dict
import json
import uuid
from datetime import datetime
import boto3
from botocore.exceptions import ClientError
from context import get_health_prompt
from retrieval import HealthRAG
from energy_calculator import EnergyCalculator, EnergyCalculatorInput, EnergyCalculatorOutput
from workout_planner import WorkoutPlanner, WorkoutPlannerInput, WorkoutPlanOutput
from strength_standards import (
    calculate_1rm,
    determine_training_status,
    calculate_overall_status
)

# Import tracking system components
from models import (
    UserProfile, UserProfileCreate,
    WorkoutPlan, WorkoutPlanCreate,
    NutritionLog, NutritionLogCreate,
    WorkoutLog, WorkoutLogCreate,
    BodyLog, BodyLogCreate,
    DailySummary
)
from database import db
from datetime import date, timedelta
from food_database import food_db
from models import FoodSearchResult

# Load environment variables
load_dotenv()

app = FastAPI()

# Configure CORS
origins = os.getenv("CORS_ORIGINS", "http://localhost:3000,http://localhost:3001").split(",")
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=False,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["*"],
)

# Initialize Bedrock client
bedrock_client = boto3.client(
    service_name="bedrock-runtime",
    region_name=os.getenv("DEFAULT_AWS_REGION", "us-east-1")
)

# Bedrock model selection
BEDROCK_MODEL_ID = os.getenv("BEDROCK_MODEL_ID", "amazon.nova-lite-v1:0")

# Memory storage configuration
USE_S3 = os.getenv("USE_S3", "false").lower() == "true"
S3_BUCKET = os.getenv("S3_BUCKET", "")
MEMORY_DIR = os.getenv("MEMORY_DIR", "../memory")

# Initialize S3 client if needed
if USE_S3:
    s3_client = boto3.client("s3")

# Initialize RAG system
USE_OPENSEARCH = os.getenv("USE_OPENSEARCH", "false").lower() == "true"
rag_system = HealthRAG(use_opensearch=USE_OPENSEARCH)

# Initialize Workout Planner
workout_planner = WorkoutPlanner(bedrock_client=bedrock_client, model_id=BEDROCK_MODEL_ID)


# Request/Response models
class ChatRequest(BaseModel):
    message: str
    session_id: Optional[str] = None


class ChatResponse(BaseModel):
    response: str
    session_id: str


class Message(BaseModel):
    role: str
    content: str
    timestamp: str


# Memory management functions
def get_memory_path(session_id: str) -> str:
    return f"{session_id}.json"


def load_conversation(session_id: str) -> List[Dict]:
    """Load conversation history from storage"""
    if USE_S3:
        try:
            response = s3_client.get_object(Bucket=S3_BUCKET, Key=get_memory_path(session_id))
            return json.loads(response["Body"].read().decode("utf-8"))
        except ClientError as e:
            if e.response["Error"]["Code"] == "NoSuchKey":
                return []
            raise
    else:
        # Local file storage
        file_path = os.path.join(MEMORY_DIR, get_memory_path(session_id))
        if os.path.exists(file_path):
            with open(file_path, "r") as f:
                return json.load(f)
        return []


def save_conversation(session_id: str, messages: List[Dict]):
    """Save conversation history to storage"""
    if USE_S3:
        s3_client.put_object(
            Bucket=S3_BUCKET,
            Key=get_memory_path(session_id),
            Body=json.dumps(messages, indent=2),
            ContentType="application/json",
        )
    else:
        # Local file storage
        os.makedirs(MEMORY_DIR, exist_ok=True)
        file_path = os.path.join(MEMORY_DIR, get_memory_path(session_id))
        with open(file_path, "w") as f:
            json.dump(messages, f, indent=2)


def call_bedrock_with_context(user_message: str, context: str) -> str:
    """Call AWS Bedrock with retrieved context"""

    # Generate system prompt with context
    system_prompt = get_health_prompt(context)

    # Build messages in Bedrock format
    messages = [
        {
            "role": "user",
            "content": [{"text": f"System: {system_prompt}"}]
        },
        {
            "role": "user",
            "content": [{"text": user_message}]
        }
    ]

    try:
        # Call Bedrock using the converse API
        response = bedrock_client.converse(
            modelId=BEDROCK_MODEL_ID,
            messages=messages,
            inferenceConfig={
                "maxTokens": 2000,
                "temperature": 0.3,  # Lower temperature for more factual responses
                "topP": 0.9
            }
        )

        # Extract the response text
        return response["output"]["message"]["content"][0]["text"]

    except ClientError as e:
        error_code = e.response['Error']['Code']
        if error_code == 'ValidationException':
            print(f"Bedrock validation error: {e}")
            raise HTTPException(status_code=400, detail="Invalid message format for Bedrock")
        elif error_code == 'AccessDeniedException':
            print(f"Bedrock access denied: {e}")
            raise HTTPException(status_code=403, detail="Access denied to Bedrock model")
        else:
            print(f"Bedrock error: {e}")
            raise HTTPException(status_code=500, detail=f"Bedrock error: {str(e)}")


@app.get("/")
async def root():
    stats = rag_system.get_stats()
    return {
        "message": "Evidence-Based Health Chatbot API",
        "memory_enabled": True,
        "storage": "S3" if USE_S3 else "local",
        "ai_model": BEDROCK_MODEL_ID,
        "vector_store": stats
    }


@app.get("/health")
async def health_check():
    stats = rag_system.get_stats()
    return {
        "status": "healthy",
        "use_s3": USE_S3,
        "bedrock_model": BEDROCK_MODEL_ID,
        "vector_store": stats
    }


@app.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest):
    try:
        # Generate session ID if not provided
        session_id = request.session_id or str(uuid.uuid4())

        # Load conversation history
        conversation = load_conversation(session_id)

        # Retrieve relevant context from medical documents
        context, sources = rag_system.retrieve_context(request.message, top_k=5)

        # Call Bedrock with context for response
        assistant_response = call_bedrock_with_context(request.message, context)

        # Update conversation history
        conversation.append(
            {"role": "user", "content": request.message, "timestamp": datetime.now().isoformat()}
        )
        conversation.append(
            {
                "role": "assistant",
                "content": assistant_response,
                "timestamp": datetime.now().isoformat(),
            }
        )

        # Save conversation
        save_conversation(session_id, conversation)

        return ChatResponse(response=assistant_response, session_id=session_id)

    except HTTPException:
        raise
    except Exception as e:
        print(f"Error in chat endpoint: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/conversation/{session_id}")
async def get_conversation(session_id: str):
    """Retrieve conversation history"""
    try:
        conversation = load_conversation(session_id)
        return {"session_id": session_id, "messages": conversation}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/stats")
async def get_stats():
    """Get RAG system statistics"""
    try:
        stats = rag_system.get_stats()
        return stats
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/calculate-energy", response_model=EnergyCalculatorOutput)
async def calculate_energy(input_data: EnergyCalculatorInput):
    """
    Calculate energy expenditure and intake metrics

    Accepts user's physical attributes and training schedule,
    returns calculated energy metrics including BMR, energy expenditure,
    and target energy intake.
    """
    try:
        result = EnergyCalculator.calculate_all(input_data)
        return result
    except Exception as e:
        print(f"Error in energy calculation: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/generate-workout-plan", response_model=WorkoutPlanOutput)
async def generate_workout_plan(input_data: WorkoutPlannerInput):
    """
    Generate a personalized workout plan using AI

    Accepts user's training profile (training status, age, sex, recovery factor, etc.)
    and generates a customized workout plan that:
    - Calculates optimal training volume per muscle group
    - Selects appropriate exercises from the exercise database
    - Distributes volume across training days
    - Sets appropriate intensities based on training level

    The workout plan is generated using AWS Bedrock LLM to create flexible,
    personalized programs that meet all specified constraints.
    """
    try:
        result = workout_planner.generate_workout_plan(input_data)
        return result
    except Exception as e:
        print(f"Error in workout plan generation: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


# ==================== TRACKING SYSTEM ENDPOINTS ====================
# These endpoints handle saving and retrieving tracking data

# ---------- User Profile Endpoints ----------
# These save/get the results from the Energy Calculator

@app.post("/api/user-profile", response_model=UserProfile)
async def create_user_profile(profile: UserProfileCreate):
    """
    Save user's targets from Energy Calculator

    What this does:
    1. After user completes energy calculator, frontend sends targets here
    2. We check if profile already exists for this user
    3. If exists: UPDATE the profile with new values
    4. If not: CREATE new profile
    5. Save to database

    Why we need this:
    - Dashboard needs to know user's daily targets
    - Tracking page compares actual intake vs targets
    """
    try:
        # Check if profile already exists
        existing = db.find_one("user_profiles", {"user_id": profile.user_id})

        if existing:
            # Update existing profile
            profile_dict = profile.dict()
            profile_dict['updated_at'] = datetime.now().isoformat()
            db.update("user_profiles", {"user_id": profile.user_id}, profile_dict)
            return UserProfile(**profile_dict, id=existing['id'], created_at=existing['created_at'])
        else:
            # Create new profile
            profile_obj = UserProfile(**profile.dict())
            profile_dict = profile_obj.dict()
            profile_dict = json.loads(json.dumps(profile_dict, default=str))
            db.insert("user_profiles", profile_dict)
            return profile_obj
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/user-profile/{user_id}")
async def get_user_profile(user_id: str):
    """
    Get user's profile and targets

    What this does:
    - Dashboard calls this to get daily calorie/macro targets
    - Returns the saved profile from database

    Returns 404 if user hasn't completed calculator yet
    """
    try:
        profile = db.find_one("user_profiles", {"user_id": user_id})
        if not profile:
            raise HTTPException(status_code=404, detail="Profile not found. Please complete Energy Calculator first.")
        return profile
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ---------- Workout Plan Endpoints ----------
# These save/get the generated workout plan

@app.post("/api/workout-plan", response_model=WorkoutPlan)
async def create_workout_plan(plan: WorkoutPlanCreate):
    """
    Save workout plan from Workout Planner

    What this does:
    1. After AI generates workout plan, frontend sends it here
    2. Deactivate any previous active plans (user can only have 1 active plan)
    3. Save new plan as active

    Why we need this:
    - Workout logging needs to know which exercises to show
    - Dashboard displays current active plan
    """
    try:
        # Deactivate any existing active plans
        db.update(
            "workout_plans",
            {"user_id": plan.user_id, "active": True},
            {"active": False, "deactivated_at": datetime.now().isoformat()}
        )

        # Create new active plan
        plan_obj = WorkoutPlan(**plan.dict())
        plan_dict = plan_obj.dict()
        plan_dict = json.loads(json.dumps(plan_dict, default=str))
        db.insert("workout_plans", plan_dict)
        return plan_obj
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/workout-plan/{user_id}/active")
async def get_active_workout_plan(user_id: str):
    """
    Get user's currently active workout plan

    Returns the plan that's currently being followed
    """
    try:
        plan = db.find_one("workout_plans", {"user_id": user_id, "active": True})
        if not plan:
            raise HTTPException(status_code=404, detail="No active workout plan found")
        return plan
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/estimate-training-status")
async def estimate_training_status(request: Dict):
    """
    Estimate user's training status based on their best lifts

    Analyzes workout logs for the 4 key exercises (Bench Press, Overhead Press,
    Deadlift, Squat) and determines training status using ExRx.net standards.

    Request body:
    {
      "user_id": "...",
      "bodyweight_kg": 75,
      "sex": "male"
    }

    Returns:
    {
      "overall_status": "Intermediate",
      "exercises": {
        "Bench Press": {"1rm": 85.0, "status": "Intermediate"},
        "Press": {"1rm": 55.0, "status": "Intermediate"},
        "Deadlift": {"1rm": 140.0, "status": "Intermediate"},
        "Squat": {"1rm": 120.0, "status": "Advanced"}
      },
      "recommendation": "Current training status: Intermediate. Recommended intensity: 80% for compounds, 65% for isolations."
    }
    """
    try:
        user_id = request['user_id']
        bodyweight = request['bodyweight_kg']
        sex = request['sex']

        # Get user's workout logs
        workout_logs = db.find("workout_logs", {"user_id": user_id})

        # Key exercises to analyze
        key_exercises = {
            "Bench Press": ["bench press", "barbell bench press"],
            "Press": ["overhead press", "press", "barbell overhead press", "dumbbell overhead press"],
            "Deadlift": ["deadlift", "powerlifting deadlift", "romanian deadlift"],
            "Squat": ["squat", "barbell squat", "back squat"]
        }

        best_lifts = {}

        # Find best performance for each key exercise
        for standard_name, exercise_variations in key_exercises.items():
            best_1rm = 0

            for log in workout_logs:
                for exercise in log.get('exercises', []):
                    exercise_name_lower = exercise['name'].lower()

                    # Check if exercise matches any variation
                    if any(variation in exercise_name_lower for variation in exercise_variations):
                        # Find heaviest set
                        for set_data in exercise['sets']:
                            weight = set_data.get('weight', 0)
                            reps = set_data.get('reps', 0)

                            if weight > 0 and reps > 0:
                                # Calculate 1RM for this set
                                estimated_1rm = calculate_1rm(weight, reps)

                                if estimated_1rm > best_1rm:
                                    best_1rm = estimated_1rm

            # Determine status if user has performed this exercise
            if best_1rm > 0:
                status = determine_training_status(
                    standard_name, best_1rm, bodyweight, sex
                )
                best_lifts[standard_name] = {
                    "1rm": round(best_1rm, 1),
                    "status": status
                }

        # Calculate overall status
        if best_lifts:
            statuses = [lift['status'] for lift in best_lifts.values()]
            overall_status = calculate_overall_status(statuses)
        else:
            overall_status = "Novice"  # Default if no data

        # Generate recommendation based on status
        intensity_recommendations = {
            "Untrained": {"compound": 60, "isolation": 60},
            "Novice": {"compound": 60, "isolation": 60},
            "Intermediate": {"compound": 80, "isolation": 65},
            "Advanced": {"compound": 85, "isolation": 70},
            "Elite": {"compound": 85, "isolation": 70}
        }

        intensity = intensity_recommendations.get(overall_status, {"compound": 60, "isolation": 60})
        recommendation = f"Current training status: {overall_status}. Recommended intensity: {intensity['compound']}% for compound exercises, {intensity['isolation']}% for isolation exercises."

        return {
            "overall_status": overall_status,
            "exercises": best_lifts,
            "recommendation": recommendation
        }

    except KeyError as e:
        raise HTTPException(status_code=400, detail=f"Missing required field: {str(e)}")
    except Exception as e:
        print(f"Error estimating training status: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


# ---------- Nutrition Logging Endpoints ----------
# These handle meal/food logging

@app.post("/api/nutrition/logs", response_model=NutritionLog)
async def create_nutrition_log(log: NutritionLogCreate):
    """
    Log a meal or snack

    What this does:
    1. User logs breakfast/lunch/dinner/snack
    2. Save to nutrition_logs collection
    3. Update daily summary (so dashboard loads fast)

    Example:
    User logs: "Breakfast - Oatmeal, Banana, Protein Powder - 450 cal"
    """
    try:
        log_obj = NutritionLog(**log.dict())
        log_dict = log_obj.dict()
        log_dict = json.loads(json.dumps(log_dict, default=str))
        db.insert("nutrition_logs", log_dict)

        # Update daily summary
        await _update_daily_summary(log.user_id, log.date)

        return log_obj
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/nutrition/logs")
async def get_nutrition_logs(
    user_id: str,
    start_date: date,
    end_date: date
):
    """
    Get nutrition logs for date range

    Max 31 days to prevent huge queries
    Used for: Nutrition history page, calendar view
    """
    try:
        # Validate date range (prevent huge queries)
        if (end_date - start_date).days > 31:
            raise HTTPException(status_code=400, detail="Max 31 days per request")

        # Find all logs for this user
        all_logs = db.find("nutrition_logs", {"user_id": user_id})

        # Filter by date range
        filtered_logs = [
            log for log in all_logs
            if start_date <= datetime.fromisoformat(log['date']).date() <= end_date
        ]

        # Sort by date and time (most recent first)
        filtered_logs.sort(key=lambda x: (x['date'], x['time']), reverse=True)

        return {
            "logs": filtered_logs,
            "total_count": len(filtered_logs)
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ---------- Workout Logging Endpoints ----------
# These handle workout session logging

@app.post("/api/workout/logs", response_model=WorkoutLog)
async def create_workout_log(log: WorkoutLogCreate):
    """
    Log a completed workout session

    What this does:
    1. User finishes workout
    2. Logs all exercises, sets, reps, weights
    3. Save to workout_logs collection
    4. TRAINING AGENT: Analyze each exercise and generate next session recommendations
    5. Update daily summary

    Example:
    "Upper Body A - Bench Press 3x8 @ 185lbs, Rows 3x10 @ 135lbs..."
    """
    try:
        log_obj = WorkoutLog(**log.dict())
        log_dict = log_obj.dict()
        log_dict = json.loads(json.dumps(log_dict, default=str))
        db.insert("workout_logs", log_dict)

        # TRAINING AGENT: Analyze each exercise and generate recommendations
        try:
            from pathlib import Path
            import sys
            sys.path.insert(0, str(Path(__file__).parent.parent))

            from ai_agents.training_specialist.algorithm import analyze_exercise_session
            from ai_agents.shared.models import Set, Session, ExerciseConfig

            for exercise in log.exercises:
                # Get or create exercise config
                exercise_name = exercise['name'] if isinstance(exercise, dict) else exercise.name
                config_data = _get_or_create_exercise_config(log.user_id, exercise_name)
                config = ExerciseConfig(**config_data)

                # Get session history (last 8 sessions)
                session_history = _get_exercise_session_history(log.user_id, exercise_name, limit=8)

                # Convert sets to Set models
                exercise_sets = exercise['sets'] if isinstance(exercise, dict) else exercise.sets
                sets = [Set(weight=s['weight'], reps=s['reps']) if isinstance(s, dict) else Set(weight=s.weight, reps=s.reps) for s in exercise_sets]

                if sets:  # Only analyze if there are sets
                    # Get current and last successful weights
                    current_weight = sets[0].weight
                    last_successful_weight = config_data.get('last_successful_weight', 0) or current_weight

                    # Analyze session
                    recommendation = analyze_exercise_session(
                        exercise_name=exercise_name,
                        sets_logged=sets,
                        config=config,
                        session_history=session_history,
                        current_weight=current_weight,
                        last_successful_weight=last_successful_weight,
                    )

                    # Store recommendation
                    _store_training_recommendation(log.user_id, recommendation, log.date)

                    # Update exercise config
                    _update_exercise_config(log.user_id, exercise_name, recommendation, current_weight)

                    # Check for training status progression
                    _check_and_update_training_status(log.user_id, exercise_name, sets)
        except Exception as e:
            # Don't fail the whole request if training agent fails
            print(f"Training agent error: {e}")
            import traceback
            traceback.print_exc()

        # Update daily summary
        await _update_daily_summary(log.user_id, log.date)

        return log_obj
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/workout/logs")
async def get_workout_logs(
    user_id: str,
    start_date: date,
    end_date: date
):
    """
    Get workout logs for date range

    Used for: Workout history page, progress tracking
    """
    try:
        # Validate date range
        if (end_date - start_date).days > 31:
            raise HTTPException(status_code=400, detail="Max 31 days per request")

        # Find all logs for this user
        all_logs = db.find("workout_logs", {"user_id": user_id})

        # Filter by date range
        filtered_logs = [
            log for log in all_logs
            if start_date <= datetime.fromisoformat(log['date']).date() <= end_date
        ]

        # Sort by date (most recent first)
        filtered_logs.sort(key=lambda x: x['date'], reverse=True)

        return {
            "logs": filtered_logs,
            "total_count": len(filtered_logs)
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ---------- Body Logging Endpoints ----------
# These handle weight and body composition tracking

@app.post("/api/body/logs", response_model=BodyLog)
async def create_body_log(log: BodyLogCreate):
    """
    Log body weight and measurements

    What this does:
    1. User weighs themselves
    2. Optionally measures body fat %
    3. Save to body_logs collection
    4. Update daily summary (for dashboard weight display)

    Example:
    User logs: "75.5 kg, 15% body fat"
    """
    try:
        log_obj = BodyLog(**log.dict())
        log_dict = log_obj.dict()
        log_dict = json.loads(json.dumps(log_dict, default=str))
        db.insert("body_logs", log_dict)

        # Update daily summary
        await _update_daily_summary(log.user_id, log.date)

        return log_obj
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/body/logs")
async def get_body_logs(
    user_id: str,
    start_date: date,
    end_date: date
):
    """
    Get body logs for date range

    Used for: Weight history page, progress charts
    """
    try:
        all_logs = db.find("body_logs", {"user_id": user_id})

        # Filter by date range
        filtered_logs = [
            log for log in all_logs
            if start_date <= datetime.fromisoformat(log['date']).date() <= end_date
        ]

        # Sort by date (most recent first)
        filtered_logs.sort(key=lambda x: x['date'], reverse=True)

        return filtered_logs
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ---------- Food Search Endpoint ----------
# USDA FoodData Central search

@app.get("/api/food/search", response_model=FoodSearchResult)
async def search_foods(query: str, page_size: int = 10):
    """
    Search USDA FoodData Central database

    What this does:
    1. User types food name (e.g., "chicken breast")
    2. We call USDA API
    3. Parse and simplify the complex response
    4. Return clean list of foods with nutrition info

    Example:
    GET /api/food/search?query=banana&page_size=5

    Returns:
    {
      "query": "banana",
      "total_results": 82,
      "foods": [
        {
          "fdc_id": 173944,
          "description": "Banana, raw",
          "calories": 89,
          "protein": 1.09,
          "carbs": 22.84,
          "fats": 0.33,
          "serving_size": "100",
          "serving_unit": "g"
        },
        ...
      ]
    }

    Args:
        query: Food name to search (e.g., "banana", "chicken")
        page_size: Number of results (default 10, max 50)

    Returns:
        List of matching foods with nutrition info
    """
    try:
        if not query or len(query) < 2:
            raise HTTPException(status_code=400, detail="Query must be at least 2 characters")

        if page_size > 50:
            page_size = 50

        results = food_db.search_foods(query, page_size)
        return results

    except HTTPException:
        raise
    except Exception as e:
        print(f"Food search error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


# ---------- Daily Summary Endpoints ----------
# These provide fast aggregated data for dashboard

@app.get("/api/summary/daily")
async def get_daily_summary(user_id: str, date: date):
    """
    Get aggregated summary for a specific day

    What this returns:
    - Total calories, protein, carbs, fats for the day
    - Number of workouts completed
    - Weight (if logged)
    - Targets (from user profile)
    - Progress percentages (actual vs target)

    Why this is fast:
    - Pre-computed summaries (updated when logs are added)
    - Dashboard doesn't have to sum all meals every time
    """
    try:
        # Check if summary exists
        summary = db.find_one("daily_summaries", {"user_id": user_id, "date": date.isoformat()})

        if not summary:
            # Compute summary if it doesn't exist
            summary = await _compute_daily_summary(user_id, date)

        # Get user profile for targets
        profile = db.find_one("user_profiles", {"user_id": user_id})

        if profile:
            summary['targets'] = {
                "calories": profile['target_calories'],
                "protein": profile['target_protein'],
                "carbs": profile['target_carbs'],
                "fats": profile['target_fats']
            }

            # Calculate progress percentages
            summary['progress'] = {
                "calories_pct": round((summary['total_calories'] / profile['target_calories']) * 100) if profile['target_calories'] > 0 else 0,
                "protein_pct": round((summary['total_protein'] / profile['target_protein']) * 100) if profile['target_protein'] > 0 else 0,
                "carbs_pct": round((summary['total_carbs'] / profile['target_carbs']) * 100) if profile['target_carbs'] > 0 else 0,
                "fats_pct": round((summary['total_fats'] / profile['target_fats']) * 100) if profile['target_fats'] > 0 else 0,
            }

        return summary
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/summary/range")
async def get_daily_summaries_range(
    user_id: str,
    start_date: date,
    end_date: date
):
    """
    Get daily summaries for a date range

    Used for: Progress charts, weekly/monthly views
    Returns an array of daily summaries with targets and progress
    """
    try:
        # Validate date range
        if (end_date - start_date).days > 90:
            raise HTTPException(status_code=400, detail="Max 90 days per request")

        # Get all summaries for this user
        all_summaries = db.find("daily_summaries", {"user_id": user_id})

        # Filter by date range
        filtered_summaries = [
            summary for summary in all_summaries
            if start_date <= datetime.fromisoformat(summary['date']).date() <= end_date
        ]

        # Get user profile for targets
        profile = db.find_one("user_profiles", {"user_id": user_id})

        # Add targets and progress to each summary
        for summary in filtered_summaries:
            if profile:
                summary['targets'] = {
                    "calories": profile['target_calories'],
                    "protein": profile['target_protein'],
                    "carbs": profile['target_carbs'],
                    "fats": profile['target_fats']
                }

                # Calculate progress percentages
                summary['progress'] = {
                    "calories_pct": round((summary['total_calories'] / profile['target_calories']) * 100) if profile['target_calories'] > 0 else 0,
                    "protein_pct": round((summary['total_protein'] / profile['target_protein']) * 100) if profile['target_protein'] > 0 else 0,
                    "carbs_pct": round((summary['total_carbs'] / profile['target_carbs']) * 100) if profile['target_carbs'] > 0 else 0,
                    "fats_pct": round((summary['total_fats'] / profile['target_fats']) * 100) if profile['target_fats'] > 0 else 0,
                }

        # Sort by date (most recent first)
        filtered_summaries.sort(key=lambda x: x['date'], reverse=True)

        return filtered_summaries
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ---------- Helper Functions ----------
# These compute and update summaries

async def _compute_daily_summary(user_id: str, target_date: date) -> Dict:
    """
    Compute daily summary from logs

    This sums up all nutrition logs and counts workouts for a specific day
    """
    # Get all nutrition logs for the day
    nutrition_logs = db.find("nutrition_logs", {"user_id": user_id})
    day_nutrition = [
        log for log in nutrition_logs
        if datetime.fromisoformat(log['date']).date() == target_date
    ]

    # Get all workout logs for the day
    workout_logs = db.find("workout_logs", {"user_id": user_id})
    day_workouts = [
        log for log in workout_logs
        if datetime.fromisoformat(log['date']).date() == target_date
    ]

    # Get weight for the day
    body_logs = db.find("body_logs", {"user_id": user_id})
    day_body = [
        log for log in body_logs
        if datetime.fromisoformat(log['date']).date() == target_date
    ]

    # Aggregate
    total_calories = sum(log['calories'] for log in day_nutrition)
    total_protein = sum(log['protein'] for log in day_nutrition)
    total_carbs = sum(log['carbs'] for log in day_nutrition)
    total_fats = sum(log['fats'] for log in day_nutrition)
    workouts_completed = len([w for w in day_workouts if w.get('completed', False)])
    weight = day_body[0]['weight'] if day_body else None

    summary = {
        "user_id": user_id,
        "date": target_date.isoformat(),
        "total_calories": total_calories,
        "total_protein": total_protein,
        "total_carbs": total_carbs,
        "total_fats": total_fats,
        "workouts_completed": workouts_completed,
        "weight": weight,
        "created_at": datetime.now().isoformat(),
        "updated_at": datetime.now().isoformat()
    }

    return summary


async def _update_daily_summary(user_id: str, target_date: date):
    """
    Update or create daily summary

    Called after any nutrition/workout log is added
    """
    summary = await _compute_daily_summary(user_id, target_date)

    # Check if summary exists
    existing = db.find_one("daily_summaries", {
        "user_id": user_id,
        "date": target_date.isoformat()
    })

    if existing:
        db.update(
            "daily_summaries",
            {"user_id": user_id, "date": target_date.isoformat()},
            summary
        )
    else:
        summary['id'] = str(uuid.uuid4())
        db.insert("daily_summaries", summary)


# ============================================================================
# ============================================================================
# Training Agent Helper Functions
# ============================================================================

def _calculate_reps_from_intensity(exercise_name: str, intensity: int) -> int:
    """
    Convert intensity (% of 1RM) to rep target using the same matrix as frontend.
    This ensures consistency between what users see in UI and what Training Agent uses.

    Based on frontend's calculateRepsFromIntensity function.
    """
    # Intensity-Rep relationship table (matches frontend exactly)
    rep_table = {
        95: {"bench_press": 3, "leg_press": 7, "other": 3},
        90: {"bench_press": 4, "leg_press": 9, "other": 5},
        85: {"bench_press": 6, "leg_press": 11, "other": 7},
        80: {"bench_press": 9, "leg_press": 13, "other": 10},
        75: {"bench_press": 12, "leg_press": 16, "other": 12},
        70: {"bench_press": 14, "leg_press": 19, "other": 15},
        65: {"bench_press": 17, "leg_press": 23, "other": 17},
        60: {"bench_press": 19, "leg_press": 27, "other": 20},
    }

    # Determine exercise type
    lower_name = exercise_name.lower()
    if "bench press" in lower_name or "bench" in lower_name:
        exercise_type = "bench_press"
    elif "leg press" in lower_name:
        exercise_type = "leg_press"
    else:
        exercise_type = "other"

    # Find closest intensity in table (round to nearest 5%)
    intensity_levels = sorted(rep_table.keys(), reverse=True)
    closest_intensity = intensity_levels[0]
    min_diff = abs(intensity - closest_intensity)

    for level in intensity_levels:
        diff = abs(intensity - level)
        if diff < min_diff:
            min_diff = diff
            closest_intensity = level

    return rep_table[closest_intensity][exercise_type]


def _parse_rep_range(rep_range_str: str) -> int:
    """
    Parse rep range string and return the upper bound as target.
    Examples: "4 - 8" -> 8, "6-8" -> 8, "5" -> 5

    NOTE: This is a fallback for old workout plans without intensity.
    New plans use intensity-to-reps conversion.
    """
    try:
        # Remove spaces and split by dash
        parts = rep_range_str.replace(" ", "").split("-")
        if len(parts) == 2:
            # Return upper bound of range
            return int(parts[1])
        else:
            # Single number
            return int(parts[0])
    except:
        return 5  # Fallback default


def _get_or_create_exercise_config(user_id: str, exercise_name: str) -> dict:
    """Get or create exercise configuration for progression tracking"""
    try:
        # Try to find existing config
        configs = db.find("user_exercises", {
            "user_id": user_id,
            "exercise_name": exercise_name
        })

        if configs:
            return configs[0]

        # Get rep target from user's active workout plan
        rep_target = 5  # Default fallback
        num_sets = 3

        # Find user's active workout plan
        active_plans = db.find("workout_plans", {
            "user_id": user_id,
            "active": True
        })

        if active_plans:
            plan = active_plans[0]
            # Find this exercise in the plan
            for exercise in plan.get('exercises', []):
                if exercise.get('name', '').lower() == exercise_name.lower():
                    # Prefer intensity-based reps (matches frontend logic)
                    if exercise.get('intensity'):
                        rep_target = _calculate_reps_from_intensity(
                            exercise_name,
                            exercise.get('intensity')
                        )
                    else:
                        # Fallback: parse rep range (e.g., "4 - 8" -> 8)
                        rep_range = exercise.get('reps', '5')
                        rep_target = _parse_rep_range(rep_range)

                    num_sets = exercise.get('sets', 3)
                    break

        # Create default config with plan-based rep target
        default_config = {
            "user_id": user_id,
            "exercise_name": exercise_name,
            "progression_model": "linear",  # Default to linear progressive
            "rep_target": rep_target,  # From workout plan
            "num_sets": num_sets,  # From workout plan
            "available_increments": [1.25, 2.5, 5.0],
            "selected_increment": 2.5,  # Default 2.5kg
            "last_successful_weight": 0,
            "current_weight": 0,
            "created_at": datetime.now().isoformat(),
        }

        db.insert("user_exercises", default_config)
        return default_config
    except Exception as e:
        print(f"Error getting/creating exercise config: {e}")
        import traceback
        traceback.print_exc()
        # Return minimal default
        return {
            "progression_model": "linear",
            "rep_target": 5,
            "num_sets": 3,
            "available_increments": [2.5],
            "selected_increment": 2.5,
            "last_successful_weight": 0,
        }


def _get_exercise_session_history(user_id: str, exercise_name: str, limit: int = 8):
    """Get recent session history for an exercise"""
    from ai_agents.shared.models import Session, Set

    try:
        # Find all workout logs for this user
        all_logs = db.find("workout_logs", {"user_id": user_id})

        # Extract sessions for this specific exercise
        sessions = []
        for log in all_logs:
            for exercise in log.get('exercises', []):
                if exercise.get('name') == exercise_name:
                    sets = exercise.get('sets', [])
                    if sets:
                        # Use first set as progression benchmark
                        first_set = sets[0]
                        sessions.append(Session(
                            date=log.get('date', ''),
                            first_set=Set(
                                weight=first_set.get('weight', 0),
                                reps=first_set.get('reps', 0)
                            )
                        ))

        # Sort by date (oldest to newest) and limit
        sessions = sorted(sessions, key=lambda s: s.date)[-limit:]
        return sessions
    except Exception as e:
        print(f"Error getting session history: {e}")
        return []


def _store_training_recommendation(user_id: str, recommendation, workout_date: str):
    """Store training recommendation in database"""
    try:
        rec_dict = {
            "user_id": user_id,
            "exercise_name": recommendation.exercise_name,
            "date": workout_date,
            "progression_model": recommendation.progression_model,
            "today_first_set": {
                "weight": recommendation.today_first_set.weight,
                "reps": recommendation.today_first_set.reps,
            },
            "hit_rep_target": recommendation.hit_rep_target,
            "plateau_detected": recommendation.plateau_detected,
            "regression_detected": recommendation.regression_detected,
            "reactive_deload_implemented": recommendation.reactive_deload_implemented,
            "next_weight": recommendation.next_weight,
            "next_rep_target": recommendation.next_rep_target,
            "action_type": recommendation.action_type,
            "message": recommendation.message,
            "reasoning": recommendation.reasoning,
            "confidence": recommendation.confidence,
            "created_at": datetime.now().isoformat(),
        }

        # Add model switch suggestion if present
        if recommendation.model_switch_suggestion:
            rec_dict["model_switch_suggestion"] = {
                "from_model": recommendation.model_switch_suggestion.from_model,
                "to_model": recommendation.model_switch_suggestion.to_model,
                "reason": recommendation.model_switch_suggestion.reason,
            }

        db.insert("training_recommendations", rec_dict)
    except Exception as e:
        print(f"Error storing training recommendation: {e}")


def _update_exercise_config(user_id: str, exercise_name: str, recommendation, current_weight: float):
    """Update exercise configuration after session"""
    try:
        update_data = {
            "current_weight": current_weight,
            "last_updated": datetime.now().isoformat(),
        }

        # Update last successful weight if rep target was hit
        if recommendation.hit_rep_target:
            update_data["last_successful_weight"] = current_weight

        # Update in database
        db.update(
            "user_exercises",
            {"user_id": user_id, "exercise_name": exercise_name},
            update_data
        )
    except Exception as e:
        print(f"Error updating exercise config: {e}")


def _check_and_update_training_status(user_id: str, exercise_name: str, sets_logged: list):
    """
    Check if user's performance indicates training status upgrade.
    If so, update user profile and workout plan intensities.

    This implements automatic progression from Novice → Intermediate → Advanced → Elite
    based on ExRx.net strength standards.
    """
    try:
        # Get user profile
        user_profile = db.find_one("user_profiles", {"user_id": user_id})
        if not user_profile:
            return

        bodyweight = user_profile.get("weight", 75)  # Default to 75kg if not set
        sex = user_profile.get("sex", "male")
        current_status = user_profile.get("training_status", "Novice")

        # Key exercises that determine training status
        key_exercises = {
            "Bench Press": ["bench press", "barbell bench press"],
            "Press": ["overhead press", "press", "barbell overhead press", "dumbbell overhead press"],
            "Deadlift": ["deadlift", "powerlifting deadlift", "romanian deadlift"],
            "Squat": ["squat", "barbell squat", "back squat"]
        }

        # Check if this exercise is a key exercise
        exercise_name_lower = exercise_name.lower()
        standard_name = None
        for name, variations in key_exercises.items():
            if any(variation in exercise_name_lower for variation in variations):
                standard_name = name
                break

        if not standard_name:
            # Not a key exercise, skip status check
            return

        # Find heaviest set and calculate 1RM
        best_1rm = 0
        for s in sets_logged:
            weight = s.weight if hasattr(s, 'weight') else s.get('weight', 0)
            reps = s.reps if hasattr(s, 'reps') else s.get('reps', 0)

            if weight > 0 and reps > 0:
                estimated_1rm = calculate_1rm(weight, reps)
                if estimated_1rm > best_1rm:
                    best_1rm = estimated_1rm

        if best_1rm == 0:
            return

        # Determine status for this exercise
        exercise_status = determine_training_status(
            standard_name, best_1rm, bodyweight, sex
        )

        print(f"Training Status Check: {exercise_name} -> 1RM: {best_1rm:.1f}kg -> Status: {exercise_status}")

        # Get all workout logs to calculate overall status
        workout_logs = db.find("workout_logs", {"user_id": user_id})

        # Calculate best 1RM for all key exercises
        all_exercise_statuses = []
        for key_name, variations in key_exercises.items():
            best_1rm_for_exercise = 0

            for log in workout_logs:
                for exercise in log.get('exercises', []):
                    ex_name_lower = exercise['name'].lower()

                    # Special handling to avoid matching "bench press" as "press"
                    # Skip if this is a bench press exercise but we're checking for overhead press
                    if key_name == "Press" and "bench" in ex_name_lower:
                        continue

                    if any(variation in ex_name_lower for variation in variations):
                        for set_data in exercise['sets']:
                            weight = set_data.get('weight', 0)
                            reps = set_data.get('reps', 0)

                            if weight > 0 and reps > 0:
                                estimated_1rm = calculate_1rm(weight, reps)
                                if estimated_1rm > best_1rm_for_exercise:
                                    best_1rm_for_exercise = estimated_1rm

            # Add status for this exercise if user has performed it
            if best_1rm_for_exercise > 0:
                status = determine_training_status(
                    key_name, best_1rm_for_exercise, bodyweight, sex
                )
                all_exercise_statuses.append(status)

        # Calculate overall status (median of all exercises)
        if all_exercise_statuses:
            new_overall_status = calculate_overall_status(all_exercise_statuses)
        else:
            new_overall_status = "Novice"

        # Check if status has changed (ONLY UPGRADE, never downgrade)
        status_order = ["Untrained", "Novice", "Intermediate", "Advanced", "Elite"]
        current_idx = status_order.index(current_status) if current_status in status_order else 0
        new_idx = status_order.index(new_overall_status) if new_overall_status in status_order else 0

        if new_idx > current_idx:
            # Only proceed if this is an upgrade
            print(f"🎉 Training Status Upgrade Detected: {current_status} → {new_overall_status}")

            # Update user profile
            db.update(
                "user_profiles",
                {"user_id": user_id},
                {"training_status": new_overall_status}
            )

            # Update workout plan intensities
            intensity_map = {
                "Untrained": {"compound": 60, "isolation": 60},
                "Novice": {"compound": 60, "isolation": 60},
                "Intermediate": {"compound": 80, "isolation": 65},
                "Advanced": {"compound": 85, "isolation": 70},
                "Elite": {"compound": 85, "isolation": 70}
            }

            new_intensities = intensity_map.get(new_overall_status, {"compound": 60, "isolation": 60})

            # Find active workout plans
            active_plans = db.find("workout_plans", {"user_id": user_id, "active": True})

            for plan in active_plans:
                # Update intensity for each exercise in the plan
                updated_exercises = []
                for exercise in plan.get('exercises', []):
                    # Determine if compound or isolation
                    # Compound: Bench Press, Squat, Deadlift, Overhead Press, Rows, Pull-ups
                    # Isolation: Everything else
                    exercise_name_lower = exercise.get('name', '').lower()
                    is_compound = any(compound in exercise_name_lower for compound in [
                        'bench press', 'squat', 'deadlift', 'overhead press',
                        'press', 'row', 'pull-up', 'pull up', 'chin-up', 'chin up'
                    ])

                    new_intensity = new_intensities['compound'] if is_compound else new_intensities['isolation']

                    # Update intensity and recalculate reps
                    exercise['intensity'] = new_intensity
                    exercise['reps'] = _calculate_reps_from_intensity(exercise.get('name', ''), new_intensity)

                    updated_exercises.append(exercise)

                # Update the plan in database
                db.update(
                    "workout_plans",
                    {"user_id": user_id, "plan_name": plan.get('plan_name')},
                    {"exercises": updated_exercises}
                )

            # Update user_exercises table with new rep targets
            # This ensures training agent uses correct targets for new intensity level
            all_user_exercises = db.find("user_exercises", {"user_id": user_id})
            for user_ex in all_user_exercises:
                ex_name = user_ex.get('exercise_name')
                # Find matching exercise in updated plan
                for plan_ex in updated_exercises:
                    if plan_ex.get('name', '').lower() == ex_name.lower():
                        new_rep_target = plan_ex.get('reps')
                        if isinstance(new_rep_target, int):
                            # Update rep target in user_exercises
                            db.update(
                                "user_exercises",
                                {"user_id": user_id, "exercise_name": ex_name},
                                {"rep_target": new_rep_target}
                            )
                            print(f"  ↳ Updated {ex_name}: rep_target → {new_rep_target}")
                        break

            print(f"✅ Updated workout plan intensities: Compound={new_intensities['compound']}%, Isolation={new_intensities['isolation']}%")
        else:
            print(f"⏸️  Training status change detected ({current_status} → {new_overall_status}) but not upgrading (only upgrades are automatic)")

    except Exception as e:
        print(f"Error checking training status: {e}")
        import traceback
        traceback.print_exc()


# ============================================================================
# Nutrition Agent Endpoint
# ============================================================================

@app.post("/api/nutrition/analyze")
async def analyze_nutrition(request: Dict):
    """
    Analyze nutrition and provide recommendations using Nutrition Specialist Agent.

    Analyzes last 14 days of data (weight, body composition, nutrition, workouts)
    and returns personalized nutrition recommendations.

    Request body:
    {
        "user_id": "test_user_90day"
    }

    Returns:
    {
        "recommendation": {
            "current_calorie_average": 2200,
            "recommended_calories": 2000,
            "adjustment_category": "decrease",
            "reasoning": "...",
            ...
        }
    }
    """
    # Import nutrition agent (lazy import to avoid circular dependencies)
    import sys
    from pathlib import Path
    sys.path.insert(0, str(Path(__file__).parent.parent))

    from ai_agents.nutrition_specialist import (
        apply_nutrition_algorithm,
        analyze_weight_trend,
        analyze_body_composition_trend
    )
    from ai_agents.shared.models import NutritionSummary, TrainingProgressSummary
    from ai_agents.training_specialist.tools import get_iso_week

    user_id = request.get("user_id")
    if not user_id:
        raise HTTPException(status_code=400, detail="user_id is required")

    # 1. Fetch user profile
    user_profile = db.find_one("user_profiles", {"user_id": user_id})
    if not user_profile:
        raise HTTPException(status_code=404, detail=f"User {user_id} not found")

    # 2. Fetch last 14 days of data
    from datetime import datetime, timedelta
    end_date = datetime.now()
    start_date = end_date - timedelta(days=13)  # 14 days total

    # Get all body logs for weight trend
    all_body_logs = db.find("body_logs", {"user_id": user_id})
    body_logs_14d = [
        log for log in all_body_logs
        if datetime.fromisoformat(log['date']) >= start_date
    ]

    # Get daily summaries (contains aggregated daily nutrition + workout data)
    all_daily_summaries = db.find("daily_summaries", {"user_id": user_id})
    daily_summaries_14d = [
        log for log in all_daily_summaries
        if datetime.fromisoformat(log['date']) >= start_date
    ]

    # 3. Analyze weight trend
    weight_logs_for_analysis = [
        {"date": log['date'], "weight": log['weight']}
        for log in body_logs_14d
        if log.get('weight')
    ]
    weight_trend = analyze_weight_trend(weight_logs_for_analysis, days=14)

    # 4. Analyze body composition trend
    body_comp_logs_for_analysis = [
        {
            "date": log['date'],
            "skinfold_sum": log.get('skinfold_sum'),
            "skinfolds": log.get('skinfolds'),
            "waist_cm": log.get('waist_cm'),
            "body_fat_pct": log.get('body_fat_pct')
        }
        for log in body_logs_14d
    ]
    body_comp_trend = analyze_body_composition_trend(body_comp_logs_for_analysis, days=14)

    # 5. Summarize nutrition (from daily summaries)
    nutrition_logged_days = [
        summary for summary in daily_summaries_14d
        if summary.get('total_calories', 0) > 0
    ]

    if nutrition_logged_days:
        avg_calories = sum(log.get('total_calories', 0) for log in nutrition_logged_days) / len(nutrition_logged_days)
        avg_protein = sum(log.get('total_protein', 0) for log in nutrition_logged_days) / len(nutrition_logged_days)
    else:
        avg_calories = user_profile.get('target_calories', 2000)
        avg_protein = user_profile.get('target_protein', 160)

    nutrition_summary = NutritionSummary(
        days_analyzed=14,
        days_logged=len(nutrition_logged_days),
        avg_calories=avg_calories,
        avg_protein_g=avg_protein,
        compliance_pct=(len(nutrition_logged_days) / 14) * 100,
        sufficient_data=len(nutrition_logged_days) >= 10
    )

    # 6. Fetch latest training progress summary from Training Agent
    # Training Agent publishes weekly summaries to training_progress_summaries table
    user_training_summaries = db.find('training_progress_summaries', {"user_id": user_id})

    # Get the most recent summary
    if user_training_summaries:
        # Sort by published_at descending
        user_training_summaries.sort(
            key=lambda x: x.get('published_at', ''),
            reverse=True
        )
        latest_summary_dict = user_training_summaries[0]

        # Convert to TrainingProgressSummary model
        training_summary = TrainingProgressSummary(**latest_summary_dict)
    else:
        # No training summary available - create placeholder with "insufficient_data"
        current_week = get_iso_week()
        workout_days = [
            summary for summary in daily_summaries_14d
            if summary.get('workouts_completed', 0) > 0
        ]
        training_summary = TrainingProgressSummary(
            user_id=user_id,
            week=current_week,
            published_by="nutrition_agent_fallback",
            published_at=datetime.utcnow().isoformat(),
            overall_strength_trend="insufficient_data",
            exercises_analyzed=0,
            exercises_progressing=0,
            exercises_plateaued=0,
            exercises_regressing=0,
            avg_weekly_volume_kg=0.0,
            trend_confidence=0.0,
            days_of_data=14,
            workouts_completed=len(workout_days),
            data_quality="poor"
        )

    # 7. Run nutrition algorithm
    recommendation = apply_nutrition_algorithm(
        user_profile,
        weight_trend,
        body_comp_trend,
        nutrition_summary,
        training_summary
    )

    # 8. Return recommendation
    return {
        "user_id": user_id,
        "analysis_date": datetime.now().isoformat(),
        "data_quality": {
            "weight_logs": len(weight_logs_for_analysis),
            "body_comp_logs": len([l for l in body_comp_logs_for_analysis if l.get('skinfold_sum')]),
            "nutrition_days": len(nutrition_logged_days),
            "training_summary_available": training_summary.overall_strength_trend != "insufficient_data"
        },
        "trends": {
            "weight": {
                "current": weight_trend.current_weight,
                "avg": weight_trend.avg_weight,
                "weekly_rate_pct": weight_trend.weekly_rate_pct,
                "is_plateau": weight_trend.is_plateau,
                "trend": weight_trend.trend
            },
            "body_composition": {
                "method": body_comp_trend.method,
                "confidence": body_comp_trend.confidence,
                "trend": body_comp_trend.trend,
                "interpretation": body_comp_trend.interpretation
            },
            "training": {
                "overall_strength_trend": training_summary.overall_strength_trend,
                "exercises_analyzed": training_summary.exercises_analyzed,
                "exercises_progressing": training_summary.exercises_progressing,
                "exercises_plateaued": training_summary.exercises_plateaued,
                "exercises_regressing": training_summary.exercises_regressing,
                "data_quality": training_summary.data_quality,
                "trend_confidence": training_summary.trend_confidence
            }
        },
        "recommendation": {
            "current_calorie_average": recommendation.current_calorie_average,
            "recommended_calories": recommendation.recommended_calories,
            "recommended_macros": {
                "protein_g": recommendation.recommended_macros.protein_g,
                "carbs_g": recommendation.recommended_macros.carbs_g,
                "fat_g": recommendation.recommended_macros.fat_g
            },
            "adjustment_category": recommendation.adjustment_category,
            "reasoning": recommendation.reasoning,
            "body_composition_status": recommendation.body_composition_status,
            "confidence": recommendation.confidence
        }
    }


# ============================================================================
# Training Agent Endpoints
# ============================================================================

@app.get("/api/training/recommendations")
async def get_training_recommendations(user_id: str, exercise_name: Optional[str] = None):
    """
    Get next session recommendations from Training Specialist Agent.

    Returns the most recent recommendations for user's exercises.

    Query params:
        - user_id: User identifier (required)
        - exercise_name: Optional - filter by specific exercise

    Returns:
        List of recommendations with next session prescriptions
    """
    try:
        query = {"user_id": user_id}
        if exercise_name:
            query["exercise_name"] = exercise_name

        # Get all recommendations
        recommendations = db.find("training_recommendations", query)

        if not recommendations:
            return {"user_id": user_id, "recommendations": []}

        # Group by exercise and get most recent for each
        from collections import defaultdict
        by_exercise = defaultdict(list)

        for rec in recommendations:
            exercise = rec.get('exercise_name')
            by_exercise[exercise].append(rec)

        # Get most recent for each exercise
        latest_recommendations = []
        for exercise, recs in by_exercise.items():
            # Sort by created_at and get most recent
            latest = sorted(
                recs,
                key=lambda r: r.get('created_at', ''),
                reverse=True
            )[0]
            latest_recommendations.append(latest)

        return {
            "user_id": user_id,
            "recommendations": latest_recommendations
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/training/exercise-config")
async def get_exercise_config(user_id: str, exercise_name: str):
    """
    Get exercise configuration (progression model, rep target, etc.)

    Query params:
        - user_id: User identifier
        - exercise_name: Exercise name

    Returns:
        Exercise configuration or 404 if not found
    """
    try:
        configs = db.find("user_exercises", {
            "user_id": user_id,
            "exercise_name": exercise_name
        })

        if not configs:
            raise HTTPException(
                status_code=404,
                detail=f"No configuration found for {exercise_name}"
            )

        return configs[0]
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/training/weekly-summary")
async def generate_weekly_training_summary(request: Dict):
    """
    Generate weekly strength trend summary using Training Specialist Agent (weekly mode).

    Analyzes last 14 days of training data and publishes strength trend summary.
    This summary is consumed by Nutrition Agent for bulk assessment.

    Request body:
    {
        "user_id": "test_user_90day"
    }

    Returns:
    {
        "summary": {
            "user_id": "test_user_90day",
            "week": "2025-W47",
            "overall_strength_trend": "improving",
            "exercises_analyzed": 5,
            "exercises_progressing": 4,
            ...
        }
    }
    """
    # Import training agent (lazy import to avoid circular dependencies)
    import sys
    from pathlib import Path
    sys.path.insert(0, str(Path(__file__).parent.parent))

    from ai_agents.training_specialist.weekly_summary import publish_weekly_strength_summary
    from datetime import datetime, timedelta

    user_id = request.get("user_id")
    if not user_id:
        raise HTTPException(status_code=400, detail="user_id is required")

    # 1. Fetch user profile (to verify user exists)
    user_profile = db.find_one("user_profiles", {"user_id": user_id})
    if not user_profile:
        raise HTTPException(status_code=404, detail=f"User {user_id} not found")

    # 2. Fetch user exercises
    user_exercises = db.find("user_exercises", {"user_id": user_id})
    if not user_exercises:
        return {
            "summary": {
                "user_id": user_id,
                "overall_strength_trend": "insufficient_data",
                "message": "No exercises configured. Add exercises to start tracking strength progress."
            }
        }

    # 3. Fetch recent training recommendations (last 14 days)
    end_date = datetime.now()
    start_date = end_date - timedelta(days=13)  # 14 days total

    all_recommendations = db.find("training_recommendations", {"user_id": user_id})
    recent_recommendations = [
        rec for rec in all_recommendations
        if datetime.fromisoformat(rec.get('analyzed_at', rec.get('created_at', ''))) >= start_date
    ]

    # 4. Fetch recent workout logs (for volume calculation)
    all_workouts = db.find("workout_logs", {"user_id": user_id})
    recent_workouts = [
        workout for workout in all_workouts
        if datetime.fromisoformat(workout.get('timestamp', workout.get('date', ''))) >= start_date
    ]

    # 5. Generate weekly strength summary
    summary = publish_weekly_strength_summary(
        user_id=user_id,
        user_exercises=user_exercises,
        recent_recommendations=recent_recommendations,
        recent_workouts=recent_workouts,
        days=14,
    )

    # 6. Save to database (training_progress_summaries table)
    summary_dict = summary.model_dump()
    db.insert("training_progress_summaries", summary_dict)

    return {
        "summary": summary_dict,
        "message": f"Weekly strength summary generated: {summary.overall_strength_trend}"
    }


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)
