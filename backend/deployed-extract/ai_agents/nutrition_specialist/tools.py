"""
Nutrition Calculation Tools

Pure Python functions for energy and macro calculations.
All functions are deterministic - same inputs always produce same outputs.
"""

from typing import Dict, Literal
from ..shared.models import MacroSplit


# ============================================================================
# Energy Calculations
# ============================================================================

def estimate_maintenance_calories(
    current_avg_intake: float,
    weekly_weight_change_pct: float
) -> float:
    """
    Estimate maintenance calories based on current intake and observed weight change.

    Uses real-world data instead of population-based formulas (more accurate).

    Logic:
    - If losing 0.7%/week → roughly 20% deficit
    - If gaining 0.5%/week → roughly 10% surplus
    - Rearrange to find maintenance calories

    Args:
        current_avg_intake: Current average daily calorie intake
        weekly_weight_change_pct: Weekly weight change as % of bodyweight
                                  (negative = loss, positive = gain)

    Returns:
        Estimated maintenance calories

    Example:
        >>> estimate_maintenance_calories(2000, -0.7)
        2500.0  # Losing 0.7%/week at 2000 cal → maintenance ~2500
    """
    # Rough approximation: 1% bodyweight change per week ≈ 30% energy deficit/surplus
    # This is based on 3500 cal ≈ 1 lb of fat (rough heuristic)

    if abs(weekly_weight_change_pct) < 0.1:
        # Weight stable → current intake is maintenance
        return current_avg_intake

    # Estimate deficit/surplus percentage
    # Negative weight change = deficit, positive = surplus
    estimated_deficit_surplus_pct = weekly_weight_change_pct * -30  # Flip sign and scale

    # If eating 2000 cal with -20% deficit, maintenance = 2000 / (1 - 0.20) = 2500
    # If eating 2500 cal with +10% surplus, maintenance = 2500 / (1 + 0.10) = 2273
    if estimated_deficit_surplus_pct > 0:  # Deficit
        maintenance = current_avg_intake / (1 - (estimated_deficit_surplus_pct / 100))
    else:  # Surplus
        maintenance = current_avg_intake / (1 + (abs(estimated_deficit_surplus_pct) / 100))

    return round(maintenance, 0)


# ============================================================================
# Macro Calculations
# ============================================================================

def calculate_macros(
    target_calories: int,
    body_weight_kg: float,
    goal: Literal["lose_weight", "build_muscle", "maintain"],
    protein_g_per_kg: float = None,
    fat_pct: float = None
) -> MacroSplit:
    """
    Calculate macro split from target calories.

    Uses evidence-based protein recommendations:
    - Cutting: 2.0-2.4 g/kg (higher to preserve muscle)
    - Bulking: 1.6-2.0 g/kg
    - Maintenance: 1.6-2.0 g/kg

    Fat: 20-30% of calories (minimum 20% for hormone health)
    Carbs: Remainder

    Args:
        target_calories: Daily calorie target
        body_weight_kg: Current body weight in kg
        goal: Fitness goal
        protein_g_per_kg: Optional custom protein target (g/kg)
        fat_pct: Optional custom fat percentage

    Returns:
        MacroSplit with protein, carbs, and fat in grams

    Example:
        >>> calculate_macros(2000, 80, "lose_weight")
        MacroSplit(protein_g=160, carbs_g=200, fat_g=67)
    """
    # Default protein targets based on goal
    if protein_g_per_kg is None:
        protein_targets = {
            "lose_weight": 2.2,      # Higher to preserve muscle in deficit
            "build_muscle": 1.8,      # Moderate for muscle gain
            "maintain": 1.8           # Moderate for maintenance
        }
        protein_g_per_kg = protein_targets[goal]

    # Default fat percentage based on goal
    if fat_pct is None:
        fat_percentages = {
            "lose_weight": 25,        # Moderate fat for satiety
            "build_muscle": 25,       # Moderate fat
            "maintain": 25            # Moderate fat
        }
        fat_pct = fat_percentages[goal]

    # Calculate protein
    protein_g = round(body_weight_kg * protein_g_per_kg)
    protein_calories = protein_g * 4

    # Calculate fat
    fat_calories = round(target_calories * (fat_pct / 100))
    fat_g = round(fat_calories / 9)

    # Calculate carbs (remainder)
    carb_calories = target_calories - protein_calories - (fat_g * 9)
    carbs_g = round(carb_calories / 4)

    # Ensure all values are non-negative
    protein_g = max(0, protein_g)
    carbs_g = max(0, carbs_g)
    fat_g = max(0, fat_g)

    return MacroSplit(
        protein_g=protein_g,
        carbs_g=carbs_g,
        fat_g=fat_g
    )


# ============================================================================
# Table 1: Optimal Deficit by Body Fat Percentage
# ============================================================================

