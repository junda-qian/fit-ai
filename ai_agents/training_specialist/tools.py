"""
Training Specialist Tools

Helper functions for progression analysis and calculations.
All functions are deterministic (no AI).
"""

from typing import List, Optional
from datetime import datetime
from ai_agents.shared.models import Session, PlateauAnalysis, ModelSwitchSuggestion


def get_iso_week(dt: Optional[datetime] = None) -> str:
    """
    Get ISO week format (YYYY-Www) for a given datetime.

    ISO week format provides a standardized way to identify weeks:
    - Weeks start on Monday
    - Week 1 is the first week containing a Thursday
    - Format: YYYY-Www (e.g., "2025-W47")

    Args:
        dt: Datetime object (defaults to UTC now)

    Returns:
        str: ISO week format (e.g., "2025-W47")

    Example:
        >>> get_iso_week(datetime(2025, 11, 22))
        '2025-W47'
    """
    if dt is None:
        dt = datetime.utcnow()

    iso_calendar = dt.isocalendar()
    year = iso_calendar[0]
    week = iso_calendar[1]

    return f"{year}-W{week:02d}"


def detect_plateau(
    recent_sessions: List[Session],
    progression_model: str,
) -> PlateauAnalysis:
    """
    Detect if user is plateaued (no progress for 2+ sessions).
    Only applies to Rep Range progression.

    Args:
        recent_sessions: List of recent sessions (ordered chronologically)
        progression_model: "linear" or "rep_range"

    Returns:
        PlateauAnalysis with plateau detected flag, duration
    """
    if progression_model != "rep_range" or len(recent_sessions) < 2:
        return PlateauAnalysis(
            plateau_detected=False,
            duration_sessions=0,
            last_progressed_date=None,
        )

    # Check last 2+ sessions for progress
    # Progress = either weight increased OR reps increased
    last_session = recent_sessions[-1]
    sessions_without_progress = 0
    last_progressed_date = None

    for i in range(len(recent_sessions) - 1, 0, -1):
        current = recent_sessions[i]
        previous = recent_sessions[i - 1]

        # Check if progress was made
        weight_increased = current.first_set.weight > previous.first_set.weight
        reps_increased = (
            current.first_set.weight == previous.first_set.weight and
            current.first_set.reps > previous.first_set.reps
        )

        if weight_increased or reps_increased:
            # Found progress!
            last_progressed_date = current.date
            break
        else:
            sessions_without_progress += 1

    plateau_detected = sessions_without_progress >= 2

    return PlateauAnalysis(
        plateau_detected=plateau_detected,
        duration_sessions=sessions_without_progress,
        last_progressed_date=last_progressed_date,
    )


def detect_regression(
    today_reps: int,
    last_session_reps: int,
) -> bool:
    """
    Detect if reps decreased from last session (at same weight).

    Args:
        today_reps: Reps completed today
        last_session_reps: Reps from last session

    Returns:
        bool (true if regressed)
    """
    return today_reps < last_session_reps


def calculate_plateau_breaker_weight(
    current_weight: float,
    exercise_type: str = "compound",
) -> float:
    """
    Calculate plateau breaker weight (~10% increase).

    Max safe increase:
    - Compound exercises: ~3RM territory
    - Isolation exercises: ~5RM territory

    Args:
        current_weight: Current working weight (kg)
        exercise_type: "compound" or "isolation"

    Returns:
        float (plateau breaker weight in kg)
    """
    # 10% increase
    increase_pct = 0.10
    breaker_weight = current_weight * (1 + increase_pct)

    # Round to nearest 2.5kg for practical loading
    breaker_weight = round(breaker_weight / 2.5) * 2.5

    return breaker_weight


def suggest_progression_model_switch(
    failure_rate: float,
    increment: float,
) -> Optional[ModelSwitchSuggestion]:
    """
    Suggest switching progression models if increment is causing issues.

    Trigger:
    - Failure rate >= 50% in Linear Progressive
    - Multiple consecutive failures

    Args:
        failure_rate: Percentage of sessions where rep target was missed
        increment: Current weight increment (kg)

    Returns:
        ModelSwitchSuggestion or None
    """
    if failure_rate >= 0.5:
        # Failing 50% or more of sessions - increment too large
        return ModelSwitchSuggestion(
            from_model="linear",
            to_model="rep_range",
            reason=f"Failure rate {failure_rate*100:.0f}% suggests {increment}kg increment is too large. Switch to Rep Range to build up to next weight."
        )

    return None


