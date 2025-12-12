"""
Function tools for Coach Orchestrator Agent

These tools allow the coach to:
1. Access user personal data (nutrition, workouts, body composition)
2. Search evidence-based knowledge (RAG)
3. Call specialist agents (Nutrition, Training)

Tools will be implemented in phases:
- Phase 1: Basic structure (this file)
- Phase 2: RAG integration (search_knowledge_base)
- Phase 3: Personal data tools
- Phase 4: Specialist agent tools
"""

import json
from typing import Dict, List, Any, Optional


# ============================================================================
# Tool Definitions for OpenAI Function Calling
# ============================================================================

def get_available_tools() -> List[Dict[str, Any]]:
    """
    Return list of function tool definitions for OpenAI SDK.

    This defines what functions the AI can call and their parameters.
    """
    tools = [
        # Phase 2: RAG Knowledge Base
        {
            "type": "function",
            "function": {
                "name": "search_knowledge_base",
                "description": """Search evidence-based fitness and health knowledge base using RAG.

                Use this when users ask GENERAL fitness/health questions (not about their personal data):
                - "What is..." or "How does..." questions
                - Training principles, nutrition science, sleep optimization
                - Exercise techniques, programming methods
                - Debunking myths or explaining scientific concepts

                Examples:
                - "What's the optimal training volume for muscle growth?"
                - "How should I structure my macronutrients?"
                - "What are evidence-based sleep optimization strategies?"
                - "Is intermittent fasting effective?"
                """,
                "parameters": {
                    "type": "object",
                    "properties": {
                        "query": {
                            "type": "string",
                            "description": "The user's question or search query"
                        },
                        "top_k": {
                            "type": "integer",
                            "description": "Number of relevant documents to retrieve (default 5)",
                            "default": 5
                        }
                    },
                    "required": ["query"]
                }
            }
        },

        # Phase 3: Personal Data Tools
        {
            "type": "function",
            "function": {
                "name": "get_user_profile",
                "description": """Get user's profile including goals, targets, and body stats.

                Use this when users ask about:
                - Their fitness goals or targets
                - Their body measurements or stats
                - General information about their profile

                Examples:
                - "What are my fitness goals?"
                - "What's my target weight?"
                - "What are my macro targets?"
                """,
                "parameters": {
                    "type": "object",
                    "properties": {},
                    "required": []
                }
            }
        },
        {
            "type": "function",
            "function": {
                "name": "get_nutrition_logs",
                "description": """Get user's recent nutrition logs and eating patterns.

                Use this when users ask about:
                - Their calorie or macro intake
                - What they've been eating
                - Nutrition tracking progress

                Examples:
                - "What's my average calorie intake this week?"
                - "How much protein am I eating?"
                - "Am I hitting my nutrition targets?"
                """,
                "parameters": {
                    "type": "object",
                    "properties": {
                        "days": {
                            "type": "integer",
                            "description": "Number of days to retrieve (default 7)",
                            "default": 7
                        }
                    },
                    "required": []
                }
            }
        },
        {
            "type": "function",
            "function": {
                "name": "get_workout_logs",
                "description": """Get user's recent workout logs and training history.

                Use this when users ask about:
                - Their recent workouts or exercises
                - Training frequency or volume
                - Progress on specific exercises

                Examples:
                - "What workouts have I done this week?"
                - "How often am I training?"
                - "How's my squat progression?"
                """,
                "parameters": {
                    "type": "object",
                    "properties": {
                        "days": {
                            "type": "integer",
                            "description": "Number of days to retrieve (default 14)",
                            "default": 14
                        },
                        "exercise": {
                            "type": "string",
                            "description": "Optional: filter by specific exercise name"
                        }
                    },
                    "required": []
                }
            }
        },
        {
            "type": "function",
            "function": {
                "name": "get_body_logs",
                "description": """Get user's body composition logs and weight tracking.

                Use this when users ask about:
                - Their weight or body composition
                - Weight changes or trends
                - Progress measurements

                Examples:
                - "How has my weight changed?"
                - "What's my current weight?"
                - "Am I losing/gaining weight?"
                """,
                "parameters": {
                    "type": "object",
                    "properties": {
                        "days": {
                            "type": "integer",
                            "description": "Number of days to retrieve (default 14)",
                            "default": 14
                        }
                    },
                    "required": []
                }
            }
        },

        # Phase 4: Specialist Agent Tools
        {
            "type": "function",
            "function": {
                "name": "get_nutrition_recommendation",
                "description": """Get personalized nutrition recommendation from the Nutrition Specialist Agent.

                Use this when users ask for:
                - Nutrition advice or recommendations
                - Should they adjust calories or macros
                - If their current diet is appropriate for their goals
                - Calorie or macro targets
                - WHY a recommendation was made or the REASONING/RATIONALE behind it
                - EXPLANATION of the algorithm or analysis behind nutrition recommendations
                - Details about how recommendations are calculated

                This runs a DETERMINISTIC ALGORITHM that analyzes their last 14 days of data
                (weight trends, body composition, nutrition logs, training progress) and returns:
                - Recommended calories and macros
                - Detailed ALGORITHMIC REASONING explaining the calculations
                - Specific metrics (e.g., "weight gain 0.1%/week vs target 0.5%/week")
                - The exact logic behind the recommendation (e.g., "increase to 10% surplus")

                Examples:
                - "Should I adjust my calories?"
                - "What should my macros be?"
                - "Am I eating enough for muscle gain?"
                - "How should I adjust my diet based on my progress?"
                - "Why is the recommended intake 2043 calories?"
                - "Can you explain the rationale for the nutrition recommendation?"
                - "How was the calorie recommendation calculated?"
                """,
                "parameters": {
                    "type": "object",
                    "properties": {},
                    "required": []
                }
            }
        },
        {
            "type": "function",
            "function": {
                "name": "get_training_summary",
                "description": """Get training progress summary from the Training Specialist Agent.

                Use this when users ask about:
                - Their training progress or strength gains
                - How their lifts are progressing
                - Which exercises are improving or plateauing
                - Overall training trends
                - Training volume or workout statistics

                This runs a DETERMINISTIC ALGORITHM that analyzes their workout data and returns:
                - Overall strength trend (improving/plateaued/regressing)
                - Exercise-by-exercise breakdown (progressing/plateaued/regressing counts)
                - Weekly training volume (total kg lifted)
                - Data quality and confidence metrics
                - Specific analysis of each exercise's progression

                Examples:
                - "How is my training going?"
                - "Am I getting stronger?"
                - "Which exercises are plateauing?"
                - "What's my overall training progress?"
                - "What's my weekly training volume?"
                - "How many exercises are progressing?"
                """,
                "parameters": {
                    "type": "object",
                    "properties": {},
                    "required": []
                }
            }
        },
    ]

    return tools


