"""
Training Specialist Algorithm

Deterministic progression algorithms for strength training.
Pure Python implementation - NO AI.

Implements two progression models:
1. Linear Progressive: Hit reps → add weight, miss → reactive deload
2. Rep Range: Hit reps → add weight, miss → add reps

Based on TRAINING_AGENT_SPEC.md
"""

from typing import List, Optional
from ai_agents.shared.models import (
    Set,
    Session,
    ExerciseConfig,
    NextSession,
    NextSessionRecommendation,
    PlateauAnalysis,
    ModelSwitchSuggestion,
)
from ai_agents.training_specialist.tools import (
    detect_plateau,
    detect_regression,
    calculate_plateau_breaker_weight,
    suggest_progression_model_switch,
)


def analyze_exercise_session(
    exercise_name: str,
    sets_logged: List[Set],
    config: ExerciseConfig,
    session_history: List[Session],
    current_weight: float,
    last_successful_weight: float,
) -> NextSessionRecommendation:
    """
    Main analysis function that routes to appropriate progression model.

    Args:
        exercise_name: Name of the exercise
        sets_logged: List of sets from today's workout
        config: Exercise configuration (progression model, rep target, etc.)
        session_history: Recent session history (last 4-8 sessions)
        current_weight: Current working weight
        last_successful_weight: Last weight where rep target was hit

    Returns:
        NextSessionRecommendation with next session prescription
    """
    # Get first set (progression benchmark)
    first_set = sets_logged[0]

    # Check if rep target was hit
    hit_rep_target = first_set.reps >= config.rep_target

    # Route to appropriate progression model
    if config.progression_model == "linear":
        next_session = apply_linear_progressive_rules(
            first_set=first_set,
            rep_target=config.rep_target,
            increment=config.selected_increment,
            last_session=session_history[-1] if session_history else None,
            last_successful_weight=last_successful_weight,
        )
    else:  # rep_range
        next_session = apply_rep_range_rules(
            first_set=first_set,
            rep_target=config.rep_target,
            increment=config.selected_increment,
            session_history=session_history,
            current_weight=current_weight,
        )

    # Check if model switching should be suggested (Linear Progressive only)
    model_switch_suggestion = None
    if config.progression_model == "linear" and len(session_history) >= 3:
        # Calculate failure rate over recent sessions
        failures = 0
        total_sessions = min(len(session_history), 4)  # Look at last 4 sessions

        for session in session_history[-total_sessions:]:
            if session.first_set.reps < config.rep_target:
                failures += 1

        failure_rate = failures / total_sessions

        # Debug logging
        print(f"🔍 Model Switch Check: {exercise_name}")
        print(f"   Session history: {len(session_history)} sessions")
        print(f"   Recent sessions analyzed: {total_sessions}")
        print(f"   Failures: {failures}")
        print(f"   Failure rate: {failure_rate:.1%}")
        print(f"   Rep target: {config.rep_target}")

        # Call suggestion function
        model_switch_suggestion = suggest_progression_model_switch(
            failure_rate=failure_rate,
            increment=config.selected_increment,
        )

        if model_switch_suggestion:
            print(f"   ✅ SUGGESTING SWITCH: {model_switch_suggestion.from_model} → {model_switch_suggestion.to_model}")
            print(f"   Reason: {model_switch_suggestion.reason}")
        else:
            print(f"   ❌ No switch suggested (failure rate not high enough)")

    # Build complete recommendation
    recommendation = NextSessionRecommendation(
        exercise_name=exercise_name,
        progression_model=config.progression_model,
        today_first_set=first_set,
        hit_rep_target=hit_rep_target,
        plateau_detected=next_session.action == "plateau_breaker",
        regression_detected=next_session.action == "reactive_deload",
        reactive_deload_implemented=next_session.action == "reactive_deload",
        next_weight=next_session.weight,
        next_rep_target=next_session.target_reps,
        action_type=next_session.action,
        message=next_session.message,
        reasoning=next_session.reasoning,
        model_switch_suggestion=model_switch_suggestion,
        confidence=1.0,  # Deterministic algorithm = 100% confidence
    )

    return recommendation


