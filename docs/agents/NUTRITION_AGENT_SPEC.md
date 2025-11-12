# Nutrition Specialist Agent Specification

## Overview

The Nutrition Specialist Agent is a **proactive, weekly-scheduled AI agent** that monitors user progress and automatically adjusts nutrition plans based on evidence-based algorithms.

**Purpose**: Analyze nutrition data weekly and provide evidence-based calorie/macro adjustments

**Trigger**: EventBridge cron (every Monday 6 AM UTC)

**Key Design Principle**:
> This agent operates independently - it gathers data, calculates trends, makes decisions, and stores results all in one Lambda function. No orchestrator needed.

---

## Why Weekly?

- Body weight trends require 14+ days to filter out daily fluctuations (water retention, sodium, hormones)
- Body composition changes are gradual (2+ weeks minimum to detect real fat/muscle changes)
- Nutrition adjustments should be conservative to avoid yo-yo dieting
- Weekly check-ins match real-world coaching cadence

---

## Weekly Analysis Flow

```
┌─────────────────────────────────────────────────────┐
│     EventBridge Scheduler (Every Monday 6 AM)        │
└────────────────────┬────────────────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────────────────┐
│         Nutrition Specialist Agent                   │
│  FOR EACH ACTIVE USER:                              │
│  1. Pull last 14 days of data                       │
│      - Weight logs                                  │
│      - Body composition logs (skinfolds/waist/BF%)  │
│      - Nutrition logs                               │
│      - Workout logs (for bulk assessment)           │
│  2. Calculate trends (deterministic - no AI)        │
│      - Weight trend (weekly rate %)                 │
│      - Body composition trend                       │
│      - Average calorie intake                       │
│  3. Apply nutrition algorithm (AI reasoning)        │
│      - Estimate maintenance calories                │
│      - Calculate optimal deficit/surplus            │
│      - Detect body recomposition                    │
│      - Make calorie/macro recommendations           │
│  4. Store weekly analysis                           │
│  5. Update nutrition plan (if needed)               │
└────────────────────┬────────────────────────────────┘
                     │
                     ▼
              ┌─────────────────┐
              │ weekly_analyses │
              │ active_plans    │
              │   (nutrition)   │
              └─────────────────┘
```

---

## Input Context

The agent gathers all data itself (no external orchestrator).

**User Profile Fields Required:**
See [User Profile Schema](../USER_PROFILE_SCHEMA.md) for complete specification.

Required fields:
- `goal`: "lose_weight", "build_muscle", "maintain"
- `sex`: "male" or "female" (for Table 1 deficit calculation)
- `training_status`: "novice", "intermediate", "advanced" (for Table 3 surplus calculation)
- `body_fat_pct`: Current body fat percentage (for Table 1)
- `is_active`: Filter for weekly analysis

### Input Data Structure

```python
{
    "user_profile": {
        "goal": "lose_weight|build_muscle|maintain",
        "sex": "male|female",
        "body_fat_pct": 20.5,
        "training_status": "novice|intermediate|advanced"
    },
    "weight_trend": {
        "starting_weight": 78.5,
        "current_weight": 78.4,
        "avg_weight": 78.5,
        "weekly_rate_kg": -0.07,
        "weekly_rate_pct": 0.09,  # % of bodyweight per week
        "is_plateau": false
    },
    "body_comp_trend": {
        "method": "skinfolds",  # "skinfolds", "waist", "body_fat_pct", "none"
        "confidence": "high",    # "high", "medium", "low", "none"
        "starting_sum": 50,      # mm (if skinfolds)
        "current_sum": 48,
        "change_mm": -2,
        "trend": "decreasing"    # "increasing", "stable", "decreasing"
    },
    "nutrition_summary": {
        "avg_calories": 2180,
        "avg_protein_g": 160,
        "days_logged": 12,
        "compliance_pct": 86
    },
    "workout_summary": {
        "sessions": 4,
        "strength_trends": {...}
    }
}
```

### Data Quality Requirements

```python
# Minimum data requirements for meaningful analysis
min_weight_logs = 5                     # Need 5+ logs in 14 days
min_body_composition_logs = 2           # Need 2+ measurements in 14 days
min_workout_logs = 2                    # Need 2+ workouts in 14 days
min_nutrition_logs = 10                 # Need 10+ days of nutrition tracking

# If minimum data not met, notify user to improve tracking consistency
```

---

## Implementation Approach: Pure Python (Deterministic)

### Decision: No AI Reasoning in Nutrition Agent

The Nutrition Specialist uses **pure Python implementation** of the evidence-based algorithms (Tables 1-3). **AI is NOT used for decision-making** in this agent.

**Why Deterministic?**
- ✅ **100% Reliable** - No hallucinations or unpredictable behavior
- ✅ **Fast** - No API calls for core decisions (<100ms per user)
- ✅ **Cost-Efficient** - $0 AI cost (vs $0.03-0.05/user with AI reasoning)
- ✅ **Testable** - Exact logic is traceable and unit-testable
- ✅ **Explainable** - Clear reasoning: "Table 1 says 20% deficit for your body fat level"
- ✅ **Predictable** - Same inputs always produce same outputs

**Where AI IS Used:**
User-facing communication is handled by the **Communication Specialist Agent** (separate agent), which translates technical recommendations into personalized, motivating messages.

### Core Algorithm Implementation

