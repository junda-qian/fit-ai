"""
Nutrition Specialist Agent

Proactive weekly nutrition analysis and automatic meal plan adjustments.

Implements deterministic, evidence-based nutrition algorithm:
- Table 1: Optimal deficit by body fat percentage (cutting)
- Table 2: Estimated deficit from weight loss rate
- Table 3: Optimal surplus by training status (bulking)

Key Features:
- 14-day trend analysis to filter daily noise
- Body recomposition detection
- Personalized calorie and macro adjustments
- 100% deterministic (no AI reasoning)
"""

from .algorithm import (
    apply_nutrition_algorithm,
    apply_cutting_algorithm,
    apply_bulking_algorithm,
)

from .tools import (
    estimate_maintenance_calories,
    calculate_macros,
    calculate_optimal_deficit,
    estimate_deficit_from_loss_rate,
    calculate_optimal_surplus,
)

from .trend_analysis import (
    analyze_weight_trend,
    analyze_body_composition_trend,
)

__version__ = "0.1.0"

__all__ = [
    # Core algorithms
    "apply_nutrition_algorithm",
    "apply_cutting_algorithm",
    "apply_bulking_algorithm",
    # Calculation tools
    "estimate_maintenance_calories",
    "calculate_macros",
    "calculate_optimal_deficit",
    "estimate_deficit_from_loss_rate",
    "calculate_optimal_surplus",
    # Trend analysis
    "analyze_weight_trend",
    "analyze_body_composition_trend",
]
