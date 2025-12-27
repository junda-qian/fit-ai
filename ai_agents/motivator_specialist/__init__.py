"""
Motivator Specialist Agent

Tracks user streaks (nutrition logging and workout plan adherence) and generates
personalized motivational messages to enhance engagement and habit formation.
"""

from .algorithm import calculate_streaks, calculate_nutrition_streak, calculate_workout_streak

__all__ = [
    "calculate_streaks",
    "calculate_nutrition_streak",
    "calculate_workout_streak",
]