def calculate_optimal_deficit(
    body_fat_pct: float,
    sex: Literal["male", "female"]
) -> float:
    """
    Calculate optimal calorie deficit percentage based on body fat level.

    Based on Table 1 in Nutrition Agent spec:
    - Leaner individuals: Smaller deficits to preserve muscle
    - Higher body fat: Larger deficits are safe and effective

    Args:
        body_fat_pct: Current body fat percentage
        sex: "male" or "female"

    Returns:
        Optimal deficit percentage (5-50%)

    Table 1: Optimal Deficit by Body Fat %
    ┌─────────────────┬──────────────┬────────────────┬──────────────────┐
    │ Category        │ Male BF%     │ Female BF%     │ Optimal Deficit  │
    ├─────────────────┼──────────────┼────────────────┼──────────────────┤
    │ Contest prep    │ < 8          │ < 14           │ 5%               │
    │ Athletic        │ 8-15         │ 14-24          │ 10%              │
    │ Average         │ 15-21        │ 24-33          │ 20%              │
    │ Overweight      │ 21-26        │ 33-39          │ 30%              │
    │ Obese           │ 26+          │ 39+            │ 50%              │
    └─────────────────┴──────────────┴────────────────┴──────────────────┘

    Example:
        >>> calculate_optimal_deficit(20, "male")
        20  # Average category → 20% deficit
    """
    if sex == "male":
        if body_fat_pct < 8:
            return 5
        elif body_fat_pct < 15:
            return 10
        elif body_fat_pct < 21:
            return 20
        elif body_fat_pct < 26:
            return 30
        else:
            return 50
    else:  # female
        if body_fat_pct < 14:
            return 5
        elif body_fat_pct < 24:
            return 10
        elif body_fat_pct < 33:
            return 20
        elif body_fat_pct < 39:
            return 30
        else:
            return 50


# ============================================================================
# Table 2: Estimated Energy Deficit from Weight Loss Rate
# ============================================================================

def estimate_deficit_from_loss_rate(weekly_loss_pct: float) -> float:
    """
    Estimate energy deficit from observed weight loss rate.

    Based on Table 2 in Nutrition Agent spec.

    Args:
        weekly_loss_pct: Weekly bodyweight loss rate as percentage (positive value)

    Returns:
        Estimated energy deficit percentage

    Table 2: Estimated Energy Deficit from Weight Loss Rate
    ┌──────────────────────────────┬──────────────────────────┐
    │ Weekly Weight Loss (% BW)    │ Estimated Deficit (%)    │
    ├──────────────────────────────┼──────────────────────────┤
    │ < 0.1                        │ 0 (maintenance)          │
    │ 0.1 - 0.3                    │ 10%                      │
    │ 0.3 - 0.7                    │ 20%                      │
    │ 0.7 - 1.1                    │ 30%                      │
    │ 1.1+                         │ 50%                      │
    └──────────────────────────────┴──────────────────────────┘

    Example:
        >>> estimate_deficit_from_loss_rate(0.7)
        20  # Losing 0.7%/week → ~20% deficit
    """
    if weekly_loss_pct < 0.1:
        return 0
    elif weekly_loss_pct <= 0.3:
        return 10
    elif weekly_loss_pct <= 0.7:
        return 20
    elif weekly_loss_pct <= 1.1:
        return 30
    else:
        return 50


# ============================================================================
# Table 3: Optimal Energy Surplus by Training Status
# ============================================================================

def calculate_optimal_surplus(
    training_status: Literal["novice", "intermediate", "advanced"]
) -> Dict[str, float]:
    """
    Calculate optimal calorie surplus and target weight gain rate for bulking.

    Based on Table 3 in Nutrition Agent spec:
    - Novices can build muscle faster → higher surplus
    - Advanced lifters build muscle slowly → smaller surplus to minimize fat gain

    Args:
        training_status: "novice", "intermediate", or "advanced"

    Returns:
        Dictionary with:
        - surplus_pct_min: Minimum surplus percentage
        - surplus_pct_max: Maximum surplus percentage
        - target_weekly_gain_pct_min: Minimum target weekly gain (%)
        - target_weekly_gain_pct_max: Maximum target weekly gain (%)
        - recommended_surplus_pct: Recommended starting point

    Table 3: Optimal Energy Surplus by Training Status
    ┌──────────────────┬────────────────────┬──────────────────────────┐
    │ Training Status  │ Energy Surplus     │ Weekly Weight Gain (%BW) │
    ├──────────────────┼────────────────────┼──────────────────────────┤
    │ Novice           │ 5-15%              │ 0.5-1%                   │
    │ Intermediate     │ 2-7%               │ 0.2-0.5%                 │
    │ Advanced         │ 1-3%               │ Any fat-free gain        │
    └──────────────────┴────────────────────┴──────────────────────────┘

    Example:
        >>> calculate_optimal_surplus("intermediate")
        {
            'surplus_pct_min': 2,
            'surplus_pct_max': 7,
            'target_weekly_gain_pct_min': 0.2,
            'target_weekly_gain_pct_max': 0.5,
            'recommended_surplus_pct': 5
        }
    """
    surplus_table = {
        "novice": {
            "surplus_pct_min": 5,
            "surplus_pct_max": 15,
            "target_weekly_gain_pct_min": 0.5,
            "target_weekly_gain_pct_max": 1.0,
            "recommended_surplus_pct": 10
        },
        "intermediate": {
            "surplus_pct_min": 2,
            "surplus_pct_max": 7,
            "target_weekly_gain_pct_min": 0.2,
            "target_weekly_gain_pct_max": 0.5,
            "recommended_surplus_pct": 5
        },
        "advanced": {
            "surplus_pct_min": 1,
            "surplus_pct_max": 3,
            "target_weekly_gain_pct_min": 0.1,
            "target_weekly_gain_pct_max": 0.3,
            "recommended_surplus_pct": 2
        }
    }

    return surplus_table[training_status]


# ============================================================================
# Exports
# ============================================================================

__all__ = [
    "estimate_maintenance_calories",
    "calculate_macros",
    "calculate_optimal_deficit",
    "estimate_deficit_from_loss_rate",
    "calculate_optimal_surplus",
]
