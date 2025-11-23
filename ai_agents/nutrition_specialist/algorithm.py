"""
Nutrition Algorithm Implementation

Deterministic nutrition algorithm implementing Tables 1-3 from spec.
NO AI reasoning - pure Python if/else logic.

Based on NUTRITION_AGENT_SPEC.md
"""

from typing import Dict
from ..shared.models import (
    NutritionRecommendation,
    WeightTrend,
    BodyCompositionTrend,
    NutritionSummary,
    TrainingProgressSummary,
    AnalysisInput
)
from .tools import (
    estimate_maintenance_calories,
    calculate_optimal_deficit,
    calculate_optimal_surplus,
    estimate_deficit_from_loss_rate,
    calculate_macros
)


# ============================================================================
# Main Nutrition Algorithm
# ============================================================================

def apply_nutrition_algorithm(
    user_profile: Dict,
    weight_trend: WeightTrend,
    body_comp_trend: BodyCompositionTrend,
    nutrition_summary: NutritionSummary,
    training_summary: TrainingProgressSummary
) -> NutritionRecommendation:
    """
    Apply evidence-based nutrition algorithm using pure Python.
    Implements Tables 1-3 as deterministic if/else logic.

    NO AI is used in this function.

    Args:
        user_profile: User profile data (goal, sex, body_fat_pct, etc.)
        weight_trend: Weight trend analysis
        body_comp_trend: Body composition trend analysis
        nutrition_summary: Nutrition log summary
        training_summary: Training progress summary published by Training Agent

    Returns:
        NutritionRecommendation with calorie/macro adjustments and reasoning

    Algorithm:
    1. Estimate maintenance calories from current intake + weight change
    2. Calculate optimal deficit/surplus from tables
    3. Detect body recomposition
    4. Apply cutting or bulking algorithm based on goal
    """
    # 1. Estimate maintenance calories (pure math)
    maintenance = estimate_maintenance_calories(
        nutrition_summary.avg_calories or 0,
        weight_trend.weekly_rate_pct
    )

    # 2. Calculate optimal deficit/surplus (lookup Table 1 or Table 3)
    goal = user_profile.get("goal", "maintain")

    if goal == "lose_weight":
        optimal_deficit_pct = calculate_optimal_deficit(
            user_profile.get("body_fat_pct", 20),
            user_profile.get("sex", "male")
        )
    elif goal == "build_muscle":
        surplus_info = calculate_optimal_surplus(
            user_profile.get("training_status", "novice")
        )
        optimal_surplus_pct = surplus_info["recommended_surplus_pct"]
    else:  # maintain
        # Maintenance - no deficit or surplus
        return NutritionRecommendation(
            current_calorie_average=int(nutrition_summary.avg_calories or 0),
            current_body_fat_pct=user_profile.get("body_fat_pct"),
            observed_weekly_weight_change_pct=weight_trend.weekly_rate_pct,
            recommended_calories=int(nutrition_summary.avg_calories or maintenance),
            recommended_deficit_or_surplus_pct=0,
            optimal_deficit_or_surplus_pct=0,
            recommended_macros=calculate_macros(
                int(maintenance),
                user_profile.get("body_weight_kg", 70),
                "maintain"
            ),
            adjustment_category="none",
            reasoning="Maintaining current weight and body composition. No changes needed.",
            body_composition_status="maintenance",
            confidence=1.0
        )

    # 3. Detect body recomposition (pure logic)
    is_plateau = weight_trend.is_plateau
    body_fat_decreasing = body_comp_trend.trend == "decreasing"

    if is_plateau and body_fat_decreasing and goal == "lose_weight":
        # Body recomposition - no adjustment needed
        return NutritionRecommendation(
            current_calorie_average=int(nutrition_summary.avg_calories or 0),
            current_body_fat_pct=user_profile.get("body_fat_pct"),
            observed_weekly_weight_change_pct=weight_trend.weekly_rate_pct,
            recommended_calories=int(nutrition_summary.avg_calories or 0),
            recommended_deficit_or_surplus_pct=0,
            optimal_deficit_or_surplus_pct=-optimal_deficit_pct,
            recommended_macros=calculate_macros(
                int(nutrition_summary.avg_calories or 0),
                user_profile.get("body_weight_kg", 70),
                goal
            ),
            adjustment_category="none",
            reasoning=f"Body recomposition detected: weight stable at {weight_trend.avg_weight:.1f}kg but body fat decreasing ({body_comp_trend.interpretation}). This is excellent progress - you're losing fat while gaining muscle! Maintain current calories.",
            body_composition_status="recomp",
            confidence=1.0
        )

    # 4. Apply cutting or bulking algorithm
    if goal == "lose_weight":
        return apply_cutting_algorithm(
            user_profile,
            weight_trend,
            body_comp_trend,
            nutrition_summary,
            maintenance,
            optimal_deficit_pct
        )
    else:  # build_muscle
        return apply_bulking_algorithm(
            user_profile,
            weight_trend,
            body_comp_trend,
            nutrition_summary,
            training_summary,
            maintenance,
            optimal_surplus_pct
        )