def calculate_1rm(
    weight: float,
    reps: int,
) -> float:
    """
    Calculate estimated 1 rep max using Epley formula.
    Used for plateau breaker calculations.

    Formula: 1RM = weight × (1 + reps / 30)

    Args:
        weight: Weight used (kg)
        reps: Reps completed

    Returns:
        float (estimated 1RM in kg)
    """
    if reps == 1:
        return weight

    estimated_1rm = weight * (1 + reps / 30.0)
    return estimated_1rm


def calculate_rep_max_percentage(
    one_rm: float,
    target_reps: int,
) -> float:
    """
    Calculate what percentage of 1RM to use for target reps.

    Based on standard rep-max percentages:
    - 1 rep: 100%
    - 3 reps: ~90%
    - 5 reps: ~85%
    - 8 reps: ~80%
    - 10 reps: ~75%
    - 12 reps: ~70%

    Args:
        one_rm: Estimated 1 rep max (kg)
        target_reps: Target rep count

    Returns:
        float (weight to use for target reps)
    """
    # Simplified formula (inverse of Epley)
    # weight = 1RM / (1 + reps / 30)
    percentage = 1 / (1 + target_reps / 30.0)
    return one_rm * percentage


def calculate_overall_strength_trend(
    user_exercises: List[dict],
    recent_recommendations: List[dict],
    days: int = 14,
) -> dict:
    """
    Analyze recent workouts to determine overall strength trend.

    This is the Training Agent's expert assessment based on session-to-session
    progression data collected from the event-driven flow.

    Args:
        user_exercises: List of user exercise configurations
        recent_recommendations: Recent training recommendations from last N days
        days: Number of days to analyze (default 14)

    Returns:
        dict with:
            - overall_strength_trend: "improving" | "stable" | "declining" | "insufficient_data"
            - exercises_analyzed: int
            - exercises_progressing: int
            - exercises_plateaued: int
            - exercises_regressing: int
            - trend_confidence: float (0-1)
            - data_quality: "good" | "fair" | "poor"
    """
    if len(recent_recommendations) < 2:
        return {
            "overall_strength_trend": "insufficient_data",
            "exercises_analyzed": 0,
            "exercises_progressing": 0,
            "exercises_plateaued": 0,
            "exercises_regressing": 0,
            "trend_confidence": 0.0,
            "data_quality": "poor"
        }

    # Count exercises in each state
    progressing_count = 0
    plateaued_count = 0
    regressing_count = 0

    for exercise in user_exercises:
        exercise_name = exercise.get("exercise_name")

        # Get recent recommendations for this exercise
        exercise_recs = [
            r for r in recent_recommendations
            if r.get("exercise_name") == exercise_name
        ]

        if not exercise_recs:
            continue

        # Check if exercise is progressing
        # Count how many times rep target was hit
        hit_target_count = sum(
            1 for r in exercise_recs
            if r.get("hit_rep_target", False)
        )

        # Check for plateau or regression flags
        plateau_detected = any(
            r.get("plateau_detected", False)
            for r in exercise_recs
        )
        regression_detected = any(
            r.get("regression_detected", False)
            for r in exercise_recs
        )

        # Categorize exercise
        if regression_detected:
            regressing_count += 1
        elif plateau_detected:
            plateaued_count += 1
        elif hit_target_count >= len(exercise_recs) * 0.7:  # Hit target in 70%+ of sessions
            progressing_count += 1
        else:
            plateaued_count += 1

    total = progressing_count + plateaued_count + regressing_count

    if total == 0:
        return {
            "overall_strength_trend": "insufficient_data",
            "exercises_analyzed": 0,
            "exercises_progressing": 0,
            "exercises_plateaued": 0,
            "exercises_regressing": 0,
            "trend_confidence": 0.0,
            "data_quality": "poor"
        }

    # Determine overall trend
    progressing_pct = progressing_count / total
    regressing_pct = regressing_count / total

    if regressing_pct > 0.3:  # >30% of exercises regressing
        overall_trend = "declining"
    elif progressing_pct >= 0.6:  # >=60% of exercises progressing
        overall_trend = "improving"
    else:
        overall_trend = "stable"

    # Calculate confidence based on number of exercises
    # More exercises = higher confidence
    trend_confidence = min(total / 5.0, 1.0)

    # Determine data quality
    if total >= 3:
        data_quality = "good"
    elif total >= 1:
        data_quality = "fair"
    else:
        data_quality = "poor"

    return {
        "overall_strength_trend": overall_trend,
        "exercises_analyzed": total,
        "exercises_progressing": progressing_count,
        "exercises_plateaued": plateaued_count,
        "exercises_regressing": regressing_count,
        "trend_confidence": trend_confidence,
        "data_quality": data_quality
    }
