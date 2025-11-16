"""
Unit Tests for Training Specialist Agent

Tests the deterministic progression algorithms:
- Linear Progressive progression
- Rep Range progression
- Plateau detection
- Regression detection
- Plateau breakers
- Model switching suggestions

Run with: pytest test_training.py -v
"""

import pytest
from datetime import datetime, timedelta
from ai_agents.shared.models import (
    Set,
    Session,
    ExerciseConfig,
    NextSession,
    NextSessionRecommendation,
)
from ai_agents.training_specialist.algorithm import (
    analyze_exercise_session,
    apply_linear_progressive_rules,
    apply_rep_range_rules,
)
from ai_agents.training_specialist.tools import (
    detect_plateau,
    detect_regression,
    calculate_plateau_breaker_weight,
    suggest_progression_model_switch,
    calculate_1rm,
)


# ============================================================================
# Linear Progressive Tests
# ============================================================================

def test_linear_progressive_hit_target():
    """Test Linear Progressive: hit rep target → add increment"""
    first_set = Set(weight=100, reps=11)
    rep_target = 11
    increment = 2.5
    last_session = Session(
        date="2025-11-15",
        first_set=Set(weight=97.5, reps=11)
    )
    last_successful_weight = 97.5

    result = apply_linear_progressive_rules(
        first_set=first_set,
        rep_target=rep_target,
        increment=increment,
        last_session=last_session,
        last_successful_weight=last_successful_weight,
    )

    assert result.action == "increase_weight"
    assert result.weight == 102.5  # 100 + 2.5
    assert result.target_reps == 11
    assert "Hit rep target" in result.message


def test_linear_progressive_miss_target():
    """Test Linear Progressive: miss rep target → reactive deload"""
    first_set = Set(weight=100, reps=10)  # Missed target by 1 rep
    rep_target = 11
    increment = 2.5
    last_session = Session(
        date="2025-11-15",
        first_set=Set(weight=97.5, reps=11)
    )
    last_successful_weight = 97.5  # Last weight where target was hit

    result = apply_linear_progressive_rules(
        first_set=first_set,
        rep_target=rep_target,
        increment=increment,
        last_session=last_session,
        last_successful_weight=last_successful_weight,
    )

    assert result.action == "reactive_deload"
    assert result.weight == 97.5  # Deload to last successful
    assert result.target_reps == 11
    assert "Missed target" in result.message or "Deload" in result.message


def test_linear_progressive_exceed_target():
    """Test Linear Progressive: exceed rep target still progresses"""
    first_set = Set(weight=100, reps=13)  # 2 reps over target
    rep_target = 11
    increment = 2.5
    last_session = Session(
        date="2025-11-15",
        first_set=Set(weight=97.5, reps=11)
    )
    last_successful_weight = 97.5

    result = apply_linear_progressive_rules(
        first_set=first_set,
        rep_target=rep_target,
        increment=increment,
        last_session=last_session,
        last_successful_weight=last_successful_weight,
    )

    assert result.action == "increase_weight"
    assert result.weight == 102.5  # Still add increment
    assert "Hit rep target" in result.message


# ============================================================================
# Rep Range Tests
# ============================================================================

def test_rep_range_hit_target():
    """Test Rep Range: hit rep target → add weight"""
    first_set = Set(weight=100, reps=11)
    rep_target = 11
    increment = 2.5
    session_history = [
        Session(date="2025-11-10", first_set=Set(weight=97.5, reps=11)),
        Session(date="2025-11-13", first_set=Set(weight=100, reps=9)),
        Session(date="2025-11-15", first_set=Set(weight=100, reps=10)),
    ]
    current_weight = 100

    result = apply_rep_range_rules(
        first_set=first_set,
        rep_target=rep_target,
        increment=increment,
        session_history=session_history,
        current_weight=current_weight,
    )

    assert result.action == "increase_weight"
    assert result.weight == 102.5  # 100 + 2.5
    assert result.target_reps == 11


def test_rep_range_miss_target_add_reps():
    """Test Rep Range: miss target → try for more reps next session"""
    first_set = Set(weight=100, reps=9)  # Missed target
    rep_target = 11
    increment = 2.5
    session_history = [
        Session(date="2025-11-10", first_set=Set(weight=97.5, reps=11)),
        Session(date="2025-11-13", first_set=Set(weight=100, reps=8)),
    ]
    current_weight = 100

    result = apply_rep_range_rules(
        first_set=first_set,
        rep_target=rep_target,
        increment=increment,
        session_history=session_history,
        current_weight=current_weight,
    )

    assert result.action == "add_reps"
    assert result.weight == 100  # Same weight
    assert result.target_reps == 11
    assert "Build reps" in result.message or "more reps" in result.message


