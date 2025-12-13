"""
Tests for Training Specialist Weekly Summary

Tests the weekly scheduled mode that publishes strength trend summaries.
"""

import pytest
from datetime import datetime
from ai_agents.training_specialist.weekly_summary import (
    publish_weekly_strength_summary,
    get_latest_strength_summary,
)
from ai_agents.training_specialist.tools import get_iso_week


def test_get_iso_week():
    """Test ISO week format generation"""
    # Test with specific date
    dt = datetime(2025, 11, 22)  # Saturday, November 22, 2025
    week = get_iso_week(dt)

    # Should be week 47 of 2025
    assert week == "2025-W47"

    # Test with current time (should not raise error)
    current_week = get_iso_week()
    assert current_week.startswith("20")  # Year should start with 20
    assert "-W" in current_week


def test_publish_weekly_strength_summary_improving():
    """Test publishing summary when user is improving"""
    user_exercises = [
        {"exercise_name": "bench_press"},
        {"exercise_name": "squat"},
        {"exercise_name": "deadlift"},
    ]

    # All exercises progressing (hit target in all sessions)
    recent_recommendations = [
        {
            "exercise_name": "bench_press",
            "today_analysis": {
                "hit_rep_target": True,
                "plateau_detected": False,
                "regression_detected": False,
            }
        },
        {
            "exercise_name": "squat",
            "today_analysis": {
                "hit_rep_target": True,
                "plateau_detected": False,
                "regression_detected": False,
            }
        },
        {
            "exercise_name": "deadlift",
            "today_analysis": {
                "hit_rep_target": True,
                "plateau_detected": False,
                "regression_detected": False,
            }
        },
    ]

    recent_workouts = [
        {
            "exercises": [
                {
                    "name": "bench_press",
                    "sets": [
                        {"weight": 100, "reps": 11},
                        {"weight": 100, "reps": 8},
                    ]
                }
            ]
        }
    ]

    summary = publish_weekly_strength_summary(
        user_id="user_123",
        user_exercises=user_exercises,
        recent_recommendations=recent_recommendations,
        recent_workouts=recent_workouts,
    )

    # Assertions
    assert summary.user_id == "user_123"
    assert summary.overall_strength_trend == "improving"  # 100% progressing
    assert summary.exercises_analyzed == 3
    assert summary.exercises_progressing == 3
    assert summary.exercises_plateaued == 0
    assert summary.exercises_regressing == 0
    assert summary.data_quality == "good"  # 3 exercises
    assert summary.trend_confidence == 0.6  # min(3/5, 1.0)
    assert summary.avg_weekly_volume_kg == 100 * 11 + 100 * 8  # 1900kg

    print(f"✅ Test passed: {summary.overall_strength_trend} trend detected correctly")


def test_publish_weekly_strength_summary_plateaued():
    """Test publishing summary when user has plateaued"""
    user_exercises = [
        {"exercise_name": "bench_press"},
        {"exercise_name": "squat"},
    ]

    # One progressing, one plateaued
    recent_recommendations = [
        {
            "exercise_name": "bench_press",
            "today_analysis": {
                "hit_rep_target": True,
                "plateau_detected": False,
                "regression_detected": False,
            }
        },
        {
            "exercise_name": "squat",
            "today_analysis": {
                "hit_rep_target": False,
                "plateau_detected": True,
                "regression_detected": False,
            }
        },
    ]

    recent_workouts = []

    summary = publish_weekly_strength_summary(
        user_id="user_456",
        user_exercises=user_exercises,
        recent_recommendations=recent_recommendations,
        recent_workouts=recent_workouts,
    )

    # 50% progressing - should be "stable"
    assert summary.overall_strength_trend == "stable"
    assert summary.exercises_analyzed == 2
    assert summary.exercises_progressing == 1
    assert summary.exercises_plateaued == 1
    assert summary.data_quality == "fair"  # 2 exercises

    print(f"✅ Test passed: {summary.overall_strength_trend} trend detected correctly")


