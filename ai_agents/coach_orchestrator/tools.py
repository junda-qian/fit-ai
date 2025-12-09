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
        # Phase 4: Will add get_nutrition_recommendation, get_training_status
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

    # Phase 4: Add specialist agent tool routing
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
        # Phase 4: Will add specialist agent tools
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
    backend_path = os.path.join(
        os.path.dirname(os.path.dirname(os.path.dirname(__file__))),
        "backend"
    )
    sys.path.insert(0, backend_path)
    from database import JSONDatabase
    return JSONDatabase()


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

        if filtered_logs:
            avg_calories = round(sum(log.get("calories", 0) for log in filtered_logs) / len(filtered_logs), 1)
            avg_protein = round(sum(log.get("protein_g", 0) for log in filtered_logs) / len(filtered_logs), 1)
        else:
            avg_calories = avg_protein = 0

        return {
            "logs": filtered_logs[:10],
            "summary": {
                "days_logged": len(filtered_logs),
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

# TODO: Implement in Phase 4
# - get_nutrition_recommendation(user_id)
# - get_training_status(user_id, exercise)
# - analyze_progress(user_id, metric, timeframe)