```python
def apply_nutrition_algorithm(user: dict, data: dict) -> NutritionRecommendation:
    """
    Apply evidence-based nutrition algorithm using pure Python.
    Implements Tables 1-3 as deterministic if/else logic.

    NO AI is used in this function.
    """

    # 1. Estimate maintenance calories (pure math)
    maintenance = estimate_maintenance_calories(
        data["nutrition_summary"]["avg_calories"],
        data["weight_trend"]["weekly_rate_pct"]
    )

    # 2. Calculate optimal deficit/surplus (lookup Table 1 or Table 3)
    if user["goal"] == "lose_weight":
        optimal_deficit_pct = calculate_optimal_deficit(
            data["user_profile"]["body_fat_pct"],
            data["user_profile"]["sex"]
        )
    else:
        surplus_info = calculate_optimal_surplus(
            data["user_profile"]["training_status"]
        )
        optimal_surplus_pct = surplus_info["recommended_surplus_pct"]

    # 3. Detect body recomposition (pure logic)
    is_plateau = data["weight_trend"]["is_plateau"]
    body_fat_decreasing = data["body_comp_trend"]["trend"] == "decreasing"

    if is_plateau and body_fat_decreasing:
        # Body recomposition - no adjustment needed
        return NutritionRecommendation(
            current_calorie_average=data["nutrition_summary"]["avg_calories"],
            recommended_calories=data["nutrition_summary"]["avg_calories"],
            adjustment_category="none",
            reasoning="Body recomposition detected: weight stable but body fat decreasing.",
            body_composition_status="recomp",
            confidence=1.0
        )
    elif user["goal"] == "lose_weight":
        # Apply cutting algorithm (Tables 1 & 2)
        return apply_cutting_algorithm(user, data, maintenance, optimal_deficit_pct)
    else:
        # Apply bulking algorithm (Table 3)
        return apply_bulking_algorithm(user, data, maintenance, optimal_surplus_pct)


def apply_cutting_algorithm(
    user: dict,
    data: dict,
    maintenance: float,
    optimal_deficit_pct: float
) -> NutritionRecommendation:
    """
    Implement cutting algorithm from Tables 1 & 2.
    Pure Python - no AI.
    """
    weekly_loss_pct = abs(data["weight_trend"]["weekly_rate_pct"])

    # Map loss rate to estimated deficit (Table 2)
    if weekly_loss_pct < 0.1:
        estimated_deficit_pct = 0  # Maintenance
    elif weekly_loss_pct <= 0.3:
        estimated_deficit_pct = 10
    elif weekly_loss_pct <= 0.7:
        estimated_deficit_pct = 20
    elif weekly_loss_pct <= 1.1:
        estimated_deficit_pct = 30
    else:
        estimated_deficit_pct = 50

    # Compare estimated vs optimal
    if abs(estimated_deficit_pct - optimal_deficit_pct) <= 5:
        # On track
        adjustment = "none"
        recommended_calories = data["nutrition_summary"]["avg_calories"]
        reasoning = f"Weight loss proceeding at optimal pace ({weekly_loss_pct:.1f}%/week)."

    elif estimated_deficit_pct > optimal_deficit_pct:
        # Losing too fast
        adjustment = "increase"
        recommended_calories = maintenance * (1 - optimal_deficit_pct / 100)
        reasoning = f"Weight loss too fast ({weekly_loss_pct:.1f}%/week). Increase to {recommended_calories:.0f} cal ({optimal_deficit_pct}% deficit)."

    else:
        # Losing too slow
        adjustment = "decrease"
        recommended_calories = maintenance * (1 - optimal_deficit_pct / 100)
        reasoning = f"Weight loss too slow ({weekly_loss_pct:.1f}%/week). Decrease to {recommended_calories:.0f} cal ({optimal_deficit_pct}% deficit)."

    return NutritionRecommendation(
        current_calorie_average=data["nutrition_summary"]["avg_calories"],
        current_body_fat_pct=data["user_profile"]["body_fat_pct"],
        observed_weekly_weight_change_pct=data["weight_trend"]["weekly_rate_pct"],
        recommended_calories=int(recommended_calories),
        recommended_deficit_or_surplus_pct=-optimal_deficit_pct,
        optimal_deficit_or_surplus_pct=-optimal_deficit_pct,
        recommended_macros=calculate_macros(recommended_calories, user),
        adjustment_category=adjustment,
        reasoning=reasoning,
        body_composition_status="fat_loss",
        confidence=1.0
    )


def apply_bulking_algorithm(
    user: dict,
    data: dict,
    maintenance: float,
    optimal_surplus_pct: float
) -> NutritionRecommendation:
    """
    Implement bulking algorithm from Table 3.
    Pure Python - no AI.
    """
    weekly_gain_pct = data["weight_trend"]["weekly_rate_pct"]  # Positive if gaining
    body_fat_trend = data["body_comp_trend"]["trend"]  # "increasing", "stable", "decreasing"
    strength_progressing = data.get("workout_summary", {}).get("strength_progressing", True)

    # Get target gain rate from Table 3
    surplus_info = calculate_optimal_surplus(data["user_profile"]["training_status"])
    target_gain_min = surplus_info["target_weekly_gain_pct_min"]
    target_gain_max = surplus_info["target_weekly_gain_pct_max"]

    # Scenario 1: No weight gain (plateau)
    if abs(weekly_gain_pct) < 0.1:
        # Not gaining weight - need to add surplus
        adjustment = "increase"
        recommended_calories = maintenance * (1 + optimal_surplus_pct / 100)
        reasoning = f"No weight gain detected. Increase to {recommended_calories:.0f} cal ({optimal_surplus_pct}% surplus) to support muscle growth."

    # Scenario 2: Weight gain above expected rate
    elif weekly_gain_pct > target_gain_max:
        if body_fat_trend == "stable" and strength_progressing:
            # Gaining muscle efficiently - maintain
            adjustment = "none"
            recommended_calories = data["nutrition_summary"]["avg_calories"]
            reasoning = f"Gaining weight ({weekly_gain_pct:.1f}%/week) with stable body fat and strength progress. Maintain {recommended_calories} cal."
        else:
            # Gaining too much fat - reduce calories
            adjustment = "decrease"
            recommended_calories = maintenance * (1 + optimal_surplus_pct / 100)
            reasoning = f"Weight gain too fast ({weekly_gain_pct:.1f}%/week) with body fat increasing. Reduce to {recommended_calories:.0f} cal ({optimal_surplus_pct}% surplus)."

    # Scenario 3: Weight gain within expected rate
    else:  # target_gain_min <= weekly_gain_pct <= target_gain_max
        if body_fat_trend == "stable" and strength_progressing:
            # Good progress, room for more
            adjustment = "increase"
            recommended_calories = data["nutrition_summary"]["avg_calories"] * 1.05
            reasoning = f"Gaining at optimal rate ({weekly_gain_pct:.1f}%/week) with stable body fat. Increase to {recommended_calories:.0f} cal for more muscle gain."

        elif body_fat_trend == "increasing" and strength_progressing:
            # Some fat gain acceptable, but watch it
            if data["body_comp_trend"].get("total_change_mm", 0) > 5:  # Significant fat gain
                adjustment = "decrease"
                recommended_calories = maintenance * (1 + optimal_surplus_pct / 100)
                reasoning = f"Body fat increasing significantly. Reduce to {recommended_calories:.0f} cal ({optimal_surplus_pct}% surplus) while maintaining strength gains."
            else:
                # Minor fat gain is acceptable during bulk
                adjustment = "none"
                recommended_calories = data["nutrition_summary"]["avg_calories"]
                reasoning = f"Gaining weight ({weekly_gain_pct:.1f}%/week) with minor fat gain and strength progress. Maintain {recommended_calories} cal."

        elif body_fat_trend == "increasing" and not strength_progressing:
            # Gaining fat without strength - problem
            adjustment = "decrease"
            recommended_calories = maintenance * (1 + (optimal_surplus_pct / 2) / 100)  # Smaller surplus
            reasoning = f"Gaining fat without strength progress. Reduce to {recommended_calories:.0f} cal. Training may need adjustment."

        else:
            # Default: maintain current
            adjustment = "none"
            recommended_calories = data["nutrition_summary"]["avg_calories"]
            reasoning = f"Gaining at optimal rate ({weekly_gain_pct:.1f}%/week). Maintain {recommended_calories} cal."

    return NutritionRecommendation(
        current_calorie_average=data["nutrition_summary"]["avg_calories"],
        current_body_fat_pct=data["user_profile"]["body_fat_pct"],
        observed_weekly_weight_change_pct=data["weight_trend"]["weekly_rate_pct"],
        recommended_calories=int(recommended_calories),
        recommended_deficit_or_surplus_pct=optimal_surplus_pct,
        optimal_deficit_or_surplus_pct=optimal_surplus_pct,
        recommended_macros=calculate_macros(recommended_calories, user),
        adjustment_category=adjustment,
        reasoning=reasoning,
        body_composition_status="muscle_gain",
        confidence=1.0
    )
```

