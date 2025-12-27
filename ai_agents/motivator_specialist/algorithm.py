"""
Motivator Specialist Algorithm

Deterministic streak calculation (NO AI).
Calculates nutrition logging streaks and workout plan adherence streaks.
"""

from datetime import date, timedelta, datetime
from typing import Dict, Optional
import sys
import os

# Add parent directory to path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

from ai_agents.shared.models import StreakData


def parse_frequency(frequency_str: Optional[str]) -> int:
    """
    Parse workout frequency string to integer.

    Args:
        frequency_str: Frequency string like "4x/week" or None

    Returns:
        Target workouts per week (default: 3)

    Examples:
        >>> parse_frequency("4x/week")
        4
        >>> parse_frequency("3x/week")
        3
        >>> parse_frequency(None)
        3
    """
    if not frequency_str or "/week" not in frequency_str:
        return 3  # Default assumption

    try:
        return int(frequency_str.split("x/week")[0].strip())
    except (ValueError, IndexError):
        return 3


def calculate_nutrition_streak(db, user_id: str) -> Dict:
    """
    Calculate consecutive days with nutrition logs.

    Applies 1-day grace period: if logged yesterday, streak is still active today.

    Args:
        db: Database adapter instance
        user_id: User identifier

    Returns:
        Dict with current_streak, longest_streak, last_logged_date
    """
    # Query nutrition logs for last 30 days
    end_date = date.today()
    start_date = end_date - timedelta(days=30)

    nutrition_logs = db.get_nutrition_logs_by_date_range(
        user_id=user_id,
        start_date=start_date.isoformat(),
        end_date=end_date.isoformat()
    )

    if not nutrition_logs:
        return {
            "current_streak": 0,
            "longest_streak": 0,
            "last_logged_date": None
        }

    # Extract unique dates with logs
    logged_dates = set()
    for log in nutrition_logs:
        log_date_str = log.get("date")
        if log_date_str:
            logged_dates.add(log_date_str)

    # Sort dates
    sorted_dates = sorted([date.fromisoformat(d) for d in logged_dates])

    if not sorted_dates:
        return {
            "current_streak": 0,
            "longest_streak": 0,
            "last_logged_date": None
        }

    # Calculate current streak (working backwards from today)
    current_streak = 0
    check_date = date.today()

    # Apply 1-day grace period
    yesterday = check_date - timedelta(days=1)

    # Check if logged yesterday (grace period)
    if yesterday in sorted_dates:
        current_streak = 1
        check_date = yesterday

        # Continue counting backwards
        while True:
            check_date = check_date - timedelta(days=1)
            if check_date in sorted_dates:
                current_streak += 1
            else:
                break

    # If not logged yesterday, check if logged today
    elif check_date in sorted_dates:
        current_streak = 1
        # Continue counting backwards
        while True:
            check_date = check_date - timedelta(days=1)
            if check_date in sorted_dates:
                current_streak += 1
            else:
                break

    # Calculate longest streak
    longest_streak = 0
    temp_streak = 0
    prev_date = None

    for log_date in sorted_dates:
        if prev_date is None:
            temp_streak = 1
        elif (log_date - prev_date).days == 1:
            temp_streak += 1
        else:
            longest_streak = max(longest_streak, temp_streak)
            temp_streak = 1

        prev_date = log_date

    longest_streak = max(longest_streak, temp_streak)

    # Ensure longest_streak is at least current_streak
    longest_streak = max(longest_streak, current_streak)

    return {
        "current_streak": current_streak,
        "longest_streak": longest_streak,
        "last_logged_date": sorted_dates[-1].isoformat() if sorted_dates else None
    }


def calculate_workout_adherence_week(
    db, user_id: str, week_start: date, target: int
) -> bool:
    """
    Check if user met workout target for a given week.

    90% threshold: 3/4 workouts counts as success.

    Args:
        db: Database adapter instance
        user_id: User identifier
        week_start: Monday of the week to check
        target: Target workouts per week

    Returns:
        True if user met >=90% of target, False otherwise
    """
    week_end = week_start + timedelta(days=7)

    workout_logs = db.get_workout_logs_by_date_range(
        user_id=user_id,
        start_date=week_start.isoformat(),
        end_date=week_end.isoformat()
    )

    # Count completed workouts
    actual = len([log for log in workout_logs if log.get("completed", True)])

    # 90% threshold
    return actual >= (target * 0.9)


