"""
Training Specialist Agent

Event-driven agent that analyzes completed workouts and prescribes next session parameters.

Architecture:
- Deterministic progression algorithms (Linear Progressive & Rep Range)
- Event-driven trigger (post-workout)
- Per-exercise, per-session basis
- No AI - pure Python algorithmic rules

Key Features:
- Linear Progressive: Hit reps → add weight, miss → reactive deload
- Rep Range: Hit reps → add weight, miss → add reps next session
- Plateau detection (2+ sessions no progress)
- Regression detection (reps decreased)
- Plateau breakers (10% increase, return to lower weight)
- Model switching suggestions
"""

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

__all__ = [
    "analyze_exercise_session",
    "apply_linear_progressive_rules",
    "apply_rep_range_rules",
    "detect_plateau",
    "detect_regression",
    "calculate_plateau_breaker_weight",
    "suggest_progression_model_switch",
    "calculate_1rm",
]