### Testing Strategy

**Unit Tests (Deterministic):**
```python
def test_cutting_algorithm_optimal_pace():
    """Test that algorithm maintains calories when on track"""
    user = {"goal": "lose_weight", "sex": "male"}
    data = {
        "user_profile": {"body_fat_pct": 20},
        "weight_trend": {"weekly_rate_pct": -0.7, "is_plateau": False},
        "nutrition_summary": {"avg_calories": 2000},
        "body_comp_trend": {"trend": "decreasing"}
    }

    recommendation = apply_nutrition_algorithm(user, data)

    assert recommendation.adjustment_category == "none"
    assert recommendation.recommended_calories == 2000
    assert "optimal pace" in recommendation.reasoning.lower()


def test_body_recomposition_detection():
    """Test that body recomp is properly detected"""
    user = {"goal": "lose_weight", "sex": "male"}
    data = {
        "user_profile": {"body_fat_pct": 18},
        "weight_trend": {"weekly_rate_pct": 0.05, "is_plateau": True},
        "nutrition_summary": {"avg_calories": 2200},
        "body_comp_trend": {"trend": "decreasing"}
    }

    recommendation = apply_nutrition_algorithm(user, data)

    assert recommendation.adjustment_category == "none"
    assert recommendation.body_composition_status == "recomp"
    assert "body recomposition" in recommendation.reasoning.lower()


def test_bulking_algorithm_plateau():
    """Test bulking when not gaining weight"""
    user = {"goal": "build_muscle", "sex": "male"}
    data = {
        "user_profile": {"body_fat_pct": 15, "training_status": "intermediate"},
        "weight_trend": {"weekly_rate_pct": 0.05, "is_plateau": True},
        "nutrition_summary": {"avg_calories": 2500},
        "body_comp_trend": {"trend": "stable"},
        "workout_summary": {"strength_progressing": True}
    }

    recommendation = apply_nutrition_algorithm(user, data)

    assert recommendation.adjustment_category == "increase"
    assert recommendation.recommended_calories > 2500
    assert "surplus" in recommendation.reasoning.lower()


def test_bulking_algorithm_gaining_too_fast():
    """Test bulking when gaining weight too fast with fat gain"""
    user = {"goal": "build_muscle", "sex": "male"}
    data = {
        "user_profile": {"body_fat_pct": 15, "training_status": "intermediate"},
        "weight_trend": {"weekly_rate_pct": 0.8, "is_plateau": False},  # Too fast (>0.5% for intermediate)
        "nutrition_summary": {"avg_calories": 3000},
        "body_comp_trend": {"trend": "increasing", "total_change_mm": 8},  # Fat increasing
        "workout_summary": {"strength_progressing": True}
    }

    recommendation = apply_nutrition_algorithm(user, data)

    assert recommendation.adjustment_category == "decrease"
    assert recommendation.recommended_calories < 3000
    assert "too fast" in recommendation.reasoning.lower()


def test_bulking_algorithm_optimal_rate():
    """Test bulking when gaining at optimal rate with stable body fat"""
    user = {"goal": "build_muscle", "sex": "male"}
    data = {
        "user_profile": {"body_fat_pct": 15, "training_status": "intermediate"},
        "weight_trend": {"weekly_rate_pct": 0.3, "is_plateau": False},  # Within 0.2-0.5% for intermediate
        "nutrition_summary": {"avg_calories": 2800},
        "body_comp_trend": {"trend": "stable"},
        "workout_summary": {"strength_progressing": True}
    }

    recommendation = apply_nutrition_algorithm(user, data)

    # Could be "increase" (room for more) or "none" (maintain)
    assert recommendation.adjustment_category in ["increase", "none"]
    assert "optimal rate" in recommendation.reasoning.lower() or "stable body fat" in recommendation.reasoning.lower()
```