# ============================================================================
# Tool Execution
# ============================================================================

def execute_tool(tool_name: str, arguments: Dict[str, Any], user_id: str) -> Dict[str, Any]:
    """
    Execute a function tool and return results.

    Args:
        tool_name: Name of the tool to execute
        arguments: Arguments passed from OpenAI
        user_id: Current user ID (injected by agent)

    Returns:
        Tool execution results as dict
    """
    # Inject user_id into arguments if needed
    if 'user_id' in get_tool_signature(tool_name) and 'user_id' not in arguments:
        arguments['user_id'] = user_id

    # Route to appropriate tool function
    if tool_name == "search_knowledge_base":
        return search_knowledge_base(**arguments)

    # Phase 3: Personal data tools
    elif tool_name == "get_user_profile":
        return get_user_profile(**arguments)
    elif tool_name == "get_nutrition_logs":
        return get_nutrition_logs(**arguments)
    elif tool_name == "get_workout_logs":
        return get_workout_logs(**arguments)
    elif tool_name == "get_body_logs":
        return get_body_logs(**arguments)

    # Phase 4: Specialist agent tools
    elif tool_name == "get_nutrition_recommendation":
        return get_nutrition_recommendation(**arguments)
    elif tool_name == "get_training_summary":
        return get_training_summary(**arguments)

    else:
        return {
            "error": f"Unknown tool: {tool_name}",
            "available_tools": [t["function"]["name"] for t in get_available_tools()]
        }


def get_tool_signature(tool_name: str) -> List[str]:
    """Get parameter names for a tool (for user_id injection)"""
    tool_params = {
        "search_knowledge_base": ["query", "top_k"],
        "get_user_profile": ["user_id"],
        "get_nutrition_logs": ["user_id", "days"],
        "get_workout_logs": ["user_id", "days", "exercise"],
        "get_body_logs": ["user_id", "days"],
        "get_nutrition_recommendation": ["user_id"],
        "get_training_summary": ["user_id"],
    }
    return tool_params.get(tool_name, [])


# ============================================================================
# Phase 2: Knowledge Base Tools (RAG)
# ============================================================================

