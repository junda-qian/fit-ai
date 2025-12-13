"""
Unit Tests for Nutrition Specialist Agent

Tests deterministic logic for:
- Tables 1-3 calculations
- Cutting algorithm
- Bulking algorithm
- Body recomposition detection
"""

from .tools import (
    calculate_optimal_deficit,
    calculate_optimal_surplus,
    estimate_deficit_from_loss_rate,
    estimate_maintenance_calories,
    calculate_macros
)
from .algorithm import (
    apply_nutrition_algorithm,
    apply_cutting_algorithm,
    apply_bulking_algorithm
)
from ..shared.models import (
    WeightTrend,
    BodyCompositionTrend,
    NutritionSummary,
    WorkoutSummary
)


# ============================================================================
# Table 1 Tests: Optimal Deficit by Body Fat %
# ============================================================================

def test_table1_male_contest_prep():
    """Test Table 1: Male < 8% BF → 5% deficit"""
    assert calculate_optimal_deficit(7, "male") == 5


def test_table1_male_athletic():
    """Test Table 1: Male 8-15% BF → 10% deficit"""
    assert calculate_optimal_deficit(12, "male") == 10


def test_table1_male_average():
    """Test Table 1: Male 15-21% BF → 20% deficit"""
    assert calculate_optimal_deficit(18, "male") == 20


def test_table1_male_overweight():
    """Test Table 1: Male 21-26% BF → 30% deficit"""
    assert calculate_optimal_deficit(24, "male") == 30


def test_table1_male_obese():
    """Test Table 1: Male 26%+ BF → 50% deficit"""
    assert calculate_optimal_deficit(30, "male") == 50


def test_table1_female_contest_prep():
    """Test Table 1: Female < 14% BF → 5% deficit"""
    assert calculate_optimal_deficit(12, "female") == 5


def test_table1_female_athletic():
    """Test Table 1: Female 14-24% BF → 10% deficit"""
    assert calculate_optimal_deficit(20, "female") == 10


def test_table1_female_average():
    """Test Table 1: Female 24-33% BF → 20% deficit"""
    assert calculate_optimal_deficit(28, "female") == 20


# ============================================================================
# Table 2 Tests: Estimated Deficit from Loss Rate
# ============================================================================

def test_table2_maintenance():
    """Test Table 2: < 0.1%/week loss → 0% deficit"""
    assert estimate_deficit_from_loss_rate(0.05) == 0


def test_table2_small_deficit():
    """Test Table 2: 0.1-0.3%/week loss → 10% deficit"""
    assert estimate_deficit_from_loss_rate(0.2) == 10


def test_table2_moderate_deficit():
    """Test Table 2: 0.3-0.7%/week loss → 20% deficit"""
    assert estimate_deficit_from_loss_rate(0.5) == 20


def test_table2_aggressive_deficit():
    """Test Table 2: 0.7-1.1%/week loss → 30% deficit"""
    assert estimate_deficit_from_loss_rate(0.9) == 30


def test_table2_extreme_deficit():
    """Test Table 2: 1.1%+ loss → 50% deficit"""
    assert estimate_deficit_from_loss_rate(1.5) == 50


# ============================================================================
# Table 3 Tests: Optimal Surplus by Training Status
# ============================================================================

def test_table3_novice():
    """Test Table 3: Novice → 5-15% surplus, 0.5-1% gain"""
    result = calculate_optimal_surplus("novice")
    assert result["surplus_pct_min"] == 5
    assert result["surplus_pct_max"] == 15
    assert result["target_weekly_gain_pct_min"] == 0.5
    assert result["target_weekly_gain_pct_max"] == 1.0
    assert result["recommended_surplus_pct"] == 10


def test_table3_intermediate():
    """Test Table 3: Intermediate → 2-7% surplus, 0.2-0.5% gain"""
    result = calculate_optimal_surplus("intermediate")
    assert result["surplus_pct_min"] == 2
    assert result["surplus_pct_max"] == 7
    assert result["recommended_surplus_pct"] == 5


def test_table3_advanced():
    """Test Table 3: Advanced → 1-3% surplus"""
    result = calculate_optimal_surplus("advanced")
    assert result["surplus_pct_min"] == 1
    assert result["surplus_pct_max"] == 3
    assert result["recommended_surplus_pct"] == 2