def test_rep_range_regression_triggers_plateau_breaker():
    """Test Rep Range: reps regressed → plateau breaker"""
    first_set = Set(weight=100, reps=8)  # Regressed from 10
    rep_target = 11
    increment = 2.5
    session_history = [
        Session(date="2025-11-10", first_set=Set(weight=100, reps=9)),
        Session(date="2025-11-13", first_set=Set(weight=100, reps=10)),  # Last session: 10 reps
    ]
    current_weight = 100

    result = apply_rep_range_rules(
        first_set=first_set,
        rep_target=rep_target,
        increment=increment,
        session_history=session_history,
        current_weight=current_weight,
    )

    assert result.action == "plateau_breaker"
    assert result.weight > 100  # Increased weight (~10%)
    assert result.target_reps == 5  # Low reps for plateau breaker
    assert "regressed" in result.message.lower() or "Plateau breaker" in result.message


def test_rep_range_plateau_detection():
    """Test Rep Range: 2+ sessions no progress → plateau breaker"""
    first_set = Set(weight=100, reps=9)  # Same as last 2 sessions
    rep_target = 11
    increment = 2.5
    session_history = [
        Session(date="2025-11-10", first_set=Set(weight=100, reps=9)),
        Session(date="2025-11-13", first_set=Set(weight=100, reps=9)),
        Session(date="2025-11-15", first_set=Set(weight=100, reps=9)),  # 3 sessions stuck
    ]
    current_weight = 100

    result = apply_rep_range_rules(
        first_set=first_set,
        rep_target=rep_target,
        increment=increment,
        session_history=session_history,
        current_weight=current_weight,
    )

    assert result.action == "plateau_breaker"
    assert result.weight > 100  # Increased weight
    assert "Plateau" in result.message


# ============================================================================
# Plateau Detection Tests
# ============================================================================

def test_detect_plateau_with_progress():
    """Test plateau detection: progress being made → no plateau"""
    session_history = [
        Session(date="2025-11-10", first_set=Set(weight=100, reps=9)),
        Session(date="2025-11-13", first_set=Set(weight=100, reps=10)),  # Progress!
    ]

    result = detect_plateau(session_history, "rep_range")

    assert result.plateau_detected == False
    assert result.duration_sessions == 0


def test_detect_plateau_no_progress():
    """Test plateau detection: 2+ sessions no progress → plateau"""
    session_history = [
        Session(date="2025-11-10", first_set=Set(weight=100, reps=9)),
        Session(date="2025-11-13", first_set=Set(weight=100, reps=9)),
        Session(date="2025-11-15", first_set=Set(weight=100, reps=9)),
    ]

    result = detect_plateau(session_history, "rep_range")

    assert result.plateau_detected == True
    assert result.duration_sessions >= 2


def test_detect_plateau_weight_progress():
    """Test plateau detection: weight increased → no plateau (even if reps lower)"""
    session_history = [
        Session(date="2025-11-10", first_set=Set(weight=100, reps=11)),
        Session(date="2025-11-13", first_set=Set(weight=102.5, reps=9)),  # Weight increased
    ]

    result = detect_plateau(session_history, "rep_range")

    assert result.plateau_detected == False  # Weight increased = progress


def test_plateau_detection_linear_model():
    """Test plateau detection: doesn't apply to linear model"""
    session_history = [
        Session(date="2025-11-10", first_set=Set(weight=100, reps=9)),
        Session(date="2025-11-13", first_set=Set(weight=100, reps=9)),
    ]

    result = detect_plateau(session_history, "linear")

    assert result.plateau_detected == False  # Linear model doesn't use plateau detection


# ============================================================================
# Regression Detection Tests
# ============================================================================

def test_detect_regression_true():
    """Test regression detection: reps decreased"""
    today_reps = 8
    last_session_reps = 10

    result = detect_regression(today_reps, last_session_reps)

    assert result == True


def test_detect_regression_false():
    """Test regression detection: reps same or increased"""
    today_reps = 10
    last_session_reps = 10

    result = detect_regression(today_reps, last_session_reps)

    assert result == False


# ============================================================================
# Plateau Breaker Tests
# ============================================================================

def test_calculate_plateau_breaker_weight():
    """Test plateau breaker weight calculation: ~10% increase"""
    current_weight = 100

    breaker_weight = calculate_plateau_breaker_weight(current_weight, "compound")

    # Should be ~110kg (10% increase)
    assert 108 <= breaker_weight <= 112
    # Should be rounded to 2.5kg increments
    assert breaker_weight % 2.5 == 0