---

## Function Tools

### 1. Trend Analysis Tools

```python
@function_tool
async def analyze_weight_trend(
    wrapper: RunContextWrapper[FitnessContext],
    days: int = 14
) -> dict:
    """
    Analyze weight trend from body logs.
    Returns plateau detection, average rate of change.
    """
    # Returns:
    # {
    #   "days_analyzed": 14,
    #   "data_points": 6,
    #   "starting_weight": 78.5,
    #   "current_weight": 78.4,
    #   "avg_weight": 78.5,
    #   "total_change": -0.1,
    #   "daily_rate": -0.007,
    #   "weekly_rate": -0.05,
    #   "weekly_rate_pct": 0.06,  # % of bodyweight
    #   "is_plateau": true,
    #   "trend": "stable"  # "stable", "increasing", "decreasing"
    # }
```

```python
@function_tool
async def analyze_body_composition_trend(
    wrapper: RunContextWrapper[FitnessContext],
    days: int = 14
) -> dict:
    """
    Analyze body composition trend using multiple methods (prioritized by reliability).

    Priority:
    1. Skinfold measurements (most reliable for trends)
    2. Waist circumference (simple, reliable)
    3. Body fat % estimates (less reliable)
    4. Inferred from strength + weight trends

    Returns trend direction and confidence level.
    """
    # Returns (if using skinfolds):
    # {
    #   "method": "skinfolds",
    #   "confidence": "high",
    #   "days_analyzed": 14,
    #   "data_points": 3,
    #   "starting_skinfold_sum_mm": 50,
    #   "current_skinfold_sum_mm": 48,
    #   "total_change_mm": -2,
    #   "daily_rate_mm": -0.14,
    #   "is_stable": false,
    #   "trend": "decreasing",
    #   "interpretation": "Fat mass decreasing"
    # }
```

### 2. Calculation Tools

```python
@function_tool
async def estimate_maintenance_calories(
    wrapper: RunContextWrapper[FitnessContext],
    current_avg_intake: float,
    weekly_weight_change_pct: float
) -> float:
    """
    Estimate maintenance calories based on current intake and observed weight change.

    Uses the relationship:
    - Weekly weight change % = energy balance / maintenance calories
    - Rearrange to find maintenance calories
    """
    # Example: If eating 2000 cal/day and losing 0.7%/week
    # Estimated deficit ~20% (from Table 2)
    # Maintenance = 2000 / (1 - 0.20) = 2500 cal
```

```python
@function_tool
async def calculate_optimal_deficit(
    wrapper: RunContextWrapper[FitnessContext],
    body_fat_pct: float,
    sex: str
) -> float:
    """
    Calculate optimal calorie deficit percentage based on body fat level.
    Based on Table 1 in Nutrition Agent Reasoning section.

    Returns: Optimal deficit percentage (5-50%)
    """
```

