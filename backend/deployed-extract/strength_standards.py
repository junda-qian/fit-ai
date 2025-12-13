"""
Strength Standards Module

This module provides functions to calculate estimated 1RM and determine training status
based on ExRx.net strength standards.

Reference: https://exrx.net/Testing/WeightLifting/StrengthStandards
"""

from typing import Dict, List, Tuple, Optional


def calculate_1rm(weight_kg: float, reps: int) -> float:
    """
    Calculate estimated 1RM using Epley formula

    Formula: Weight × (1 + (Reps / 30))

    Args:
        weight_kg: Weight lifted in kg
        reps: Number of reps performed

    Returns:
        Estimated 1RM in kg

    Example:
        >>> calculate_1rm(80, 5)
        93.33
    """
    if reps <= 0:
        return weight_kg

    return weight_kg * (1 + (reps / 30))


def find_closest_bodyweight_category(bodyweight_kg: float, sex: str) -> float:
    """
    Find closest bodyweight category for strength standards

    Args:
        bodyweight_kg: User's bodyweight in kg
        sex: 'male' or 'female'

    Returns:
        Closest standard bodyweight category

    Example:
        >>> find_closest_bodyweight_category(73, 'male')
        75
    """
    if sex.lower() in ['male', 'm']:
        categories = [52, 56, 60, 67, 75, 82, 90, 100, 110, 125, 145]
    else:  # female
        categories = [44, 48, 52, 56, 60, 67, 75, 82, 90]

    # Find closest category
    closest = min(categories, key=lambda x: abs(x - bodyweight_kg))

    # If user is heavier than max category, use max+ category
    if bodyweight_kg > max(categories):
        return max(categories)

    return closest


def get_standards_for_exercise(
    exercise_name: str,
    bodyweight_kg: float,
    sex: str
) -> Optional[Dict[str, float]]:
    """
    Get strength standards for a specific exercise

    Args:
        exercise_name: One of "Bench Press", "Press", "Deadlift", "Squat"
        bodyweight_kg: User's bodyweight in kg
        sex: 'male' or 'female'

    Returns:
        Dictionary with thresholds for each level, or None if exercise not found

    Example:
        >>> get_standards_for_exercise("Bench Press", 75, "male")
        {'Untrained': 55.0, 'Novice': 70.0, 'Intermediate': 85.0, 'Advanced': 115.0, 'Elite': 145.0}
    """
    # Normalize exercise name
    exercise_map = {
        "bench press": "Bench Press",
        "barbell bench press": "Bench Press",
        "overhead press": "Press",
        "press": "Press",
        "barbell overhead press": "Press",
        "dumbbell overhead press": "Press",
        "deadlift": "Deadlift",
        "powerlifting deadlift": "Deadlift",
        "romanian deadlift": "Deadlift",
        "squat": "Squat",
        "barbell squat": "Squat",
        "back squat": "Squat",
    }

    normalized_name = exercise_name.lower().strip()
    standard_name = exercise_map.get(normalized_name)

    if not standard_name or standard_name not in STRENGTH_STANDARDS:
        return None

    sex_normalized = 'male' if sex.lower() in ['male', 'm'] else 'female'
    bw_category = find_closest_bodyweight_category(bodyweight_kg, sex_normalized)

    return STRENGTH_STANDARDS[standard_name][sex_normalized].get(bw_category)


def determine_training_status(
    exercise_name: str,
    one_rm_kg: float,
    bodyweight_kg: float,
    sex: str
) -> str:
    """
    Determine training status based on 1RM and strength standards

    Args:
        exercise_name: One of "Bench Press", "Press", "Deadlift", "Squat"
        one_rm_kg: Calculated 1RM in kg
        bodyweight_kg: User's bodyweight in kg
        sex: 'male' or 'female'

    Returns:
        Training status: "Untrained", "Novice", "Intermediate", "Advanced", or "Elite"

    Example:
        >>> determine_training_status("Bench Press", 85, 75, "male")
        'Intermediate'
    """
    standards = get_standards_for_exercise(exercise_name, bodyweight_kg, sex)

    if not standards:
        return "Novice"  # Default if exercise not found

    # Determine status by comparing 1RM to thresholds
    if one_rm_kg < standards['Novice']:
        return "Untrained"
    elif one_rm_kg < standards['Intermediate']:
        return "Novice"
    elif one_rm_kg < standards['Advanced']:
        return "Intermediate"
    elif one_rm_kg < standards['Elite']:
        return "Advanced"
    else:
        return "Elite"