def apply_linear_progressive_rules(
    first_set: Set,
    rep_target: int,
    increment: float,
    last_session: Optional[Session],
    last_successful_weight: float,
) -> NextSession:
    """
    Apply Linear Progressive rules.

    Rules:
    - Hit rep target in first set → add increment
    - Miss rep target → reactive deload (return to last successful weight)

    Args:
        first_set: Today's first set
        rep_target: Target reps for progression
        increment: Weight increment (kg)
        last_session: Last session data (if available)
        last_successful_weight: Last weight where rep target was hit

    Returns:
        NextSession with weight, reps, action
    """
    hit_target = first_set.reps >= rep_target

    if hit_target:
        # Success! Add increment for next session
        next_weight = first_set.weight + increment
        return NextSession(
            weight=next_weight,
            target_reps=rep_target,
            action="increase_weight",
            message=f"Hit rep target! Next session: {next_weight}kg x {rep_target} reps",
            reasoning=f"Linear Progressive: Hit {first_set.reps} reps (target {rep_target}). Adding {increment}kg increment."
        )
    else:
        # Failed! Reactive deload
        # Return to last successful weight
        return NextSession(
            weight=last_successful_weight,
            target_reps=rep_target,
            action="reactive_deload",
            message=f"Missed target. Deload to {last_successful_weight}kg x {rep_target} reps",
            reasoning=f"Linear Progressive: Missed rep target ({first_set.reps}/{rep_target}). Implementing reactive deload to last successful weight."
        )


def apply_rep_range_rules(
    first_set: Set,
    rep_target: int,
    increment: float,
    session_history: List[Session],
    current_weight: float,
) -> NextSession:
    """
    Apply Rep Range Progression rules.

    Rules:
    - Hit rep target → add weight
    - Didn't hit rep target → try for more reps next session
    - Plateau (2+ sessions no progress) → plateau breaker
    - Regression (reps decreased) → reactive deload + plateau breaker

    Args:
        first_set: Today's first set
        rep_target: Target reps for progression
        increment: Weight increment (kg)
        session_history: Recent session history
        current_weight: Current working weight

    Returns:
        NextSession with weight, reps, action
    """
    hit_target = first_set.reps >= rep_target

    if hit_target:
        # Success! Add weight for next session
        next_weight = first_set.weight + increment
        return NextSession(
            weight=next_weight,
            target_reps=rep_target,
            action="increase_weight",
            message=f"Hit rep target! Next session: {next_weight}kg x {rep_target} reps",
            reasoning=f"Rep Range: Hit {rep_target} reps. Adding {increment}kg increment."
        )

    # Didn't hit target - check for regression or plateau
    if session_history:
        last_session = session_history[-1]

        # Detect regression (reps decreased at same weight)
        if (last_session.first_set.weight == first_set.weight and
            first_set.reps < last_session.first_set.reps):
            # Regression detected! Implement plateau breaker
            breaker_weight = calculate_plateau_breaker_weight(
                current_weight=first_set.weight,
                exercise_type="compound",  # TODO: Add exercise type to config
            )
            return NextSession(
                weight=breaker_weight,
                target_reps=5,  # Low reps for plateau breaker
                action="plateau_breaker",
                message=f"Reps regressed. Plateau breaker: {breaker_weight}kg x 5 reps",
                reasoning=f"Rep Range: Reps decreased from {last_session.first_set.reps} to {first_set.reps}. Implementing plateau breaker at {breaker_weight}kg."
            )

        # Detect plateau (2+ sessions no progress)
        plateau = detect_plateau(session_history, "rep_range")
        if plateau.plateau_detected:
            # Plateau detected! Implement plateau breaker
            breaker_weight = calculate_plateau_breaker_weight(
                current_weight=first_set.weight,
                exercise_type="compound",  # TODO: Add exercise type to config
            )
            return NextSession(
                weight=breaker_weight,
                target_reps=5,  # Low reps for plateau breaker
                action="plateau_breaker",
                message=f"Plateau detected ({plateau.duration_sessions} sessions). Plateau breaker: {breaker_weight}kg x 5 reps",
                reasoning=f"Rep Range: No progress for {plateau.duration_sessions} sessions. Implementing plateau breaker."
            )

    # Normal case: try to add reps next session
    return NextSession(
        weight=first_set.weight,
        target_reps=rep_target,
        action="add_reps",
        message=f"Build reps: {first_set.weight}kg x {rep_target} reps",
        reasoning=f"Rep Range: Hit {first_set.reps} reps (target {rep_target}). Keep same weight and try for more reps."
    )