```python
@function_tool
async def calculate_optimal_surplus(
    wrapper: RunContextWrapper[FitnessContext],
    training_status: str
) -> dict:
    """
    Calculate optimal calorie surplus and target weight gain rate for bulking.
    Based on Table 3 in Nutrition Agent Reasoning section.

    Returns:
    {
        "surplus_pct_min": 5,
        "surplus_pct_max": 15,
        "target_weekly_gain_pct_min": 0.5,
        "target_weekly_gain_pct_max": 1.0,
        "recommended_surplus_pct": 10
    }
    """
```

```python
@function_tool
async def calculate_tdee(
    wrapper: RunContextWrapper[FitnessContext],
    weight_kg: float,
    height_cm: float,
    age: int,
    sex: str,
    activity_level: str
) -> float:
    """
    Calculate Total Daily Energy Expenditure using Mifflin-St Jeor equation.
    Activity levels: sedentary, light, moderate, active, very_active
    """
```

```python
@function_tool
async def calculate_macros(
    wrapper: RunContextWrapper[FitnessContext],
    target_calories: int,
    protein_g_per_kg: float,
    fat_pct: float
) -> dict:
    """
    Calculate macro split from target calories.

    Returns:
    {
        "protein_g": 160,
        "carbs_g": 200,
        "fat_g": 67
    }
    """
```

---

## Structured Output

```python
class NutritionRecommendation(BaseModel):
    # Current state
    current_calorie_average: int
    current_body_fat_pct: float
    observed_weekly_weight_change_pct: float

    # Recommendations
    recommended_calories: int
    recommended_deficit_or_surplus_pct: float
    optimal_deficit_or_surplus_pct: float
    recommended_macros: MacroSplit

    # Decision
    adjustment_category: str  # "increase", "decrease", "none"
    reasoning: str
    body_composition_status: str  # "fat_loss", "muscle_gain", "recomp", "maintenance"

    confidence: float  # 0.0-1.0


class MacroSplit(BaseModel):
    protein_g: int
    carbs_g: int
    fat_g: int

    @validator('*')
    def validate_positive(cls, v):
        if v < 0:
            raise ValueError("Macros must be positive")
        return v
```

---

## Nutrition Agent Reasoning

The Nutrition Specialist uses evidence-based algorithms to optimize energy intake based on observed body composition changes.

### Overview

To optimize energy intake, the nutrition agent monitors three key metrics:
1. **Energy intake** (calories consumed)
2. **Body weight** (scale weight)
3. **Body fat percentage** (via measurements, photos, or estimates)

---

## Cutting (Fat Loss)

### Table 1: Optimal Deficit by Body Fat Percentage

| Category | Fat % (Male) | Fat % (Female) | Optimal deficit (%) |
| --- | --- | --- | --- |
| Contest prep | < 8 | < 14 | 5 |
| Athletic | 8 -15 | 14 -24 | 10 |
| Average | 15 - 21 | 24 - 33 | 20 |
| Overweight | 21 - 26 | 33 - 39 | 30 |
| Obese | 26+ | 39+ | 50 |

### Table 2: Estimated Energy Deficit from Observed Weight Loss Rate

| Observed weekly bodyweight loss rate (%) | Estimated energy deficit (%) |
| --- | --- |
| 0.3 | 10 |
| 0.7 | 20 |
| 1.1 | 30 |
| 1.5 | 50 |

### Decision Tree: Cutting Algorithm

**Scenario 1: Body Weight Loss Plateau**

• **If body fat is unchanged:**
  - Current energy intake is at maintenance
  - **Action:** Create deficit based on Table 1 (Optimal Deficit by Body Fat %)
  - **Example:** Male with 20% body fat eating 2000 kcal/day → Set target to 1600 kcal (20% deficit)

• **If body fat decreases:**
  - Body recomposition is occurring (fat loss + muscle gain)
  - **Action:** No changes needed - this is a good outcome
  - **Reasoning:** Fat decrease while weight stable = muscle increase

**Scenario 2: Body Weight Loss Happening**

1. Calculate observed weekly bodyweight loss rate (%)
2. Look up estimated energy deficit (Table 2)
3. Look up optimal deficit (Table 1)
4. Compare the two:

• **If estimated deficit ≈ optimal deficit:**
  - **Action:** No changes - weight and fat loss proceeding at optimal pace
  - **Example:** 0.7% weekly loss, 20% body fat male → 20% deficit is both estimated and optimal ✓

• **If estimated deficit > optimal deficit:**
  - Weight loss is too fast - risk of muscle loss
  - **Action:** Increase target calories to create more modest deficit
  - **Example:**
    - Female, 20% body fat (athletic)
    - Observed weekly loss: 0.7% → estimated deficit: 20%
    - Optimal deficit: 10%
    - Current average intake: 2000 kcal → maintenance ~2500 kcal
    - **New target:** 2250 kcal (10% deficit)

• **If estimated deficit < optimal deficit:**
  - Weight loss is too slow - can afford more aggressive deficit
  - **Action:** Decrease target calories to create larger deficit
  - **Example:**
    - Male, 25% body fat (overweight)
    - Observed weekly loss: 0.3% → estimated deficit: 10%
    - Optimal deficit: 30%
    - Current average intake: 2700 kcal → maintenance ~3000 kcal
    - **New target:** 2100 kcal (30% deficit)

---

## Bulking (Muscle Gain)

### Table 3: Optimal Energy Surplus by Training Status

| Training status | Initial energy surplus | Planned weekly weight gain rate (% bodyweight) |
| --- | --- | --- |
| Novice | 5-15% | 0.5-1% |
| Intermediate | 2-7% | 0.2-0.5% |
| Advanced | 1-3% | any fat-free |