# ============================================================================
# Maintenance Calorie Estimation Tests
# ============================================================================

def test_estimate_maintenance_plateau():
    """Test: Weight stable → current intake is maintenance"""
    maintenance = estimate_maintenance_calories(2000, 0.05)
    assert maintenance == 2000


def test_estimate_maintenance_losing():
    """Test: Losing 0.7%/week at 2000 cal → maintenance ~2500"""
    maintenance = estimate_maintenance_calories(2000, -0.7)
    # Rough estimate: -0.7% ≈ -20% deficit → maintenance = 2000 / 0.8 = 2500
    assert 2400 <= maintenance <= 2600


def test_estimate_maintenance_gaining():
    """Test: Gaining 0.5%/week at 2500 cal → maintenance ~2400"""
    maintenance = estimate_maintenance_calories(2500, 0.5)
    # Rough estimate: +0.5% ≈ +15% surplus → maintenance = 2500 / 1.15 ≈ 2174
    assert 2100 <= maintenance <= 2300


# ============================================================================
# Macro Calculation Tests
# ============================================================================

def test_calculate_macros_cutting():
    """Test macro calculation for cutting (higher protein)"""
    macros = calculate_macros(2000, 80, "lose_weight")

    # Protein: ~2.2 g/kg × 80kg = 176g
    assert 160 <= macros.protein_g <= 180

    # Fat: ~25% of 2000 cal = 500 cal / 9 = 56g
    assert 50 <= macros.fat_g <= 70

    # Carbs: remainder
    assert macros.carbs_g > 0

    # Total should approximate target calories
    total_cal = macros.total_calories()
    assert 1900 <= total_cal <= 2100


def test_calculate_macros_bulking():
    """Test macro calculation for bulking"""
    macros = calculate_macros(2500, 80, "build_muscle")

    # Protein: ~1.8 g/kg × 80kg = 144g
    assert 135 <= macros.protein_g <= 155

    # All macros should be positive
    assert macros.protein_g > 0
    assert macros.carbs_g > 0
    assert macros.fat_g > 0


# ============================================================================
# Cutting Algorithm Tests
# ============================================================================

def test_cutting_optimal_pace():
    """Test cutting: On track → maintain calories"""
    user_profile = {
        "goal": "lose_weight",
        "sex": "male",
        "body_fat_pct": 20,
        "body_weight_kg": 80
    }

    weight_trend = WeightTrend(
        days_analyzed=14,
        data_points=8,
        starting_weight=79.0,
        current_weight=78.5,
        avg_weight=78.7,
        total_change=-0.5,
        weekly_rate=-0.5,
        weekly_rate_pct=-0.63,  # ~20% deficit (optimal for 20% BF)
        is_plateau=False,
        trend="decreasing",
        sufficient_data=True
    )

    body_comp_trend = BodyCompositionTrend(
        method="skinfolds",
        confidence="high",
        days_analyzed=14,
        data_points=3,
        starting_skinfold_sum_mm=50,
        current_skinfold_sum_mm=48,
        total_change_mm=-2,
        trend="decreasing",
        interpretation="Fat mass decreasing",
        sufficient_data=True
    )

    nutrition_summary = NutritionSummary(
        days_analyzed=14,
        days_logged=12,
        avg_calories=2000,
        avg_protein_g=160,
        compliance_pct=86,
        sufficient_data=True
    )

    workout_summary = WorkoutSummary(
        days_analyzed=14,
        sessions=4,
        sufficient_data=True
    )

    recommendation = apply_nutrition_algorithm(
        user_profile,
        weight_trend,
        body_comp_trend,
        nutrition_summary,
        workout_summary
    )

    # Should maintain calories (on track)
    assert recommendation.adjustment_category == "none"
    assert recommendation.recommended_calories == 2000
    assert "optimal pace" in recommendation.reasoning.lower()