# ============================================================================
# Cutting Algorithm (Tables 1 & 2)
# ============================================================================

def apply_cutting_algorithm(
    user_profile: Dict,
    weight_trend: WeightTrend,
    body_comp_trend: BodyCompositionTrend,
    nutrition_summary: NutritionSummary,
    maintenance: float,
    optimal_deficit_pct: float
) -> NutritionRecommendation:
    """
    Implement cutting algorithm from Tables 1 & 2.
    Pure Python - no AI.

    Logic:
    1. Calculate observed weekly loss rate
    2. Estimate current deficit from Table 2
    3. Compare to optimal deficit from Table 1
    4. Adjust calories accordingly
    """
    weekly_loss_pct = abs(weight_trend.weekly_rate_pct)

    # Map loss rate to estimated deficit (Table 2)
    estimated_deficit_pct = estimate_deficit_from_loss_rate(weekly_loss_pct)

    current_calories = int(nutrition_summary.avg_calories or 0)
    body_fat_pct = user_profile.get("body_fat_pct", 20)

    # Compare estimated vs optimal
    if abs(estimated_deficit_pct - optimal_deficit_pct) <= 5:
        # On track - maintain current calories
        adjustment = "none"
        recommended_calories = current_calories
        reasoning = (
            f"Weight loss proceeding at optimal pace ({weekly_loss_pct:.1f}%/week). "
            f"Current deficit (~{estimated_deficit_pct}%) matches optimal ({optimal_deficit_pct}% for {body_fat_pct:.1f}% body fat). "
            f"Continue with {recommended_calories} cal/day."
        )

    elif estimated_deficit_pct > optimal_deficit_pct:
        # Losing too fast - increase calories
        adjustment = "increase"
        recommended_calories = int(maintenance * (1 - optimal_deficit_pct / 100))
        reasoning = (
            f"Weight loss too fast ({weekly_loss_pct:.1f}%/week = ~{estimated_deficit_pct}% deficit). "
            f"Risk of muscle loss at your body fat level ({body_fat_pct:.1f}%). "
            f"Increase to {recommended_calories} cal/day ({optimal_deficit_pct}% deficit) to preserve muscle while continuing fat loss."
        )

    else:
        # Losing too slow - decrease calories
        adjustment = "decrease"
        recommended_calories = int(maintenance * (1 - optimal_deficit_pct / 100))
        reasoning = (
            f"Weight loss too slow ({weekly_loss_pct:.1f}%/week = ~{estimated_deficit_pct}% deficit). "
            f"At {body_fat_pct:.1f}% body fat, you can safely increase deficit to {optimal_deficit_pct}%. "
            f"Decrease to {recommended_calories} cal/day for more effective fat loss."
        )

    return NutritionRecommendation(
        current_calorie_average=current_calories,
        current_body_fat_pct=body_fat_pct,
        observed_weekly_weight_change_pct=weight_trend.weekly_rate_pct,
        recommended_calories=recommended_calories,
        recommended_deficit_or_surplus_pct=-optimal_deficit_pct,  # Negative for deficit
        optimal_deficit_or_surplus_pct=-optimal_deficit_pct,
        recommended_macros=calculate_macros(
            recommended_calories,
            user_profile.get("body_weight_kg", 70),
            "lose_weight"
        ),
        adjustment_category=adjustment,
        reasoning=reasoning,
        body_composition_status="fat_loss",
        confidence=1.0
    )


# ============================================================================
# Bulking Algorithm (Table 3)
# ============================================================================