### Decision Tree: Bulking Algorithm

**Scenario 1: Body Weight and Fat Level Unchanged**

- Current energy intake is at maintenance
- **Action:** Add target energy surplus based on Table 3
- **Example:** Novice lifter eating 2500 kcal/day → Set target to 2750 kcal (10% surplus)

**Scenario 2: Weight Gain Above Expected Rate**

• **If body fat unchanged AND strength progressing well:**
  - Muscle gain is happening effectively
  - **Action:** Maintain current energy intake
  - **Reasoning:** No benefit from further calorie increase

• **If body fat increasing:**
  - Consuming too many calories relative to muscle gain capacity
  - **Action:** Decrease calories moderately
  - **Example:** Reduce from 3000 kcal to 2800 kcal

**Scenario 3: Weight Gain Within Expected Rate**

• **If body fat unchanged AND strength progressing well:**
  - Room for more aggressive muscle gain
  - **Action:** Increase calories moderately
  - **Example:** Increase from 2800 kcal to 3000 kcal

• **If body fat increasing (minor) AND strength progressing well:**
  - **Action:** Maintain current energy intake
  - Some fat gain is acceptable during bulking

• **If body fat increasing (significant) AND strength progressing well:**
  - **Action:** Decrease calories moderately
  - Too much fat gain relative to muscle gain

• **If body fat increasing AND strength NOT progressing:**
  - Training plan may need optimization
  - **Action:**
    1. Flag for training specialist review
    2. Decrease energy intake moderately
  - **Reasoning:** Gaining fat without strength gains = suboptimal training stimulus

---

## Body Composition Tracking Methods

### Recommended Primary Method: Skinfold Caliper Measurements

**Why skinfolds are superior for trend detection:**
- Measures subcutaneous fat thickness directly (mm)
- Same sites measured consistently = reliable TREND detection
- Absolute body fat % may be inaccurate, but CHANGES are detectable
- Cheap ($10-30 calipers), easy to do at home
- Not affected by hydration like BIA scales

**Skinfold Protocol:**
1. **Measure 3-7 sites** (tricep, abdomen, thigh, suprailiac, subscapular, chest, midaxillary)
2. **Store raw mm values** - don't just estimate body fat %
3. **Track trends:**
   - Sum of all sites (e.g., 60mm → 58mm → 56mm)
   - Individual sites to spot reduce in specific areas
4. **Consistency is key:**
   - Same time of day
   - Same hydration state
   - Same person measuring (self or partner)

**Example of trend detection:**
```
Week 1: Tricep 12mm, Abdomen 20mm, Thigh 18mm → Sum: 50mm
Week 2: Tricep 12mm, Abdomen 19mm, Thigh 17mm → Sum: 48mm (-2mm = fat decreasing)
Week 3: Tricep 11mm, Abdomen 18mm, Thigh 17mm → Sum: 46mm (-2mm = fat decreasing)

Weight plateau (78kg → 78kg → 78kg) + skinfolds decreasing = BODY RECOMPOSITION ✓
```

### Secondary Methods

1. **Waist circumference** (simple alternative)
   - Measure at navel level, morning, empty stomach
   - Decreasing waist + stable weight = fat loss

2. **Progress photos** (visual assessment)
   - AI vision analysis for body composition changes
   - Manual visual comparison

3. **BIA scale** (convenient but less reliable)
   - Track trends, ignore absolute values
   - Measure same time of day, same hydration

4. **Estimated body fat %** (for category only)
   - Jackson-Pollock formula from skinfolds
   - Navy method (waist, neck, height)
   - Visual estimate from photos
   - Only used to determine deficit category ("athletic" vs "average")

### What the Algorithm Needs

1. **Fat mass TREND** (primary decision factor):
   - Skinfold sum: increasing/decreasing/stable
   - OR waist circumference: increasing/decreasing/stable
   - OR photo comparison: more/less/same body fat

2. **Estimated body fat % CATEGORY** (secondary, for deficit table):
   - Rough category is sufficient: "athletic" (8-15% M, 14-24% F), "average" (15-21% M, 24-33% F), etc.
   - Can be estimated from skinfolds, photos, or circumferences
   - Doesn't need to be precise (±5% error is acceptable)

### Minimum Data Requirements

- Weight logs: 5+ data points over 14 days
- **Body composition logs: 2+ measurements over 14 days**
  - **Preferred:** Skinfold measurements (3-7 sites, raw mm values)
  - **Alternative:** Waist circumference
  - **Fallback:** Body fat % estimate (acknowledge higher uncertainty)
- Nutrition logs: 10+ days of calorie tracking
- Training logs: 2+ weeks of workout data (for bulking strength assessment)

### Handling Missing/Unreliable Body Composition Data

If user doesn't track body composition:
1. **Infer from strength progression:**
   - Weight stable + strength increasing = likely fat loss (body recomp)
   - Weight stable + strength stable = true plateau
2. **Conservative approach:**
   - Use smaller deficit adjustments
   - Prioritize preserving strength over aggressive weight loss
3. **Recommend starting skinfold tracking:**
   - Provide guidance on purchasing calipers
   - Tutorial on measurement technique

---

## Why Skinfold Measurements Are Critical

### The Problem with Body Fat % Alone