def test_plateau_breaker_weight_small_load():
    """Test plateau breaker with small weight"""
    current_weight = 20

    breaker_weight = calculate_plateau_breaker_weight(current_weight, "isolation")

    # Should be ~22kg (10% increase)
    assert 21 <= breaker_weight <= 23
    assert breaker_weight % 2.5 == 0


# ============================================================================
# Model Switch Suggestion Tests
# ============================================================================

def test_suggest_model_switch_high_failure_rate():
    """Test model switch: failure rate > 50% → suggest switch"""
    failure_rate = 0.6  # 60% failure rate
    increment = 5.0

    result = suggest_progression_model_switch(failure_rate, increment)

    assert result is not None
    assert result.from_model == "linear"
    assert result.to_model == "rep_range"
    assert "too large" in result.reason.lower()


def test_suggest_model_switch_low_failure_rate():
    """Test model switch: failure rate < 50% → no switch"""
    failure_rate = 0.3  # 30% failure rate
    increment = 2.5

    result = suggest_progression_model_switch(failure_rate, increment)

    assert result is None  # No switch needed


# ============================================================================
# 1RM Calculation Tests
# ============================================================================

def test_calculate_1rm_epley_formula():
    """Test 1RM calculation using Epley formula"""
    weight = 100
    reps = 5

    one_rm = calculate_1rm(weight, reps)

    # 1RM = 100 * (1 + 5/30) = 100 * 1.167 = 116.7
    assert 116 <= one_rm <= 117


def test_calculate_1rm_one_rep():
    """Test 1RM calculation: 1 rep = actual weight"""
    weight = 100
    reps = 1

    one_rm = calculate_1rm(weight, reps)

    assert one_rm == 100  # 1 rep = 1RM


def test_calculate_1rm_high_reps():
    """Test 1RM calculation: high reps"""
    weight = 60
    reps = 12

    one_rm = calculate_1rm(weight, reps)

    # 1RM = 60 * (1 + 12/30) = 60 * 1.4 = 84
    assert 83 <= one_rm <= 85


# ============================================================================
# Integration Tests
# ============================================================================

def test_analyze_exercise_session_linear_success():
    """Test full analysis: Linear Progressive with success"""
    exercise_name = "Bench Press"
    sets_logged = [
        Set(weight=100, reps=11),
        Set(weight=100, reps=8),
        Set(weight=100, reps=7),
    ]
    config = ExerciseConfig(
        progression_model="linear",
        rep_target=11,
        num_sets=3,
        available_increments=[2.5, 5.0],
        selected_increment=2.5,
    )
    session_history = [
        Session(date="2025-11-13", first_set=Set(weight=97.5, reps=11)),
    ]
    current_weight = 100
    last_successful_weight = 97.5

    result = analyze_exercise_session(
        exercise_name=exercise_name,
        sets_logged=sets_logged,
        config=config,
        session_history=session_history,
        current_weight=current_weight,
        last_successful_weight=last_successful_weight,
    )

    assert result.exercise_name == "Bench Press"
    assert result.progression_model == "linear"
    assert result.hit_rep_target == True
    assert result.action_type == "increase_weight"
    assert result.next_weight == 102.5
    assert result.confidence == 1.0  # Deterministic = 100% confidence


def test_analyze_exercise_session_rep_range_build_reps():
    """Test full analysis: Rep Range needing to build reps"""
    exercise_name = "Squat"
    sets_logged = [
        Set(weight=120, reps=9),  # Missed target
        Set(weight=120, reps=7),
        Set(weight=120, reps=6),
    ]
    config = ExerciseConfig(
        progression_model="rep_range",
        rep_target=11,
        num_sets=3,
        available_increments=[2.5, 5.0],
        selected_increment=2.5,
    )
    session_history = [
        Session(date="2025-11-10", first_set=Set(weight=117.5, reps=11)),
        Session(date="2025-11-13", first_set=Set(weight=120, reps=8)),
    ]
    current_weight = 120
    last_successful_weight = 117.5

    result = analyze_exercise_session(
        exercise_name=exercise_name,
        sets_logged=sets_logged,
        config=config,
        session_history=session_history,
        current_weight=current_weight,
        last_successful_weight=last_successful_weight,
    )

    assert result.exercise_name == "Squat"
    assert result.progression_model == "rep_range"
    assert result.hit_rep_target == False
    assert result.action_type == "add_reps"
    assert result.next_weight == 120  # Same weight
    assert result.confidence == 1.0


# ============================================================================
# Run Tests
# ============================================================================

if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