def search_knowledge_base(query: str, top_k: int = 5) -> Dict[str, Any]:
    """
    Search evidence-based fitness/health knowledge using RAG.

    Uses the existing HealthRAG system to search fitness/nutrition documents.

    Args:
        query: User's question
        top_k: Number of documents to retrieve

    Returns:
        {
            "context": str,  # Formatted context from documents
            "sources": List[Dict],  # Source metadata
            "summary": str  # Summary for the AI
        }
    """
    try:
        # Import HealthRAG from backend
        import sys
        import os
        backend_path = os.path.join(
            os.path.dirname(os.path.dirname(os.path.dirname(__file__))),
            "backend"
        )
        sys.path.insert(0, backend_path)

        from retrieval import HealthRAG

        # Initialize RAG system
        # Use OpenSearch in production, FAISS locally
        use_opensearch = os.getenv("USE_OPENSEARCH", "false").lower() == "true"
        rag = HealthRAG(use_opensearch=use_opensearch)

        # Retrieve relevant documents
        context, sources = rag.retrieve_context(query, top_k=top_k)

        if not context:
            return {
                "context": "",
                "sources": [],
                "summary": "No relevant information found in the knowledge base for this query.",
                "query": query
            }

        # Format summary for the AI
        summary = f"Found {len(sources)} relevant sources about: {query}\n\n{context}"

        return {
            "context": context,
            "sources": sources,
            "summary": summary,
            "query": query,
            "num_sources": len(sources)
        }

    except Exception as e:
        return {
            "error": str(e),
            "message": f"Failed to search knowledge base: {str(e)}",
            "query": query,
            "sources": []
        }


# ============================================================================
# Phase 3: Personal Data Tools
# ============================================================================

def _get_database():
    """Get database instance"""
    import sys
    import os
    # Get project root directory (3 levels up from this file)
    project_root = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
    backend_path = os.path.join(project_root, "backend")
    data_path = os.path.join(project_root, "data", "tracking")

    sys.path.insert(0, backend_path)
    from database import JSONDatabase
    return JSONDatabase(data_dir=data_path)


def get_user_profile(user_id: str) -> Dict[str, Any]:
    """Get user profile with goals and targets"""
    try:
        db = _get_database()
        profile = db.find_one("user_profiles", {"user_id": user_id})
        if not profile:
            return {"error": "User profile not found", "user_id": user_id}
        return profile
    except Exception as e:
        return {"error": str(e)}


def get_nutrition_logs(user_id: str, days: int = 7) -> Dict[str, Any]:
    """Get recent nutrition logs"""
    try:
        from datetime import datetime, date, timedelta
        db = _get_database()

        end_date = date.today()
        start_date = end_date - timedelta(days=days)
        all_logs = db.find("nutrition_logs", {"user_id": user_id})

        filtered_logs = [
            log for log in all_logs
            if start_date <= datetime.fromisoformat(log['date']).date() <= end_date
        ]
        filtered_logs.sort(key=lambda x: x.get('date', ''), reverse=True)

        # Group by date and calculate daily totals (meals are logged individually)
        from collections import defaultdict
        daily_totals = defaultdict(lambda: {"calories": 0, "protein_g": 0})
        for log in filtered_logs:
            log_date = log['date']
            daily_totals[log_date]["calories"] += log.get("calories", 0)
            daily_totals[log_date]["protein_g"] += log.get("protein_g", 0)

        # Calculate averages from daily totals (not individual meals)
        if daily_totals:
            avg_calories = round(sum(day["calories"] for day in daily_totals.values()) / len(daily_totals), 1)
            avg_protein = round(sum(day["protein_g"] for day in daily_totals.values()) / len(daily_totals), 1)
            days_logged = len(daily_totals)
        else:
            avg_calories = avg_protein = 0
            days_logged = 0

        return {
            "logs": filtered_logs[:10],
            "summary": {
                "days_logged": days_logged,
                "avg_calories": avg_calories,
                "avg_protein": avg_protein
            }
        }
    except Exception as e:
        return {"error": str(e)}