```
Example: User at 80kg with 20% body fat = 16kg fat mass

Week 1: 80kg, 20% BF
Week 2: 80kg, 19.5% BF

Question: Is the 0.5% change real or measurement error?
- BIA scales: ±3-5% error
- Visual estimates: Very subjective
- Navy method: ±4% error

The 0.5% change could easily be:
- Hydration variation
- Measurement inconsistency
- Time of day difference
```

### Skinfolds Solve This

```
Week 1: Tricep 12mm, Abdomen 20mm, Thigh 18mm → Sum: 50mm
Week 2: Tricep 12mm, Abdomen 19mm, Thigh 17mm → Sum: 48mm
Week 3: Tricep 11mm, Abdomen 18mm, Thigh 17mm → Sum: 46mm

Clear downward trend: -4mm over 3 weeks = FAT DECREASING ✓
Combined with weight plateau = BODY RECOMPOSITION CONFIRMED ✓
```

**Benefits:**
- **Direct measurement** of subcutaneous fat thickness (mm)
- **Same-site consistency** makes trends reliable
- **Cheap and accessible** ($10-30 calipers)
- **Not affected by hydration** like BIA scales
- **Even if absolute BF% is wrong**, the TREND is accurate

---

## Lambda Handler Example

```python
# ai_agents/nutrition_specialist/lambda_handler.py

def lambda_handler(event, context):
    """
    EventBridge triggers this every Monday at 6 AM UTC.
    Processes all active users.
    """
    # 1. Fetch all active users
    users = db.user_profiles.find_all_active()

    results = []
    for user in users:
        # 2. Gather data and calculate trends
        data = gather_14_day_data(user["user_id"])

        # 3. Check minimum data requirements
        if not meets_minimum_requirements(data):
            notify_user_improve_tracking(user["user_id"], data)
            continue

        # 4. Apply nutrition algorithm
        recommendation = apply_nutrition_algorithm(user, data)

        # 5. Store weekly analysis
        store_weekly_analysis(user["user_id"], data, recommendation)

        # 6. Update nutrition plan if needed
        if recommendation.adjustment_category != "none":
            update_nutrition_plan(user["user_id"], recommendation)

        results.append(recommendation)

    return {"users_processed": len(results)}


def gather_14_day_data(user_id: str) -> dict:
    """Gather all data and calculate trends"""
    user_profile = db.user_profiles.find_one({"user_id": user_id})
    weight_logs = db.body_logs.find_recent(user_id, days=14)
    body_comp_logs = db.body_logs.find_recent(user_id, days=14)
    nutrition_logs = db.nutrition_logs.find_recent(user_id, days=14)
    workout_logs = db.workout_logs.find_recent(user_id, days=14)

    return {
        "user_profile": {
            "goal": user_profile.goal,
            "sex": user_profile.sex,
            "body_fat_pct": calculate_current_body_fat(body_comp_logs),
            "training_status": user_profile.training_status
        },
        "weight_trend": analyze_weight_trend(weight_logs),
        "body_comp_trend": analyze_body_composition_trend(body_comp_logs),
        "nutrition_summary": {
            "avg_calories": calculate_avg_calories(nutrition_logs),
            "days_logged": len(nutrition_logs)
        },
        "workout_summary": analyze_strength_trends(workout_logs)
    }


def apply_nutrition_algorithm(user: dict, data: dict) -> NutritionRecommendation:
    """Apply evidence-based nutrition algorithm"""
    # 1. Estimate maintenance calories from current intake and weight change rate
    maintenance = estimate_maintenance_calories(
        data["nutrition_summary"]["avg_calories"],
        data["weight_trend"]["weekly_rate_pct"]
    )

    # 2. Calculate optimal deficit/surplus based on body fat %, sex, training status
    if user["goal"] == "lose_weight":
        optimal_deficit = calculate_optimal_deficit(
            data["user_profile"]["body_fat_pct"],
            data["user_profile"]["sex"]
        )
    else:
        optimal_surplus = calculate_optimal_surplus(
            data["user_profile"]["training_status"]
        )

    # 3. Body recomposition check
    if (data["weight_trend"]["weekly_rate_pct"] < 0.2 and
        data["body_comp_trend"]["trend"] == "decreasing"):
        return NutritionRecommendation(
            adjustment_category="none",
            recommended_calories=data["nutrition_summary"]["avg_calories"],
            reasoning="Body recomposition detected - maintain current intake"
        )

    # 4. Make recommendation based on algorithm
    # ... rest of algorithm implementation
```

---

## DynamoDB Schema

### New Table: `weekly_analyses`