def test_cutting_too_fast():
    """Test cutting: Losing too fast → increase calories"""
    user_profile = {
        "goal": "lose_weight",
        "sex": "male",
        "body_fat_pct": 12,  # Athletic - should only use 10% deficit
        "body_weight_kg": 75
    }

    weight_trend = WeightTrend(
        days_analyzed=14,
        data_points=8,
        weekly_rate_pct=-0.9,  # Losing 0.9%/week = ~30% deficit (too fast!)
        is_plateau=False,
        trend="decreasing",
        sufficient_data=True
    )

    body_comp_trend = BodyCompositionTrend(
        method="skinfolds",
        confidence="high",
        days_analyzed=14,
        data_points=3,
        trend="decreasing",
        interpretation="Fat mass decreasing",
        sufficient_data=True
    )

    nutrition_summary = NutritionSummary(
        days_analyzed=14,
        days_logged=12,
        avg_calories=1800,
        sufficient_data=True
    )

    workout_summary = WorkoutSummary(
        days_analyzed=14,
        sessions=4,
        sufficient_data=True
    )

    recommendation = apply_nutrition_algorithm(
        user_profile,
        weight_trend,
        body_comp_trend,
        nutrition_summary,
        workout_summary
    )

    # Should increase calories (losing too fast for body fat level)
    assert recommendation.adjustment_category == "increase"
    assert recommendation.recommended_calories > 1800
    assert "too fast" in recommendation.reasoning.lower()


def test_body_recomposition_detection():
    """Test: Weight plateau + fat decreasing = body recomp → maintain"""
    user_profile = {
        "goal": "lose_weight",
        "sex": "male",
        "body_fat_pct": 18,
        "body_weight_kg": 78
    }

    weight_trend = WeightTrend(
        days_analyzed=14,
        data_points=8,
        avg_weight=78.5,
        weekly_rate_pct=0.05,  # Basically stable
        is_plateau=True,  # Weight plateau
        trend="stable",
        sufficient_data=True
    )

    body_comp_trend = BodyCompositionTrend(
        method="skinfolds",
        confidence="high",
        days_analyzed=14,
        data_points=3,
        starting_skinfold_sum_mm=50,
        current_skinfold_sum_mm=46,
        total_change_mm=-4,
        trend="decreasing",  # But fat is decreasing!
        interpretation="Fat mass decreasing",
        sufficient_data=True
    )

    nutrition_summary = NutritionSummary(
        days_analyzed=14,
        days_logged=12,
        avg_calories=2200,
        sufficient_data=True
    )

    workout_summary = WorkoutSummary(
        days_analyzed=14,
        sessions=4,
        sufficient_data=True
    )

    recommendation = apply_nutrition_algorithm(
        user_profile,
        weight_trend,
        body_comp_trend,
        nutrition_summary,
        workout_summary
    )

    # Should maintain (body recomposition)
    assert recommendation.adjustment_category == "none"
    assert recommendation.body_composition_status == "recomp"
    assert "recomposition" in recommendation.reasoning.lower()


# ============================================================================
# Bulking Algorithm Tests
# ============================================================================

def test_bulking_no_weight_gain():
    """Test bulking: No weight gain → increase calories"""
    user_profile = {
        "goal": "build_muscle",
        "sex": "male",
        "body_fat_pct": 15,
        "training_status": "intermediate",
        "body_weight_kg": 75
    }

    weight_trend = WeightTrend(
        days_analyzed=14,
        data_points=8,
        avg_weight=75.0,
        weekly_rate_pct=0.05,  # No gain
        is_plateau=True,
        trend="stable",
        sufficient_data=True
    )

    body_comp_trend = BodyCompositionTrend(
        method="skinfolds",
        confidence="high",
        days_analyzed=14,
        data_points=3,
        trend="stable",
        interpretation="Body fat stable",
        sufficient_data=True
    )

    nutrition_summary = NutritionSummary(
        days_analyzed=14,
        days_logged=12,
        avg_calories=2500,
        sufficient_data=True
    )

    workout_summary = WorkoutSummary(
        days_analyzed=14,
        sessions=4,
        strength_progressing=True,
        sufficient_data=True
    )

    recommendation = apply_nutrition_algorithm(
        user_profile,
        weight_trend,
        body_comp_trend,
        nutrition_summary,
        workout_summary
    )

    # Should increase calories (need surplus for muscle growth)
    assert recommendation.adjustment_category == "increase"
    assert recommendation.recommended_calories > 2500
    assert "surplus" in recommendation.reasoning.lower()