def get_workout_logs(user_id: str, days: int = 14, exercise: Optional[str] = None) -> Dict[str, Any]:
    """Get recent workout logs"""
    try:
        from datetime import datetime, date, timedelta
        db = _get_database()

        end_date = date.today()
        start_date = end_date - timedelta(days=days)
        all_logs = db.find("workout_logs", {"user_id": user_id})

        filtered_logs = [
            log for log in all_logs
            if start_date <= datetime.fromisoformat(log.get('date', log.get('timestamp', ''))).date() <= end_date
        ]

        if exercise:
            exercise_filtered = []
            for workout in filtered_logs:
                matching = [ex for ex in workout.get("exercises", []) if exercise.lower() in ex.get("name", "").lower()]
                if matching:
                    exercise_filtered.append({**workout, "exercises": matching})
            filtered_logs = exercise_filtered

        filtered_logs.sort(key=lambda x: x.get('date', ''), reverse=True)

        all_exercises = set()
        for workout in filtered_logs:
            for ex in workout.get("exercises", []):
                all_exercises.add(ex.get("name"))

        return {
            "logs": filtered_logs[:10],
            "summary": {
                "total_workouts": len(filtered_logs),
                "exercises_performed": sorted(list(all_exercises))
            }
        }
    except Exception as e:
        return {"error": str(e)}


def get_body_logs(user_id: str, days: int = 14) -> Dict[str, Any]:
    """Get body composition logs"""
    try:
        from datetime import datetime, date, timedelta
        db = _get_database()

        end_date = date.today()
        start_date = end_date - timedelta(days=days)
        all_logs = db.find("body_logs", {"user_id": user_id})

        filtered_logs = [
            log for log in all_logs
            if start_date <= datetime.fromisoformat(log['date']).date() <= end_date
        ]
        filtered_logs.sort(key=lambda x: x.get('date', ''), reverse=True)

        weights = [log.get("weight_kg", 0) for log in filtered_logs if log.get("weight_kg")]
        if weights:
            latest_weight = weights[0]
            weight_change = weights[0] - weights[-1]
            avg_weight = sum(weights) / len(weights)
        else:
            latest_weight = weight_change = avg_weight = 0

        return {
            "logs": filtered_logs,
            "summary": {
                "days_logged": len(filtered_logs),
                "latest_weight": round(latest_weight, 1),
                "weight_change": round(weight_change, 2),
                "avg_weight": round(avg_weight, 1)
            }
        }
    except Exception as e:
        return {"error": str(e)}


# ============================================================================
# Phase 4: Specialist Agent Tools
# ============================================================================