def apply_bulking_algorithm(
    user_profile: Dict,
    weight_trend: WeightTrend,
    body_comp_trend: BodyCompositionTrend,
    nutrition_summary: NutritionSummary,
    training_summary: TrainingProgressSummary,
    maintenance: float,
    optimal_surplus_pct: float
) -> NutritionRecommendation:
    """
    Implement bulking algorithm from Table 3.
    Pure Python - no AI.

    Logic:
    1. Get target gain rate from Table 3
    2. Compare observed vs target gain rate
    3. Consider body fat trend + strength progression from Training Agent
    4. Adjust calories accordingly
    """
    weekly_gain_pct = weight_trend.weekly_rate_pct  # Positive if gaining
    body_fat_trend_direction = body_comp_trend.trend

    # Use Training Agent's expert assessment instead of calculating ourselves
    strength_progressing = training_summary.overall_strength_trend == "improving"

    # Get target gain rate from Table 3
    surplus_info = calculate_optimal_surplus(user_profile.get("training_status", "novice"))
    target_gain_min = surplus_info["target_weekly_gain_pct_min"]
    target_gain_max = surplus_info["target_weekly_gain_pct_max"]

    current_calories = int(nutrition_summary.avg_calories or 0)

    # Scenario 1: No weight gain (plateau)
    if abs(weekly_gain_pct) < 0.1:
        adjustment = "increase"
        recommended_calories = int(maintenance * (1 + optimal_surplus_pct / 100))
        reasoning = (
            f"No weight gain detected (averaging {weight_trend.avg_weight:.1f}kg). "
            f"Need calorie surplus for muscle growth. "
            f"Increase to {recommended_calories} cal ({optimal_surplus_pct}% surplus) to support muscle building."
        )

    # Scenario 2: Weight gain above expected rate
    elif weekly_gain_pct > target_gain_max:
        if body_fat_trend_direction == "stable" and strength_progressing:
            # Gaining muscle efficiently - maintain
            adjustment = "none"
            recommended_calories = current_calories
            reasoning = (
                f"Gaining weight ({weekly_gain_pct:.1f}%/week) faster than target ({target_gain_max}%/week), "
                f"BUT body fat is stable and strength is increasing. This indicates efficient muscle gain. "
                f"Maintain {recommended_calories} cal/day."
            )
        else:
            # Gaining too much fat - reduce calories
            adjustment = "decrease"
            recommended_calories = int(maintenance * (1 + optimal_surplus_pct / 100))
            reasoning = (
                f"Weight gain too fast ({weekly_gain_pct:.1f}%/week vs target {target_gain_max}%/week) "
                f"with body fat increasing. Too much fat gain relative to muscle. "
                f"Reduce to {recommended_calories} cal ({optimal_surplus_pct}% surplus) to optimize muscle-to-fat ratio."
            )

    # Scenario 3: Weight gain within expected rate
    elif target_gain_min <= weekly_gain_pct <= target_gain_max:
        if body_fat_trend_direction == "stable" and strength_progressing:
            # Good progress, room for more
            adjustment = "increase"
            recommended_calories = int(current_calories * 1.05)  # +5%
            reasoning = (
                f"Gaining at optimal rate ({weekly_gain_pct:.1f}%/week) with stable body fat and strength progress. "
                f"Room to push harder. Increase to {recommended_calories} cal (+5%) for more muscle gain."
            )

        elif body_fat_trend_direction == "increasing" and strength_progressing:
            # Check magnitude of fat gain
            if body_comp_trend.total_change_mm and body_comp_trend.total_change_mm > 5:
                # Significant fat gain
                adjustment = "decrease"
                recommended_calories = int(maintenance * (1 + optimal_surplus_pct / 100))
                reasoning = (
                    f"Body fat increasing significantly (+{body_comp_trend.total_change_mm:.1f}mm skinfolds). "
                    f"While strength is progressing, reduce surplus to minimize fat gain. "
                    f"Decrease to {recommended_calories} cal ({optimal_surplus_pct}% surplus)."
                )
            else:
                # Minor fat gain is acceptable
                adjustment = "none"
                recommended_calories = current_calories
                reasoning = (
                    f"Gaining weight ({weekly_gain_pct:.1f}%/week) with minor fat gain and strength progress. "
                    f"Some fat gain during bulk is normal. Maintain {recommended_calories} cal/day."
                )

        elif body_fat_trend_direction == "increasing" and not strength_progressing:
            # Gaining fat without strength - problem
            adjustment = "decrease"
            recommended_calories = int(maintenance * (1 + (optimal_surplus_pct / 2) / 100))  # Half surplus
            reasoning = (
                f"Gaining fat without strength progress. Training stimulus may be insufficient. "
                f"Reduce to {recommended_calories} cal (smaller surplus). "
                f"Consider reviewing training program."
            )
            # Add warning
            warnings = ["Training may need adjustment - gaining fat without strength gains"]

        else:
            # Default: maintain current
            adjustment = "none"
            recommended_calories = current_calories
            reasoning = f"Gaining at optimal rate ({weekly_gain_pct:.1f}%/week). Maintain {recommended_calories} cal/day."

    # Scenario 4: Gaining slower than target
    else:
        adjustment = "increase"
        recommended_calories = int(maintenance * (1 + optimal_surplus_pct / 100))
        reasoning = (
            f"Weight gain slower than target ({weekly_gain_pct:.1f}%/week vs {target_gain_min}%/week). "
            f"Increase to {recommended_calories} cal ({optimal_surplus_pct}% surplus) for muscle growth."
        )

    return NutritionRecommendation(
        current_calorie_average=current_calories,
        current_body_fat_pct=user_profile.get("body_fat_pct"),
        observed_weekly_weight_change_pct=weekly_gain_pct,
        recommended_calories=recommended_calories,
        recommended_deficit_or_surplus_pct=optimal_surplus_pct,  # Positive for surplus
        optimal_deficit_or_surplus_pct=optimal_surplus_pct,
        recommended_macros=calculate_macros(
            recommended_calories,
            user_profile.get("body_weight_kg", 70),
            "build_muscle"
        ),
        adjustment_category=adjustment,
        reasoning=reasoning,
        body_composition_status="muscle_gain",
        confidence=1.0,
        warnings=warnings if 'warnings' in locals() else []
    )


# ============================================================================
# Exports
# ============================================================================

__all__ = [
    "apply_nutrition_algorithm",
    "apply_cutting_algorithm",
    "apply_bulking_algorithm",
]