def test_bulking_gaining_too_fast():
    """Test bulking: Gaining too fast with fat gain → reduce calories"""
    user_profile = {
        "goal": "build_muscle",
        "sex": "male",
        "body_fat_pct": 15,
        "training_status": "intermediate",  # Target: 0.2-0.5%/week
        "body_weight_kg": 75
    }

    weight_trend = WeightTrend(
        days_analyzed=14,
        data_points=8,
        avg_weight=75.5,
        weekly_rate_pct=0.8,  # Gaining 0.8%/week (too fast!)
        is_plateau=False,
        trend="increasing",
        sufficient_data=True
    )

    body_comp_trend = BodyCompositionTrend(
        method="skinfolds",
        confidence="high",
        days_analyzed=14,
        data_points=3,
        starting_skinfold_sum_mm=45,
        current_skinfold_sum_mm=53,
        total_change_mm=8,  # Fat increasing
        trend="increasing",
        interpretation="Fat mass increasing",
        sufficient_data=True
    )

    nutrition_summary = NutritionSummary(
        days_analyzed=14,
        days_logged=12,
        avg_calories=3000,
        sufficient_data=True
    )

    workout_summary = WorkoutSummary(
        days_analyzed=14,
        sessions=4,
        strength_progressing=True,
        sufficient_data=True
    )

    recommendation = apply_nutrition_algorithm(
        user_profile,
        weight_trend,
        body_comp_trend,
        nutrition_summary,
        workout_summary
    )

    # Should decrease calories (too much fat gain)
    assert recommendation.adjustment_category == "decrease"
    assert recommendation.recommended_calories < 3000
    assert "too fast" in recommendation.reasoning.lower()


# ============================================================================
# Run Tests
# ============================================================================

if __name__ == "__main__":
    print("Running Nutrition Agent Unit Tests...")
    print("\n" + "="*60)
    print("Table 1 Tests (Optimal Deficit by Body Fat %)")
    print("="*60)
    test_table1_male_contest_prep()
    test_table1_male_athletic()
    test_table1_male_average()
    test_table1_male_overweight()
    test_table1_male_obese()
    test_table1_female_contest_prep()
    test_table1_female_athletic()
    test_table1_female_average()
    print("✅ All Table 1 tests passed!")

    print("\n" + "="*60)
    print("Table 2 Tests (Estimated Deficit from Loss Rate)")
    print("="*60)
    test_table2_maintenance()
    test_table2_small_deficit()
    test_table2_moderate_deficit()
    test_table2_aggressive_deficit()
    test_table2_extreme_deficit()
    print("✅ All Table 2 tests passed!")

    print("\n" + "="*60)
    print("Table 3 Tests (Optimal Surplus by Training Status)")
    print("="*60)
    test_table3_novice()
    test_table3_intermediate()
    test_table3_advanced()
    print("✅ All Table 3 tests passed!")

    print("\n" + "="*60)
    print("Maintenance Calorie Estimation Tests")
    print("="*60)
    test_estimate_maintenance_plateau()
    test_estimate_maintenance_losing()
    test_estimate_maintenance_gaining()
    print("✅ All maintenance estimation tests passed!")

    print("\n" + "="*60)
    print("Macro Calculation Tests")
    print("="*60)
    test_calculate_macros_cutting()
    test_calculate_macros_bulking()
    print("✅ All macro calculation tests passed!")

    print("\n" + "="*60)
    print("Cutting Algorithm Tests")
    print("="*60)
    test_cutting_optimal_pace()
    print("  ✅ Optimal pace test passed")
    test_cutting_too_fast()
    print("  ✅ Too fast test passed")
    test_body_recomposition_detection()
    print("  ✅ Body recomposition test passed")
    print("✅ All cutting algorithm tests passed!")

    print("\n" + "="*60)
    print("Bulking Algorithm Tests")
    print("="*60)
    test_bulking_no_weight_gain()
    print("  ✅ No weight gain test passed")
    test_bulking_gaining_too_fast()
    print("  ✅ Gaining too fast test passed")
    print("✅ All bulking algorithm tests passed!")

    print("\n" + "="*60)
    print("🎉 ALL TESTS PASSED!")
    print("="*60)
