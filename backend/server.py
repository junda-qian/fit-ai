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
origins = os.getenv("CORS_ORIGINS", "http://localhost:3000").split(",")
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=False,
    allow_methods=["GET", "POST", "OPTIONS"],
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
    4. Update daily summary

    Example:
    "Upper Body A - Bench Press 3x8 @ 185lbs, Rows 3x10 @ 135lbs..."
    """
    try:
        log_obj = WorkoutLog(**log.dict())
        log_dict = log_obj.dict()
        log_dict = json.loads(json.dumps(log_dict, default=str))
        db.insert("workout_logs", log_dict)

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


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)