def calculate_workout_streak(db, user_id: str) -> Dict:
    """
    Calculate consecutive weeks meeting workout plan targets.

    Compares actual workout logs against workout_plans.frequency.
    Excludes current incomplete week.

    Args:
        db: Database adapter instance
        user_id: User identifier

    Returns:
        Dict with current_streak, longest_streak, target, this_week_count
    """
    # Get active workout plan
    plan = db.get_active_workout_plan(user_id)

    if not plan:
        # No active plan - count this week's workouts anyway
        today = date.today()
        week_start = today - timedelta(days=today.weekday())
        week_end = today

        this_week_logs = db.get_workout_logs_by_date_range(
            user_id=user_id,
            start_date=week_start.isoformat(),
            end_date=week_end.isoformat()
        )
        this_week_count = len([log for log in this_week_logs if log.get("completed", True)])

        return {
            "current_streak": 0,
            "longest_streak": 0,
            "target": 0,
            "this_week_count": this_week_count
        }

    # Parse frequency
    target = parse_frequency(plan.get("frequency", "3x/week"))

    # Get current week info
    today = date.today()
    current_week_monday = today - timedelta(days=today.weekday())

    # Count this week's workouts (incomplete week)
    this_week_logs = db.get_workout_logs_by_date_range(
        user_id=user_id,
        start_date=current_week_monday.isoformat(),
        end_date=today.isoformat()
    )
    this_week_count = len([log for log in this_week_logs if log.get("completed", True)])

    # Start from last complete week (last Monday)
    last_week_monday = current_week_monday - timedelta(days=7)

    current_streak = 0
    longest_streak = 0
    temp_streak = 0

    # Check last 12 weeks max
    for i in range(12):
        week_start = last_week_monday - timedelta(days=7 * i)

        if calculate_workout_adherence_week(db, user_id, week_start, target):
            temp_streak += 1
            if i == 0:  # Most recent complete week
                current_streak = temp_streak
        else:
            longest_streak = max(longest_streak, temp_streak)
            temp_streak = 0

    # Update longest if current streak is the longest
    longest_streak = max(longest_streak, temp_streak)

    # If we're still in a streak, current_streak = temp_streak
    if temp_streak > 0:
        current_streak = temp_streak

    return {
        "current_streak": current_streak,
        "longest_streak": longest_streak,
        "target": target,
        "this_week_count": this_week_count
    }


def assess_data_quality(nutrition_days: int, workout_weeks: int) -> str:
    """
    Determine data quality for streak reliability.

    Args:
        nutrition_days: Days with nutrition logs
        workout_weeks: Weeks with workout data

    Returns:
        Data quality level: "excellent", "good", "fair", or "poor"
    """
    if nutrition_days >= 14 and workout_weeks >= 4:
        return "excellent"
    elif nutrition_days >= 7 and workout_weeks >= 2:
        return "good"
    elif nutrition_days >= 3 or workout_weeks >= 1:
        return "fair"
    else:
        return "poor"


def calculate_streaks(db, user_id: str) -> StreakData:
    """
    Main entry point for streak calculation.

    Orchestrates nutrition and workout streak calculations.

    Args:
        db: Database adapter instance
        user_id: User identifier

    Returns:
        StreakData model with all streak information
    """
    # Calculate nutrition streak
    nutrition_data = calculate_nutrition_streak(db, user_id)

    # Calculate workout streak
    workout_data = calculate_workout_streak(db, user_id)

    # Count days analyzed (30 for nutrition, 12 weeks for workouts)
    days_analyzed = 30

    # Assess data quality
    nutrition_days = nutrition_data["current_streak"]
    workout_weeks = workout_data["current_streak"]

    sufficient_data = (nutrition_days >= 3 or workout_weeks >= 1)

    return StreakData(
        # Nutrition
        nutrition_current_streak=nutrition_data["current_streak"],
        nutrition_longest_streak=nutrition_data["longest_streak"],
        nutrition_last_logged_date=nutrition_data["last_logged_date"],
        # Workout
        workout_current_streak=workout_data["current_streak"],
        workout_longest_streak=workout_data["longest_streak"],
        workout_target_per_week=workout_data["target"],
        workout_this_week_count=workout_data["this_week_count"],
        # Data quality
        sufficient_data=sufficient_data,
        days_analyzed=days_analyzed
    )