def test_publish_weekly_strength_summary_declining():
    """Test publishing summary when user is declining"""
    user_exercises = [
        {"exercise_name": "bench_press"},
        {"exercise_name": "squat"},
        {"exercise_name": "deadlift"},
    ]

    # 2 regressing, 1 progressing = 66% regressing
    recent_recommendations = [
        {
            "exercise_name": "bench_press",
            "today_analysis": {
                "hit_rep_target": False,
                "plateau_detected": False,
                "regression_detected": True,
            }
        },
        {
            "exercise_name": "squat",
            "today_analysis": {
                "hit_rep_target": False,
                "plateau_detected": False,
                "regression_detected": True,
            }
        },
        {
            "exercise_name": "deadlift",
            "today_analysis": {
                "hit_rep_target": True,
                "plateau_detected": False,
                "regression_detected": False,
            }
        },
    ]

    recent_workouts = []

    summary = publish_weekly_strength_summary(
        user_id="user_789",
        user_exercises=user_exercises,
        recent_recommendations=recent_recommendations,
        recent_workouts=recent_workouts,
    )

    # >30% regressing - should be "declining"
    assert summary.overall_strength_trend == "declining"
    assert summary.exercises_regressing == 2
    assert summary.exercises_progressing == 1

    print(f"✅ Test passed: {summary.overall_strength_trend} trend detected correctly")


def test_publish_weekly_strength_summary_insufficient_data():
    """Test publishing summary with insufficient data"""
    user_exercises = [
        {"exercise_name": "bench_press"},
    ]

    # Only 1 recommendation (need at least 2 for analysis)
    recent_recommendations = [
        {
            "exercise_name": "bench_press",
            "today_analysis": {
                "hit_rep_target": True,
                "plateau_detected": False,
                "regression_detected": False,
            }
        },
    ]

    recent_workouts = []

    summary = publish_weekly_strength_summary(
        user_id="user_new",
        user_exercises=user_exercises,
        recent_recommendations=recent_recommendations,
        recent_workouts=recent_workouts,
    )

    # Not enough data (need at least 2 recommendations)
    assert summary.overall_strength_trend == "insufficient_data"
    assert summary.exercises_analyzed == 0
    assert summary.data_quality == "poor"
    assert summary.trend_confidence == 0.0

    print(f"✅ Test passed: Insufficient data handled correctly")


def test_get_latest_strength_summary_with_data():
    """Test getting latest strength summary when data exists"""

    class MockDB:
        def find(self, collection, query):
            # Return mock summaries
            return [
                {
                    "user_id": "user_123",
                    "week": "2025-W46",
                    "overall_strength_trend": "stable",
                    "exercises_progressing": 2,
                    "exercises_plateaued": 1,
                    "exercises_regressing": 0,
                    "data_quality": "good",
                    "trend_confidence": 0.6,
                },
                {
                    "user_id": "user_123",
                    "week": "2025-W47",  # More recent
                    "overall_strength_trend": "improving",
                    "exercises_progressing": 3,
                    "exercises_plateaued": 0,
                    "exercises_regressing": 0,
                    "data_quality": "good",
                    "trend_confidence": 0.6,
                },
            ]

    db = MockDB()
    summary = get_latest_strength_summary(db, "user_123")

    # Should get the most recent week (W47)
    assert summary["overall_strength_trend"] == "improving"
    assert summary["week"] == "2025-W47"
    assert summary["exercises_progressing"] == 3

    print(f"✅ Test passed: Latest summary retrieved correctly")


def test_get_latest_strength_summary_no_data():
    """Test getting latest strength summary when no data exists"""

    class MockDB:
        def find(self, collection, query):
            return []  # No data

    db = MockDB()
    summary = get_latest_strength_summary(db, "user_new")

    # Should return default values
    assert summary["overall_strength_trend"] == "insufficient_data"
    assert summary["exercises_progressing"] == 0
    assert summary["data_quality"] == "poor"

    print(f"✅ Test passed: Default values returned when no data")


if __name__ == "__main__":
    print("Running Training Specialist Weekly Summary Tests...\n")

    test_get_iso_week()
    test_publish_weekly_strength_summary_improving()
    test_publish_weekly_strength_summary_plateaued()
    test_publish_weekly_strength_summary_declining()
    test_publish_weekly_strength_summary_insufficient_data()
    test_get_latest_strength_summary_with_data()
    test_get_latest_strength_summary_no_data()

    print("\n🎉 All tests passed!")