```python
{
    "user_id": "string",  # Partition key
    "week_starting": "2025-10-20",  # Sort key (ISO date)
    "status": "completed|failed",

    # Data summary
    "data_summary": {
        "weight_logs_count": 6,
        "workout_logs_count": 4,
        "nutrition_logs_count": 12,

        # Body composition tracking
        "body_composition_method": "skinfolds",  # "skinfolds", "waist", "body_fat_pct", "none"
        "body_composition_logs_count": 3,
        "body_composition_confidence": "high",  # "high", "medium", "low", "none"

        # Weight metrics
        "avg_weight_kg": 78.5,
        "weight_change_kg": -0.3,
        "weekly_weight_change_pct": 0.38,  # Percentage of bodyweight

        # Body composition metrics (method-dependent)
        "skinfold_sum_starting_mm": 50,
        "skinfold_sum_current_mm": 46,
        "skinfold_change_mm": -4,  # Negative = fat decreasing

        "body_composition_trend": "decreasing",  # "increasing", "stable", "decreasing"
        "body_composition_interpretation": "Fat mass decreasing",

        # Nutrition metrics
        "avg_calories": 2180,

        # Training metrics
        "total_training_volume": 15000  # kg
    },

    # Issues detected (nutrition-related only)
    "issues_detected": [
        {
            "type": "weight_plateau",
            "severity": "medium",
            "description": "No weight change in 14 days (avg 78.5kg)",
            "recommended_action": "reduce_calories",
            "metadata": {}
        }
    ],

    # Plan updates (nutrition only)
    "plan_updated": true,
    "updates": {
        "nutrition": {
            "old_calories": 2200,
            "new_calories": 2000,
            "reasoning": "Weight plateau detected..."
        }
    },

    # Metadata
    "analyzed_at": "2025-10-27T06:00:00Z",
    "analysis_duration_ms": 3500
}
```

### New Table: `active_plans` (Nutrition only)

```python
{
    "user_id": "string",  # Partition key
    "plan_type": "nutrition",  # Always "nutrition"
    "version": 3,
    "created_at": "2025-10-27T06:00:00Z",
    "active": true,

    # Nutrition plan fields
    "target_calories": 2000,
    "macro_split": {
        "protein_g": 160,
        "carbs_g": 200,
        "fat_g": 67
    },
    "meal_plan": [
        {
            "meal_name": "Breakfast",
            "time": "08:00",
            "foods": [...]
        }
    ],

    # Metadata
    "reason_for_update": "Weight plateau detected in weekly analysis",
    "previous_version": 2,
    "updated_by": "nutrition_specialist"
}
```

### Updated Table: `body_logs` (Enhanced with skinfold support)

```python
{
    "user_id": "string",  # Partition key
    "timestamp": "2025-10-27T08:00:00Z",  # Sort key
    "log_date": "2025-10-27",

    # Basic metrics (existing)
    "weight": 78.5,  # kg
    "height": 175,   # cm (optional, usually static)

    # Body composition tracking (NEW - multiple methods supported)

    # Method 1: Skinfold measurements (PREFERRED)
    "skinfolds": {
        "tricep": 12,        # mm
        "abdomen": 18,       # mm
        "thigh": 17,         # mm
        "suprailiac": 15,    # mm (optional)
        "subscapular": 14,   # mm (optional)
        "chest": 10,         # mm (optional, males)
        "midaxillary": 12    # mm (optional)
    },
    "skinfold_sum": 46,  # mm (auto-calculated sum of all measured sites)

    # Method 2: Circumference measurements (ALTERNATIVE)
    "waist_cm": 83,      # cm (at navel level)
    "hips_cm": 95,       # cm (optional)
    "neck_cm": 38,       # cm (optional, for Navy method)
    "bicep_cm": 35,      # cm (optional)
    "thigh_cm": 58,      # cm (optional)

    # Method 3: Body fat % estimate (FALLBACK)
    "body_fat_pct": 20.5,           # % (can be calculated from skinfolds or entered directly)
    "body_fat_method": "jackson_pollock_3",  # "jackson_pollock_3", "jackson_pollock_7", "navy", "bia_scale", "visual", "dexa"

    # Progress photos (OPTIONAL)
    "photo_front": "s3://bucket/user123/2025-10-27_front.jpg",
    "photo_side": "s3://bucket/user123/2025-10-27_side.jpg",
    "photo_back": "s3://bucket/user123/2025-10-27_back.jpg",

    # Metadata
    "notes": "Measured in morning, fasted",
    "created_at": "2025-10-27T08:05:00Z"
}
```

---

## Key Advantages

1. **Personalized to individual body composition** - Leaner individuals get smaller deficits to preserve muscle, higher body fat allows more aggressive deficits
2. **Distinguishes fat loss from muscle gain** - Body recomposition is recognized and encouraged
3. **Prevents muscle loss** - Adjusts deficits if weight loss is too rapid for current body fat level
4. **Optimizes muscle gain rate** - Surplus scaled to training status to minimize fat gain
5. **Evidence-based thresholds** - Tables based on coaching best practices and research
6. **Coordinates with training** - Recognizes when poor strength gains indicate training issues
7. **Transparent reasoning** - Users understand why calories are adjusted
8. **Reliable trend detection** - Prioritizes skinfold measurements over body fat % estimates for accurate fat mass tracking
9. **Flexible measurement methods** - Supports skinfolds, waist circumference, body fat %, or inference from strength gains
10. **Confidence-aware recommendations** - Adjusts recommendation aggressiveness based on data quality

---

## Lambda Deployment

**Function name**: `fitness-nutrition-specialist`

**Runtime**: Python 3.11+

**Trigger**: EventBridge cron rule (every Monday 6 AM UTC)

**Environment variables**:
- `DYNAMODB_TABLE_PREFIX`: Table name prefix
- `BEDROCK_MODEL_ID`: Claude model ID

**IAM Permissions**:
- DynamoDB: Read/Write access to `user_profiles`, `body_logs`, `nutrition_logs`, `workout_logs`, `weekly_analyses`, `active_plans`
- Bedrock: Invoke model