def get_nutrition_recommendation(user_id: str) -> Dict[str, Any]:
    """
    Get personalized nutrition recommendation from Nutrition Specialist Agent.

    Analyzes last 14 days of data (weight, body composition, nutrition, training)
    and provides calorie/macro recommendations.

    Args:
        user_id: User ID

    Returns:
        Nutrition recommendation with calories, macros, and reasoning
    """
    try:
        import sys
        import os
        from datetime import datetime, timedelta

        # Add paths for imports
        backend_path = os.path.join(
            os.path.dirname(os.path.dirname(os.path.dirname(__file__))),
            "backend"
        )
        sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
        sys.path.insert(0, backend_path)

        from ai_agents.nutrition_specialist import (
            apply_nutrition_algorithm,
            analyze_weight_trend,
            analyze_body_composition_trend
        )
        from ai_agents.shared.models import NutritionSummary, TrainingProgressSummary
        from ai_agents.training_specialist.tools import get_iso_week
        from database import JSONDatabase

        # Use absolute path to project root data directory
        project_root = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
        data_path = os.path.join(project_root, "data", "tracking")
        db = JSONDatabase(data_dir=data_path)

        # 1. Fetch user profile
        user_profile = db.find_one("user_profiles", {"user_id": user_id})
        if not user_profile:
            return {"error": f"User profile not found for {user_id}"}

        # 2. Fetch last 14 days of data
        end_date = datetime.now()
        start_date = end_date - timedelta(days=13)  # 14 days total

        # Get body logs for weight trend
        all_body_logs = db.find("body_logs", {"user_id": user_id})
        body_logs_14d = [
            log for log in all_body_logs
            if datetime.fromisoformat(log['date']) >= start_date
        ]

        # Get daily summaries
        all_daily_summaries = db.find("daily_summaries", {"user_id": user_id})
        daily_summaries_14d = [
            log for log in all_daily_summaries
            if datetime.fromisoformat(log['date']) >= start_date
        ]

        # 3. Analyze weight trend
        weight_logs = [
            {"date": log['date'], "weight": log.get('weight')}
            for log in body_logs_14d
            if log.get('weight')
        ]
        weight_trend = analyze_weight_trend(weight_logs, days=14)

        # 4. Analyze body composition trend
        body_comp_logs = [
            {
                "date": log['date'],
                "skinfold_sum": log.get('skinfold_sum'),
                "skinfolds": log.get('skinfolds'),
                "waist_cm": log.get('waist_cm'),
                "body_fat_pct": log.get('body_fat_pct')
            }
            for log in body_logs_14d
        ]
        body_comp_trend = analyze_body_composition_trend(body_comp_logs, days=14)

        # 5. Summarize nutrition
        nutrition_logged_days = [
            s for s in daily_summaries_14d
            if s.get('total_calories', 0) > 0
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

        # 6. Get training progress summary
        user_training_summaries = db.find('training_progress_summaries', {"user_id": user_id})

        if user_training_summaries:
            user_training_summaries.sort(
                key=lambda x: x.get('published_at', ''),
                reverse=True
            )
            training_summary = TrainingProgressSummary(**user_training_summaries[0])
        else:
            # No training summary - create placeholder
            current_week = get_iso_week()
            workout_days = [
                s for s in daily_summaries_14d
                if s.get('workouts_completed', 0) > 0
            ]
            training_summary = TrainingProgressSummary(
                user_id=user_id,
                week=current_week,
                published_by="coach_orchestrator_fallback",
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

        # 8. Format response
        return {
            "recommended_calories": recommendation.recommended_calories,
            "recommended_macros": {
                "protein_g": recommendation.recommended_macros.protein_g,
                "carbs_g": recommendation.recommended_macros.carbs_g,
                "fat_g": recommendation.recommended_macros.fat_g
            },
            "current_avg_calories": int(nutrition_summary.avg_calories),
            "adjustment_category": recommendation.adjustment_category,
            "reasoning": recommendation.reasoning,
            "body_composition_status": recommendation.body_composition_status,
            "data_quality": {
                "weight_logs": len(weight_logs),
                "nutrition_days_logged": len(nutrition_logged_days),
                "sufficient_data": nutrition_summary.sufficient_data
            }
        }

    except Exception as e:
        import traceback
        error_details = traceback.format_exc()
        print(f"ERROR in get_nutrition_recommendation: {error_details}")
        return {
            "error": str(e),
            "message": f"Failed to get nutrition recommendation: {str(e)}",
            "traceback": error_details
        }


def get_training_summary(user_id: str) -> Dict[str, Any]:
    """
    Get weekly training progress summary from Training Specialist Agent.

    Analyzes strength trends, progression, plateaus across all exercises.

    Args:
        user_id: User ID

    Returns:
        Training summary with strength trends and exercise analysis
    """
    try:
        import sys
        import os

        # Add paths for imports
        sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
        backend_path = os.path.join(
            os.path.dirname(os.path.dirname(os.path.dirname(__file__))),
            "backend"
        )
        sys.path.insert(0, backend_path)

        from database import JSONDatabase

        # Use absolute path to project root data directory
        project_root = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
        data_path = os.path.join(project_root, "data", "tracking")
        db = JSONDatabase(data_dir=data_path)

        # Fetch latest training progress summary
        user_training_summaries = db.find('training_progress_summaries', {"user_id": user_id})

        if not user_training_summaries:
            return {
                "error": "No training data available",
                "message": "User has not completed enough workouts for analysis",
                "overall_strength_trend": "insufficient_data",
                "workouts_completed": 0
            }

        # Get most recent summary
        user_training_summaries.sort(
            key=lambda x: x.get('published_at', ''),
            reverse=True
        )
        latest_summary = user_training_summaries[0]

        return {
            "overall_strength_trend": latest_summary.get('overall_strength_trend'),
            "exercises_analyzed": latest_summary.get('exercises_analyzed', 0),
            "exercises_progressing": latest_summary.get('exercises_progressing', 0),
            "exercises_plateaued": latest_summary.get('exercises_plateaued', 0),
            "exercises_regressing": latest_summary.get('exercises_regressing', 0),
            "workouts_completed": latest_summary.get('workouts_completed', 0),
            "avg_weekly_volume_kg": latest_summary.get('avg_weekly_volume_kg', 0.0),
            "trend_confidence": latest_summary.get('trend_confidence', 0.0),
            "data_quality": latest_summary.get('data_quality', 'unknown'),
            "week": latest_summary.get('week'),
            "summary": f"Overall trend: {latest_summary.get('overall_strength_trend')}. {latest_summary.get('exercises_progressing', 0)} exercises progressing, {latest_summary.get('exercises_plateaued', 0)} plateaued, {latest_summary.get('exercises_regressing', 0)} regressing."
        }

    except Exception as e:
        return {
            "error": str(e),
            "message": f"Failed to get training summary: {str(e)}"
        }