def calculate_overall_status(exercise_statuses: List[str]) -> str:
    """
    Calculate overall training status from multiple exercises using median

    Args:
        exercise_statuses: List of status strings for different exercises

    Returns:
        Overall training status (median)

    Example:
        >>> calculate_overall_status(["Novice", "Intermediate", "Intermediate", "Advanced"])
        'Intermediate'
    """
    if not exercise_statuses:
        return "Novice"

    status_order = ["Untrained", "Novice", "Intermediate", "Advanced", "Elite"]

    # Convert to indices
    status_indices = [status_order.index(s) for s in exercise_statuses if s in status_order]

    if not status_indices:
        return "Novice"

    # Get median
    sorted_indices = sorted(status_indices)
    median_index = sorted_indices[len(sorted_indices) // 2]

    return status_order[median_index]


# ============================================================================
# STRENGTH STANDARDS DATA
# Source: ExRx.net (Age 18-39)
# ============================================================================

STRENGTH_STANDARDS = {
    "Bench Press": {
        "male": {
            52: {"Untrained": 37.5, "Novice": 50.0, "Intermediate": 60.0, "Advanced": 82.5, "Elite": 100.0},
            56: {"Untrained": 40.0, "Novice": 52.5, "Intermediate": 62.5, "Advanced": 90.0, "Elite": 110.0},
            60: {"Untrained": 45.0, "Novice": 57.5, "Intermediate": 70.0, "Advanced": 95.0, "Elite": 117.5},
            67: {"Untrained": 50.0, "Novice": 65.0, "Intermediate": 77.5, "Advanced": 107.5, "Elite": 132.5},
            75: {"Untrained": 55.0, "Novice": 70.0, "Intermediate": 85.0, "Advanced": 115.0, "Elite": 145.0},
            82: {"Untrained": 60.0, "Novice": 75.0, "Intermediate": 90.0, "Advanced": 125.0, "Elite": 157.5},
            90: {"Untrained": 62.5, "Novice": 80.0, "Intermediate": 97.5, "Advanced": 132.5, "Elite": 162.5},
            100: {"Untrained": 62.5, "Novice": 82.5, "Intermediate": 102.5, "Advanced": 137.5, "Elite": 172.5},
            110: {"Untrained": 65.0, "Novice": 85.0, "Intermediate": 105.0, "Advanced": 142.5, "Elite": 180.0},
            125: {"Untrained": 67.5, "Novice": 87.5, "Intermediate": 107.5, "Advanced": 147.5, "Elite": 185.0},
            145: {"Untrained": 70.0, "Novice": 90.0, "Intermediate": 112.5, "Advanced": 152.5, "Elite": 190.0},
        },
        "female": {
            44: {"Untrained": 22.5, "Novice": 30.0, "Intermediate": 35.0, "Advanced": 42.5, "Elite": 52.5},
            48: {"Untrained": 25.0, "Novice": 32.5, "Intermediate": 37.5, "Advanced": 45.0, "Elite": 57.5},
            52: {"Untrained": 27.5, "Novice": 35.0, "Intermediate": 37.5, "Advanced": 50.0, "Elite": 62.5},
            56: {"Untrained": 30.0, "Novice": 37.5, "Intermediate": 40.0, "Advanced": 52.5, "Elite": 65.0},
            60: {"Untrained": 32.5, "Novice": 40.0, "Intermediate": 42.5, "Advanced": 57.5, "Elite": 67.5},
            67: {"Untrained": 35.0, "Novice": 40.0, "Intermediate": 47.5, "Advanced": 62.5, "Elite": 75.0},
            75: {"Untrained": 37.5, "Novice": 42.5, "Intermediate": 52.5, "Advanced": 65.0, "Elite": 85.0},
            82: {"Untrained": 37.5, "Novice": 50.0, "Intermediate": 55.0, "Advanced": 72.5, "Elite": 90.0},
            90: {"Untrained": 40.0, "Novice": 52.5, "Intermediate": 60.0, "Advanced": 75.0, "Elite": 95.0},
        }
    },
    "Press": {
        "male": {
            52: {"Untrained": 22.5, "Novice": 32.5, "Intermediate": 40.0, "Advanced": 50.0, "Elite": 60.0},
            56: {"Untrained": 25.0, "Novice": 35.0, "Intermediate": 45.0, "Advanced": 52.5, "Elite": 65.0},
            60: {"Untrained": 27.5, "Novice": 37.5, "Intermediate": 47.5, "Advanced": 57.5, "Elite": 70.0},
            67: {"Untrained": 30.0, "Novice": 42.5, "Intermediate": 55.0, "Advanced": 62.5, "Elite": 77.5},
            75: {"Untrained": 32.5, "Novice": 45.0, "Intermediate": 57.5, "Advanced": 70.0, "Elite": 85.0},
            82: {"Untrained": 35.0, "Novice": 50.0, "Intermediate": 62.5, "Advanced": 75.0, "Elite": 100.0},
            90: {"Untrained": 37.5, "Novice": 52.5, "Intermediate": 65.0, "Advanced": 77.5, "Elite": 105.0},
            100: {"Untrained": 40.0, "Novice": 55.0, "Intermediate": 70.0, "Advanced": 82.5, "Elite": 115.0},
            110: {"Untrained": 42.5, "Novice": 57.5, "Intermediate": 72.5, "Advanced": 85.0, "Elite": 120.0},
            125: {"Untrained": 42.5, "Novice": 60.0, "Intermediate": 75.0, "Advanced": 87.5, "Elite": 122.5},
            145: {"Untrained": 45.0, "Novice": 60.0, "Intermediate": 75.0, "Advanced": 90.0, "Elite": 125.0},
        },
        "female": {
            44: {"Untrained": 15.0, "Novice": 17.5, "Intermediate": 22.5, "Advanced": 30.0, "Elite": 40.0},
            48: {"Untrained": 15.0, "Novice": 20.0, "Intermediate": 25.0, "Advanced": 32.5, "Elite": 42.5},
            52: {"Untrained": 17.5, "Novice": 22.5, "Intermediate": 27.5, "Advanced": 35.0, "Elite": 45.0},
            56: {"Untrained": 17.5, "Novice": 22.5, "Intermediate": 27.5, "Advanced": 37.5, "Elite": 47.5},
            60: {"Untrained": 17.5, "Novice": 25.0, "Intermediate": 30.0, "Advanced": 40.0, "Elite": 50.0},
            67: {"Untrained": 20.0, "Novice": 27.5, "Intermediate": 32.5, "Advanced": 42.5, "Elite": 55.0},
            75: {"Untrained": 22.5, "Novice": 30.0, "Intermediate": 35.0, "Advanced": 47.5, "Elite": 62.5},
            82: {"Untrained": 22.5, "Novice": 32.5, "Intermediate": 37.5, "Advanced": 50.0, "Elite": 65.0},
            90: {"Untrained": 25.0, "Novice": 35.0, "Intermediate": 40.0, "Advanced": 52.5, "Elite": 67.5},
        }
    },
    "Deadlift": {
        "male": {
            52: {"Untrained": 42.5, "Novice": 82.5, "Intermediate": 92.5, "Advanced": 135.0, "Elite": 175.0},
            56: {"Untrained": 47.5, "Novice": 87.5, "Intermediate": 100.0, "Advanced": 145.0, "Elite": 187.5},
            60: {"Untrained": 50.0, "Novice": 95.0, "Intermediate": 110.0, "Advanced": 155.0, "Elite": 200.0},
            67: {"Untrained": 57.5, "Novice": 107.5, "Intermediate": 122.5, "Advanced": 172.5, "Elite": 217.5},
            75: {"Untrained": 62.5, "Novice": 115.0, "Intermediate": 135.0, "Advanced": 185.0, "Elite": 235.0},
            82: {"Untrained": 67.5, "Novice": 125.0, "Intermediate": 142.5, "Advanced": 200.0, "Elite": 250.0},
            90: {"Untrained": 70.0, "Novice": 132.5, "Intermediate": 152.5, "Advanced": 207.5, "Elite": 257.5},
            100: {"Untrained": 75.0, "Novice": 137.5, "Intermediate": 160.0, "Advanced": 217.5, "Elite": 265.0},
            110: {"Untrained": 77.5, "Novice": 145.0, "Intermediate": 165.0, "Advanced": 222.5, "Elite": 270.0},
            125: {"Untrained": 80.0, "Novice": 147.5, "Intermediate": 170.0, "Advanced": 227.5, "Elite": 272.5},
            145: {"Untrained": 82.5, "Novice": 152.5, "Intermediate": 172.5, "Advanced": 230.0, "Elite": 277.5},
        },
        "female": {
            44: {"Untrained": 25.0, "Novice": 47.5, "Intermediate": 50.0, "Advanced": 80.0, "Elite": 105.0},
            48: {"Untrained": 27.5, "Novice": 52.5, "Intermediate": 60.0, "Advanced": 85.0, "Elite": 110.0},
            52: {"Untrained": 30.0, "Novice": 55.0, "Intermediate": 62.5, "Advanced": 90.0, "Elite": 115.0},
            56: {"Untrained": 32.5, "Novice": 60.0, "Intermediate": 67.5, "Advanced": 95.0, "Elite": 120.0},
            60: {"Untrained": 35.0, "Novice": 62.5, "Intermediate": 72.5, "Advanced": 100.0, "Elite": 125.0},
            67: {"Untrained": 37.5, "Novice": 67.5, "Intermediate": 80.0, "Advanced": 110.0, "Elite": 135.0},
            75: {"Untrained": 40.0, "Novice": 72.5, "Intermediate": 85.0, "Advanced": 117.5, "Elite": 145.0},
            82: {"Untrained": 42.5, "Novice": 80.0, "Intermediate": 92.5, "Advanced": 125.0, "Elite": 150.0},
            90: {"Untrained": 45.0, "Novice": 87.5, "Intermediate": 97.5, "Advanced": 130.0, "Elite": 160.0},
        }
    },
    "Squat": {
        "male": {
            52: {"Untrained": 35.0, "Novice": 65.0, "Intermediate": 80.0, "Advanced": 107.5, "Elite": 145.0},
            56: {"Untrained": 37.5, "Novice": 70.0, "Intermediate": 87.5, "Advanced": 117.5, "Elite": 157.5},
            60: {"Untrained": 40.0, "Novice": 77.5, "Intermediate": 92.5, "Advanced": 127.5, "Elite": 167.5},
            67: {"Untrained": 45.0, "Novice": 85.0, "Intermediate": 105.0, "Advanced": 142.5, "Elite": 185.0},
            75: {"Untrained": 50.0, "Novice": 92.5, "Intermediate": 112.5, "Advanced": 155.0, "Elite": 202.5},
            82: {"Untrained": 55.0, "Novice": 100.0, "Intermediate": 122.5, "Advanced": 167.5, "Elite": 217.5},
            90: {"Untrained": 57.5, "Novice": 105.0, "Intermediate": 130.0, "Advanced": 177.5, "Elite": 230.0},
            100: {"Untrained": 60.0, "Novice": 110.0, "Intermediate": 135.0, "Advanced": 185.0, "Elite": 240.0},
            110: {"Untrained": 62.5, "Novice": 115.0, "Intermediate": 140.0, "Advanced": 192.5, "Elite": 250.0},
            125: {"Untrained": 65.0, "Novice": 117.5, "Intermediate": 145.0, "Advanced": 197.5, "Elite": 257.5},
            145: {"Untrained": 67.5, "Novice": 122.5, "Intermediate": 147.5, "Advanced": 202.5, "Elite": 262.5},
        },
        "female": {
            44: {"Untrained": 20.0, "Novice": 37.5, "Intermediate": 45.0, "Advanced": 60.0, "Elite": 75.0},
            48: {"Untrained": 22.5, "Novice": 40.0, "Intermediate": 47.5, "Advanced": 65.0, "Elite": 80.0},
            52: {"Untrained": 25.0, "Novice": 45.0, "Intermediate": 52.5, "Advanced": 67.5, "Elite": 87.5},
            56: {"Untrained": 25.0, "Novice": 47.5, "Intermediate": 55.0, "Advanced": 72.5, "Elite": 90.0},
            60: {"Untrained": 27.5, "Novice": 50.0, "Intermediate": 60.0, "Advanced": 77.5, "Elite": 95.0},
            67: {"Untrained": 30.0, "Novice": 55.0, "Intermediate": 62.5, "Advanced": 85.0, "Elite": 105.0},
            75: {"Untrained": 32.5, "Novice": 57.5, "Intermediate": 67.5, "Advanced": 90.0, "Elite": 115.0},
            82: {"Untrained": 35.0, "Novice": 62.5, "Intermediate": 75.0, "Advanced": 97.5, "Elite": 122.5},
            90: {"Untrained": 37.5, "Novice": 67.5, "Intermediate": 80.0, "Advanced": 105.0, "Elite": 132.5},
        }
    }
}
