"""
Training Specialist Weekly Summary

Publishes weekly aggregate strength trend summaries for consumption by:
- Nutrition Agent (for bulk effectiveness assessment)
- Dashboard (for user progress tracking)
- Communication Agent (for weekly summaries)
- Coach Orchestrator (for answering questions)

This module implements the weekly scheduled mode of the Training Agent.
"""

from datetime import datetime
from typing import List, Dict, Any
from ai_agents.shared.models import TrainingProgressSummary
from ai_agents.training_specialist.tools import (
    calculate_overall_strength_trend,
    get_iso_week,
)


def publish_weekly_strength_summary(
    user_id: str,
    user_exercises: List[Dict[str, Any]],
    recent_recommendations: List[Dict[str, Any]],
    recent_workouts: List[Dict[str, Any]],
    days: int = 14,
) -> TrainingProgressSummary:
    """
    Publish weekly strength trend summary for a user.

    This function:
    1. Analyzes recent training recommendations (last 14 days)
    2. Calculates overall strength trend
    3. Calculates aggregate volume metrics
    4. Creates a TrainingProgressSummary that can be saved to database

    Args:
        user_id: User identifier
        user_exercises: List of user exercise configurations
        recent_recommendations: Recent training recommendations from last N days
        recent_workouts: Recent workout logs for volume calculation
        days: Number of days to analyze (default 14)

    Returns:
        TrainingProgressSummary ready to be saved to training_progress_summaries table

    Example:
        >>> summary = publish_weekly_strength_summary(
        ...     user_id="user_123",
        ...     user_exercises=exercises,
        ...     recent_recommendations=recommendations,
        ...     recent_workouts=workouts,
        ... )
        >>> # Save to database
        >>> db.insert("training_progress_summaries", summary.model_dump())
    """
    # Calculate overall strength trend using our deterministic algorithm
    trend_data = calculate_overall_strength_trend(
        user_exercises=user_exercises,
        recent_recommendations=recent_recommendations,
        days=days,
        recent_workouts=recent_workouts,
    )

    # Calculate aggregate weekly volume
    total_volume = 0.0
    for workout in recent_workouts:
        for exercise in workout.get("exercises", []):
            for set_data in exercise.get("sets", []):
                weight = set_data.get("weight_kg", set_data.get("weight", 0))
                reps = set_data.get("reps", 0)
                total_volume += weight * reps

    # Create TrainingProgressSummary model
    summary = TrainingProgressSummary(
        user_id=user_id,
        week=get_iso_week(),
        published_by="training_agent",
        published_at=datetime.utcnow().isoformat(),
        overall_strength_trend=trend_data["overall_strength_trend"],
        exercises_analyzed=trend_data["exercises_analyzed"],
        exercises_progressing=trend_data["exercises_progressing"],
        exercises_plateaued=trend_data["exercises_plateaued"],
        exercises_regressing=trend_data["exercises_regressing"],
        avg_weekly_volume_kg=total_volume,
        trend_confidence=trend_data["trend_confidence"],
        days_of_data=days,
        workouts_completed=len(recent_workouts),
        data_quality=trend_data["data_quality"],
    )

    return summary


def get_latest_strength_summary(
    db: Any,
    user_id: str,
) -> Dict[str, Any]:
    """
    Get the latest strength summary for a user.

    This is a helper function for the Nutrition Agent to read
    the Training Agent's published strength trend.

    Args:
        db: Database client
        user_id: User identifier

    Returns:
        dict with strength summary data, or default values if not found

    Example:
        >>> strength_summary = get_latest_strength_summary(db, "user_123")
        >>> if strength_summary["overall_strength_trend"] == "improving":
        ...     print("User is getting stronger!")
    """
    # Query training_progress_summaries table
    summaries = db.find(
        "training_progress_summaries",
        {"user_id": user_id}
    )

    if not summaries:
        # No data available - return default
        return {
            "overall_strength_trend": "insufficient_data",
            "exercises_progressing": 0,
            "exercises_plateaued": 0,
            "exercises_regressing": 0,
            "data_quality": "poor",
        }

    # Get most recent summary (sorted by week)
    latest = sorted(summaries, key=lambda x: x.get("week", ""), reverse=True)[0]

    return {
        "overall_strength_trend": latest.get("overall_strength_trend", "insufficient_data"),
        "exercises_progressing": latest.get("exercises_progressing", 0),
        "exercises_plateaued": latest.get("exercises_plateaued", 0),
        "exercises_regressing": latest.get("exercises_regressing", 0),
        "data_quality": latest.get("data_quality", "poor"),
        "trend_confidence": latest.get("trend_confidence", 0.0),
        "week": latest.get("week", ""),
    }
