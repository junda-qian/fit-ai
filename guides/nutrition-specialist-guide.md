# Nutrition Specialist Agent - Complete Guide

## What Is It?

The Nutrition Specialist is an **intelligent nutrition coach** that analyzes your progress data (weight, body composition, training) and provides personalized calorie and macro recommendations. Think of it as your personal dietitian who:

- Tracks your weight trends
- Monitors body composition changes (fat gain/loss)
- Analyzes training progress (via Training Specialist)
- Calculates optimal calorie adjustments
- Recommends macro nutrient splits

**Key Feature**: This is a **pure algorithmic agent** - NO AI/LLM is used. All decisions are made using deterministic if/else logic based on evidence-based research.

## Why Does It Exist?

Nutrition is confusing. Common problems:
- **"I'm eating 1500 calories but not losing weight!"** → Maybe 1500 isn't actually a deficit for you
- **"I gained 5 lbs this month - is this too fast?"** → Depends on your body fat and training status
- **"My weight hasn't moved in 3 weeks"** → Could be a plateau OR body recomposition (losing fat, gaining muscle)

The Nutrition Specialist solves these by:
1. **Using YOUR real-world data** instead of population formulas
2. **Detecting body recomposition** (when scale weight is misleading)
3. **Applying evidence-based tables** for optimal deficit/surplus
4. **Considering training progress** for smarter bulking decisions

---

## How It Works (High-Level)

```
User Data (14 days):
├── Weight logs
├── Body composition measurements
├── Nutrition logs
└── Training progress (from Training Agent)
         ↓
  Nutrition Specialist
         ↓
    Analyzes:
    1. Weight trend
    2. Body comp trend
    3. Maintenance calories
    4. Optimal deficit/surplus
         ↓
    Recommendation:
    - Increase/decrease/maintain calories
    - Updated macro targets
    - Plain-English reasoning
```

---

## The Three Core Algorithms

### 1. Weight Trend Analysis

**Purpose**: Understand if you're gaining, losing, or maintaining weight.

**Input**: List of weight measurements over 14 days

**Process**:
```python
1. Sort logs by date
2. Calculate:
   - Starting weight
   - Current weight
   - Average weight
   - Total change
   - Daily rate (kg/day)
   - Weekly rate (kg/week)
   - Weekly rate as % of bodyweight
3. Detect plateau (< 0.2%/week = stable)
4. Determine trend (increasing/stable/decreasing)
```

**Example**:
```
Logs:
- Nov 1: 80.0 kg
- Nov 7: 79.5 kg
- Nov 14: 79.0 kg

Analysis:
- Total change: -1.0 kg over 14 days
- Daily rate: -0.071 kg/day
- Weekly rate: -0.5 kg/week
- Weekly rate %: -0.63% (relative to avg weight 79.5kg)
- Plateau: No (0.63% > 0.2% threshold)
- Trend: decreasing
```

**Why %/week matters**:
- 100kg person losing 0.5kg/week = 0.5% (slow)
- 60kg person losing 0.5kg/week = 0.83% (moderate)

Same absolute loss, different relative impact!

---

### 2. Body Composition Trend Analysis

**Purpose**: Detect fat gain/loss independent of scale weight.

**Priority of Methods**:
1. **Skinfold calipers** (best - tracks subcutaneous fat)
2. **Waist circumference** (good - simple, reliable)
3. **Body fat % estimates** (okay - higher error margin)

**Why this matters**:
```
Scenario 1: Weight stable, skinfolds decreasing
→ Body recomposition! (losing fat, gaining muscle)
→ DON'T reduce calories

Scenario 2: Weight increasing, skinfolds stable
→ Lean muscle gain! (good bulk)
→ KEEP calories

Scenario 3: Weight increasing, skinfolds increasing
→ Fat gain (bad bulk)
→ REDUCE calories
```

**Skinfold Analysis**:
```python
1. Get skinfold sum measurements (e.g., sum of 3-site or 7-site)
2. Calculate change from start to current
3. Thresholds:
   - < 2mm change = stable
   - Decreasing = fat loss
   - Increasing = fat gain
```

**Example**:
```
Nov 1: 50mm total
Nov 14: 46mm total
Change: -4mm

Interpretation: "Fat mass decreasing"
Confidence: High (skinfolds are reliable for trends)
```

---

### 3. Main Nutrition Algorithm

**Purpose**: Recommend calorie adjustments based on all available data.

**Inputs**:
- User profile (goal, body fat %, sex, training status)
- Weight trend
- Body composition trend
- Nutrition summary (avg calories)
- Training summary (from Training Specialist)

**Flow**:
```
1. Estimate maintenance calories
   ↓
2. Calculate optimal deficit/surplus from tables
   ↓
3. Detect body recomposition
   ↓
4. Apply cutting OR bulking algorithm
   ↓
5. Return recommendation with reasoning
```

---

## Evidence-Based Tables

### Table 1: Optimal Deficit by Body Fat %

**Purpose**: Determine safe deficit size based on how lean you are.

**Logic**: Leaner people need smaller deficits to preserve muscle. Higher body fat allows larger deficits.

| Category       | Male BF%  | Female BF% | Optimal Deficit |
|----------------|-----------|------------|-----------------|
| Contest prep   | < 8%      | < 14%      | 5%              |
| Athletic       | 8-15%     | 14-24%     | 10%             |
| Average        | 15-21%    | 24-33%     | 20%             |
| Overweight     | 21-26%    | 33-39%     | 30%             |
| Obese          | 26%+      | 39%+       | 50%             |

**Example**:
```python
calculate_optimal_deficit(20, "male")
→ 20% deficit (average category)

calculate_optimal_deficit(12, "female")
→ 5% deficit (contest prep - very lean, be conservative)
```

**Why different by sex?**
- Women naturally have higher essential body fat (~10-13% vs ~2-5% for men)
- Same body fat % = different leanness level
- Example: 20% BF male = athletic, 20% BF female = quite lean

---

### Table 2: Estimated Deficit from Weight Loss Rate

**Purpose**: Reverse-engineer your current deficit from observed weight loss.

**Logic**: Weight loss rate correlates with energy deficit size.

| Weekly Loss (% BW) | Estimated Deficit |
|--------------------|-------------------|
| < 0.1%             | 0% (maintenance)  |
| 0.1 - 0.3%         | 10%               |
| 0.3 - 0.7%         | 20%               |
| 0.7 - 1.1%         | 30%               |
| 1.1%+              | 50%               |

**Example**:
```python
estimate_deficit_from_loss_rate(0.7)
→ 20% (losing 0.7%/week suggests ~20% deficit)

estimate_deficit_from_loss_rate(1.2)
→ 50% (losing 1.2%/week = very aggressive deficit)
```

**How it's used in the algorithm**:
```
If your loss rate suggests 30% deficit
But optimal deficit for your body fat is only 20%
→ INCREASE calories (you're losing too fast, risking muscle loss)
```

---

### Table 3: Optimal Surplus by Training Status

**Purpose**: Determine appropriate calorie surplus for muscle building.

**Logic**: Beginners can build muscle faster, so higher surplus is productive. Advanced lifters build muscle slowly, so smaller surplus minimizes fat gain.

| Training Status | Energy Surplus | Weekly Gain (%BW) |
|-----------------|----------------|-------------------|
| Novice          | 5-15%          | 0.5-1.0%          |
| Intermediate    | 2-7%           | 0.2-0.5%          |
| Advanced        | 1-3%           | 0.1-0.3%          |

**Example**:
```python
calculate_optimal_surplus("intermediate")
→ {
    'recommended_surplus_pct': 5,
    'target_weekly_gain_pct_min': 0.2,
    'target_weekly_gain_pct_max': 0.5
}
```

**Why this matters**:
```
Novice gaining 1%/week (80kg → 80.8kg):
✓ Good! Building muscle fast, some fat gain is acceptable

Advanced gaining 1%/week:
✗ Bad! Can't build muscle that fast, mostly fat gain
```

---

## Maintenance Calorie Estimation

**Traditional approach** (population formulas):
```
Harris-Benedict, Mifflin-St Jeor, etc.
→ Uses age, sex, height, weight
→ Gives rough estimate
→ Often inaccurate (±200-400 calories)
```

**Nutrition Specialist approach** (reverse engineering):
```
Uses YOUR actual data:
- Current average intake
- Observed weight change

If eating 2000 cal and losing 0.7%/week:
→ Losing 0.7%/week ≈ 20% deficit (from Table 2)
→ Maintenance = 2000 / (1 - 0.20) = 2500 cal
```

**Formula**:
```python
def estimate_maintenance_calories(current_intake, weekly_change_pct):
    if abs(weekly_change_pct) < 0.1:
        return current_intake  # Already at maintenance

    # Rough approximation: 1% change ≈ 30% deficit/surplus
    estimated_deficit_surplus_pct = weekly_change_pct * -30

    if deficit:
        maintenance = current_intake / (1 - deficit_pct/100)
    else:  # surplus
        maintenance = current_intake / (1 + surplus_pct/100)

    return maintenance
```

**Example**:
```
Input:
- Current intake: 2000 cal
- Weekly change: -0.7% (losing weight)

Calculation:
- Estimated deficit: 0.7 * -30 = 21% (roughly 20%)
- Maintenance = 2000 / (1 - 0.21) = 2532 cal

Output: ~2500 maintenance calories
```

**Why this is more accurate**:
- Based on YOUR metabolism (not population average)
- Accounts for your actual activity level
- Includes measurement errors and logging accuracy

---

## Cutting Algorithm (Fat Loss)

**Goal**: Lose fat while preserving muscle.

**Inputs**:
- User profile (body fat %, sex)
- Weight trend
- Body composition trend
- Nutrition summary
- Maintenance calories

**Logic Flow**:
```
1. Check for body recomposition
   IF weight stable AND body fat decreasing:
      → "Great! Maintain calories, you're recomping"
      → STOP (no adjustment)

2. Calculate observed loss rate (weekly %/week)

3. Map to estimated deficit (Table 2)

4. Get optimal deficit for body fat level (Table 1)

5. Compare:
   a) Losing too fast (estimated > optimal)
      → INCREASE calories to preserve muscle

   b) Losing too slow (estimated < optimal)
      → DECREASE calories for more fat loss

   c) On track (within 5% of optimal)
      → MAINTAIN calories
```

**Example 1: Losing Too Fast**
```
User: Male, 15% body fat, 80kg
Maintenance: 2500 cal
Current intake: 1600 cal
Weekly loss: 1.0% (0.8kg/week)

Analysis:
1. Optimal deficit for 15% BF male: 10% (Table 1)
2. Observed loss rate 1.0%/week → ~30% deficit (Table 2)
3. Comparison: 30% > 10% (losing too fast!)

Recommendation:
- Increase to 2250 cal (10% deficit)
- Reasoning: "Weight loss too fast (1.0%/week = ~30% deficit).
  Risk of muscle loss at 15% body fat. Increase to 2250 cal
  (10% deficit) to preserve muscle while continuing fat loss."
```

**Example 2: On Track**
```
User: Male, 25% body fat, 90kg
Maintenance: 2800 cal
Current intake: 2000 cal
Weekly loss: 0.7% (0.63kg/week)

Analysis:
1. Optimal deficit for 25% BF male: 30% (Table 1 - overweight)
2. Observed loss rate 0.7%/week → ~20% deficit (Table 2)
3. Comparison: 20% vs 30% (slightly under, but close enough)

Recommendation:
- Maintain 2000 cal
- Reasoning: "Weight loss proceeding well (0.7%/week).
  Current deficit (~20%) is close to optimal (30% for 25% body fat).
  Continue with 2000 cal/day."
```

---

## Bulking Algorithm (Muscle Gain)

**Goal**: Gain muscle while minimizing fat gain.

**Inputs**:
- Same as cutting, PLUS:
- Training summary (from Training Specialist agent)

**Why Training Specialist matters**:
```
Weight gain + strength increasing = muscle gain ✓
Weight gain + strength stagnant = fat gain ✗

Nutrition Specialist doesn't calculate this itself.
It trusts the Training Specialist's expert assessment.
```

**Logic Flow**:
```
1. Get target gain rate from Table 3 (based on training status)

2. Compare observed vs target gain rate:

   Scenario A: No weight gain (plateau)
      → INCREASE calories (need surplus for muscle)

   Scenario B: Gaining above target rate
      IF body fat stable AND strength increasing:
         → MAINTAIN (efficient muscle gain!)
      ELSE:
         → DECREASE (too much fat gain)

   Scenario C: Gaining within target rate
      IF body fat stable AND strength increasing:
         → INCREASE +5% (room to push harder)
      IF body fat increasing AND strength increasing:
         IF significant fat gain (>5mm skinfolds):
            → DECREASE (minimize fat)
         ELSE:
            → MAINTAIN (minor fat gain acceptable)
      IF body fat increasing AND strength NOT increasing:
         → DECREASE to half surplus (gaining fat without strength)

   Scenario D: Gaining slower than target
      → INCREASE calories
```

**Example 1: Efficient Bulk**
```
User: Intermediate, 75kg, 12% body fat
Maintenance: 2500 cal
Current intake: 2600 cal
Weekly gain: 0.6% (0.45kg/week)
Target: 0.2-0.5%/week (from Table 3)
Body comp: Stable
Strength: Increasing

Analysis:
- Gaining 0.6%/week (above target 0.5%)
- BUT body fat stable + strength up
- This indicates efficient muscle gain!

Recommendation:
- MAINTAIN 2600 cal
- Reasoning: "Gaining weight (0.6%/week) faster than target
  (0.5%/week), BUT body fat is stable and strength is increasing.
  This indicates efficient muscle gain. Maintain 2600 cal/day."
```

**Example 2: Too Much Fat**
```
User: Intermediate, 75kg, 14% body fat
Maintenance: 2500 cal
Current intake: 2750 cal
Weekly gain: 0.6% (0.45kg/week)
Target: 0.2-0.5%/week
Body comp: Increasing (+6mm skinfolds)
Strength: Increasing

Analysis:
- Gaining 0.6%/week (above target)
- Body fat increasing significantly
- Strength up (good) BUT too much fat relative to muscle

Recommendation:
- DECREASE to 2625 cal (5% surplus)
- Reasoning: "Body fat increasing significantly (+6mm skinfolds).
  While strength is progressing, reduce surplus to minimize
  fat gain. Decrease to 2625 cal (5% surplus)."
```

**Example 3: Not Enough Gain**
```
User: Novice, 70kg, 15% body fat
Maintenance: 2400 cal
Current intake: 2500 cal
Weekly gain: 0.3% (0.21kg/week)
Target: 0.5-1.0%/week (from Table 3 - novice)

Analysis:
- Gaining 0.3%/week (below target 0.5%)
- As a novice, can build muscle faster

Recommendation:
- INCREASE to 2640 cal (10% surplus)
- Reasoning: "Weight gain slower than target (0.3%/week vs
  0.5%/week). Increase to 2640 cal (10% surplus) for muscle growth."
```

---

## Macro Calculations

**Purpose**: Split calories into protein, carbs, and fats.

**Evidence-Based Protein Targets**:
| Goal         | Protein (g/kg bodyweight) | Why                          |
|--------------|---------------------------|------------------------------|
| Cutting      | 2.0-2.4                   | Higher to preserve muscle    |
| Bulking      | 1.6-2.0                   | Moderate for muscle gain     |
| Maintenance  | 1.6-2.0                   | Moderate for maintenance     |

**Fat Targets**:
- **25-30% of calories**
- Minimum 20% for hormone health
- Not too high (leaves less for carbs = less training fuel)

**Carbs**:
- **Fill the remainder** after protein and fat
- Primary fuel for intense training
- Protein-sparing (prevents muscle breakdown)

**Formula**:
```python
def calculate_macros(target_calories, body_weight_kg, goal):
    # 1. Protein (g/kg based on goal)
    protein_g_per_kg = {
        "lose_weight": 2.2,
        "build_muscle": 1.8,
        "maintain": 1.8
    }[goal]

    protein_g = round(body_weight_kg * protein_g_per_kg)
    protein_cal = protein_g * 4  # 4 cal/gram

    # 2. Fat (25% of total calories)
    fat_cal = round(target_calories * 0.25)
    fat_g = round(fat_cal / 9)  # 9 cal/gram

    # 3. Carbs (remainder)
    carbs_cal = target_calories - protein_cal - (fat_g * 9)
    carbs_g = round(carbs_cal / 4)  # 4 cal/gram

    return {
        "protein_g": protein_g,
        "carbs_g": carbs_g,
        "fat_g": fat_g
    }
```

**Example**:
```
Target: 2000 calories
Weight: 75kg
Goal: Cutting

Calculations:
1. Protein: 75kg × 2.2 = 165g = 660 cal
2. Fat: 2000 × 0.25 = 500 cal = 56g
3. Carbs: 2000 - 660 - 500 = 840 cal = 210g

Result:
- Protein: 165g (33% of calories)
- Fat: 56g (25% of calories)
- Carbs: 210g (42% of calories)
```

---

## Integration with Training Specialist

**Why Nutrition needs Training data**:

During a bulk, two people gaining 0.5kg/week:
- Person A: Strength increasing → likely muscle gain ✓
- Person B: Strength stagnant → likely fat gain ✗

Same weight gain, different quality!

**How it works**:
```
1. Training Specialist runs weekly analysis
   - Analyzes all exercises
   - Determines overall strength trend
   - Publishes TrainingProgressSummary to database

2. Nutrition Specialist fetches this summary
   - Reads: overall_strength_trend
   - Values: "improving", "stable", "declining", "insufficient_data"

3. Uses in bulking decisions:
   IF strength_progressing AND weight_gaining AND bf_stable:
      → Great bulk! Keep or even increase calories

   IF NOT strength_progressing AND weight_gaining:
      → Bad bulk! Reduce surplus, check training program
```

**TrainingProgressSummary Model**:
```python
{
    "user_id": "user_123",
    "week": "2025-W47",
    "overall_strength_trend": "improving",  # ← Key field
    "exercises_analyzed": 8,
    "exercises_progressing": 6,
    "exercises_plateaued": 2,
    "exercises_regressing": 0,
    "avg_weekly_volume_kg": 12500.0,
    "data_quality": "good",
    "trend_confidence": 0.85
}
```

**Example Scenario**:
```
Week 1-4: User gaining 0.4kg/week, strength up
→ Nutrition: "Good progress! Maintain calories"

Week 5-8: User still gaining 0.4kg/week, strength plateaued
→ Training: "Strength stagnant, possible overreaching"
→ Nutrition: "Gaining weight without strength gains.
             Reduce calories. Training may need adjustment."
```

---

## Backend Architecture

### File Structure
```
ai_agents/
└── nutrition_specialist/
    ├── algorithm.py          # Main nutrition logic
    ├── trend_analysis.py     # Weight & body comp analysis
    ├── tools.py              # Helper functions & tables
    └── __init__.py           # Exports

ai_agents/shared/
└── models.py                 # Pydantic models
```

### API Endpoint

```
POST /api/nutrition/analyze

Request:
{
  "user_id": "user_123"
}

Backend Process:
1. Fetch user profile
2. Fetch last 14 days of data:
   - Body logs (weight, skinfolds, waist)
   - Daily summaries (nutrition, workouts)
3. Analyze weight trend
4. Analyze body composition trend
5. Summarize nutrition data
6. Fetch training summary from Training Agent
7. Run nutrition algorithm
8. Return recommendation

Response:
{
  "user_id": "user_123",
  "analysis_date": "2025-11-15T10:30:00Z",
  "data_quality": {
    "weight_logs": 10,
    "body_comp_logs": 8,
    "nutrition_days": 12,
    "training_summary_available": true
  },
  "trends": {
    "weight": {
      "current": 78.5,
      "avg": 79.0,
      "weekly_rate_pct": -0.63,
      "is_plateau": false,
      "trend": "decreasing"
    },
    "body_composition": {
      "method": "skinfolds",
      "confidence": "high",
      "trend": "decreasing",
      "interpretation": "Fat mass decreasing"
    },
    "training": {
      "overall_strength_trend": "improving",
      "exercises_analyzed": 8,
      "data_quality": "good"
    }
  },
  "recommendation": {
    "current_calorie_average": 2000,
    "recommended_calories": 2000,
    "recommended_macros": {
      "protein_g": 165,
      "carbs_g": 210,
      "fat_g": 56
    },
    "adjustment_category": "none",
    "reasoning": "Weight loss proceeding at optimal pace...",
    "body_composition_status": "fat_loss",
    "confidence": 1.0
  }
}
```

---

## Common Scenarios

### Scenario 1: Successful Cut

**Data**:
- Goal: lose_weight
- Body fat: 20% (male)
- Weight: 80kg → 78kg over 14 days
- Skinfolds: 60mm → 56mm
- Current intake: 2000 cal
- Strength: stable

**Analysis**:
```
Weight trend:
- Weekly loss: 0.71% (good rate)
- Trend: decreasing

Body comp:
- Method: skinfolds
- Change: -4mm (fat decreasing)
- Confidence: high

Optimal deficit: 20% (Table 1 for 20% BF male)
Estimated deficit: 20% (Table 2 for 0.71%/week)
```

**Recommendation**:
```
Adjustment: NONE
Calories: 2000 (maintain)
Reasoning: "Weight loss proceeding at optimal pace (0.71%/week).
Current deficit (~20%) matches optimal (20% for 20% body fat).
Continue with 2000 cal/day."
```

---

### Scenario 2: Body Recomposition Detected

**Data**:
- Goal: lose_weight
- Body fat: 18% (male)
- Weight: 75kg → 75kg (stable)
- Skinfolds: 55mm → 51mm
- Current intake: 2200 cal
- Strength: increasing

**Analysis**:
```
Weight trend:
- Weekly change: 0.0%
- Plateau: Yes
- Trend: stable

Body comp:
- Method: skinfolds
- Change: -4mm (fat decreasing!)
- Confidence: high

Special case: Weight stable BUT fat decreasing = RECOMP!
```

**Recommendation**:
```
Adjustment: NONE
Calories: 2200 (maintain)
Reasoning: "Body recomposition detected: weight stable at 75kg
but body fat decreasing (skinfolds -4mm). This is excellent
progress - you're losing fat while gaining muscle! Maintain
current calories."
```

---

### Scenario 3: Dirty Bulk (Too Much Fat)

**Data**:
- Goal: build_muscle
- Training status: intermediate
- Body fat: 15% → 18%
- Weight: 70kg → 72kg over 14 days
- Skinfolds: 45mm → 52mm (+7mm)
- Current intake: 2800 cal
- Strength: increasing

**Analysis**:
```
Weight trend:
- Weekly gain: 1.02% (too fast!)
- Trend: increasing

Body comp:
- Method: skinfolds
- Change: +7mm (significant fat gain)
- Confidence: high

Target: 0.2-0.5%/week (Table 3 for intermediate)
Actual: 1.02%/week (way too fast!)
Strength: Increasing (good, but too much fat)
```

**Recommendation**:
```
Adjustment: DECREASE
Calories: 2450 (5% surplus)
Reasoning: "Body fat increasing significantly (+7mm skinfolds).
While strength is progressing, reduce surplus to minimize fat
gain. Decrease to 2450 cal (5% surplus)."
```

---

### Scenario 4: Stalled Cut (Need to Push Harder)

**Data**:
- Goal: lose_weight
- Body fat: 28% (male)
- Weight: 95kg → 94.5kg over 14 days
- Current intake: 2500 cal
- Maintenance (estimated): 2900 cal

**Analysis**:
```
Weight trend:
- Weekly loss: 0.19%
- Trend: decreasing (but slow)

Optimal deficit: 30% (Table 1 for 28% BF - overweight)
Estimated deficit: 10% (Table 2 for 0.19%/week)
Comparison: 10% << 30% (losing too slow!)
```

**Recommendation**:
```
Adjustment: DECREASE
Calories: 2030 (30% deficit)
Reasoning: "Weight loss too slow (0.19%/week = ~10% deficit).
At 28% body fat, you can safely increase deficit to 30%.
Decrease to 2030 cal/day for more effective fat loss."
```

---

## Technical Details

### Pure Deterministic Algorithm

**NO AI is used**:
```python
# This is the entire algorithm:
if condition_A:
    return recommendation_A
elif condition_B:
    return recommendation_B
else:
    return recommendation_C
```

**Benefits**:
- **Explainable**: Every decision can be traced
- **Consistent**: Same inputs = same outputs
- **Fast**: No API calls, <10ms execution
- **Free**: No LLM costs
- **Testable**: Easy to write unit tests
- **Debuggable**: Can step through logic

**Contrast with LLM approach**:
```
LLM Agent:
- Feeds all data to AI
- AI "reasons" about recommendation
- Non-deterministic (varies slightly)
- Slower (~1-3 seconds)
- Costs money per call
- Harder to debug

Deterministic Agent:
- Uses if/else logic
- Tables define decisions
- 100% deterministic
- Very fast (<10ms)
- Free
- Easy to debug
```

---

### Data Quality Requirements

**Minimum data needed**:
```
Weight trend: 3+ measurements over 14 days
Body comp: 2+ measurements over 14 days (optional but recommended)
Nutrition logs: 10+ days over 14 days
Training summary: Published by Training Agent (for bulking)
```

**What happens with insufficient data**:
```python
if not sufficient_data:
    return NutritionRecommendation(
        adjustment_category="none",
        reasoning="Insufficient data. Log more consistently.",
        confidence=0.0
    )
```

**Data quality levels**:
```
Excellent: 14/14 days logged, daily weigh-ins, skinfolds tracked
Good: 10-13/14 days logged, 3+ weigh-ins, body comp tracked
Fair: 7-9/14 days logged, 2 weigh-ins
Poor: <7/14 days logged, <2 weigh-ins
```

---

### Testing the Algorithm

**Unit tests** (`test_nutrition.py`):
```python
def test_cutting_on_track():
    """Test cutting algorithm when loss rate is optimal"""
    weight_trend = WeightTrend(
        weekly_rate_pct=-0.7,  # Losing 0.7%/week
        is_plateau=False,
        trend="decreasing"
    )

    body_comp_trend = BodyCompositionTrend(
        method="skinfolds",
        trend="decreasing"
    )

    user_profile = {
        "goal": "lose_weight",
        "body_fat_pct": 20,  # Male, average
        "sex": "male"
    }

    recommendation = apply_cutting_algorithm(...)

    assert recommendation.adjustment_category == "none"
    assert recommendation.recommended_calories == 2000
```

**Test coverage**:
- All scenarios in Tables 1, 2, 3
- Body recomposition detection
- Edge cases (very high/low body fat)
- Insufficient data handling

---

## Common Questions

### Q: Why not use AI for this?

**A**: Nutrition decisions follow clear rules:
- Body fat % → optimal deficit (Table 1)
- Loss rate → estimated deficit (Table 2)
- Training status → optimal surplus (Table 3)

These are lookup tables + simple math. AI would be overkill and less reliable.

**When AI IS useful**:
- Natural language explanations (generating varied reasoning text)
- Personalized meal suggestions (creative food combinations)
- Answering user questions (conversational interface)

**When deterministic is better**:
- Rule-based decisions (this agent)
- Precise calculations (energy/macros)
- Consistent outputs (same recommendation every time)

---

### Q: How often should I run this analysis?

**A**: Every 1-2 weeks.

**Why not daily?**
- Weight fluctuates day-to-day (water, food timing, etc.)
- Need 14 days for reliable trends
- Body composition changes slowly

**Why not monthly?**
- 2 weeks is enough to see trends
- Allows faster course corrections
- Prevents wasting time on ineffective approaches

---

### Q: What if my weight is stable but I'm not losing fat?

**A**: Two possibilities:

**1. True Plateau** (bad):
```
Weight: stable
Body comp: stable (skinfolds not changing)
Strength: stable/declining

→ Not in a deficit
→ DECREASE calories
```

**2. Body Recomposition** (good):
```
Weight: stable
Body comp: improving (skinfolds decreasing)
Strength: increasing

→ Losing fat, gaining muscle simultaneously
→ MAINTAIN calories (this is ideal!)
```

The algorithm detects this automatically.

---

### Q: Can I override the recommendation?

**A**: Yes! The agent provides guidance, but you know your body best.

**When to override**:
- You feel terrible on recommended calories (energy, mood, performance)
- Life stress is high (adjust conservatively)
- Special events coming up (vacation, competition)
- Hunger is unmanageable (increase by 5-10%)

**When to trust the algorithm**:
- You're emotionally attached to the scale number
- You want faster results than recommended
- You're making excuses to avoid discipline

---

### Q: What about diet breaks and refeeds?

**A**: The algorithm doesn't explicitly program these, but they're important:

**Diet Break** (1-2 weeks at maintenance):
- After 8-12 weeks of cutting
- Restore hormones, reduce fatigue
- Psychological relief
- Then resume deficit

**Refeed** (1-2 days at maintenance):
- Weekly during aggressive cuts
- Replenish glycogen
- Boost leptin temporarily
- Psychological boost

Manually implement these by temporarily ignoring "decrease" recommendations.

---

### Q: Why does it use %/week instead of absolute weight?

**A**: Relative weight change accounts for body size:

```
Person A: 100kg losing 0.5kg/week = 0.5%/week (slow)
Person B: 60kg losing 0.5kg/week = 0.83%/week (fast)
```

Same absolute loss, but:
- Person A can safely lose faster (larger energy stores)
- Person B is already losing relatively fast

Tables use %/week for this reason.

---

## Summary

The Nutrition Specialist is a **pure algorithmic agent** that:

1. **Analyzes your data**:
   - Weight trends (14 days)
   - Body composition changes (skinfolds/waist/BF%)
   - Nutrition compliance
   - Training progress (from Training Agent)

2. **Applies evidence-based tables**:
   - Table 1: Optimal deficit by body fat %
   - Table 2: Deficit from loss rate
   - Table 3: Optimal surplus by training status

3. **Makes smart decisions**:
   - Detects body recomposition (hidden progress)
   - Estimates YOUR maintenance (not population average)
   - Considers training progress for bulking
   - Provides clear reasoning

4. **Recommends adjustments**:
   - Increase/decrease/maintain calories
   - Updated macro targets
   - Plain-English explanation

**Key Advantages**:
- 100% deterministic (explainable, testable, debuggable)
- Uses YOUR real-world data
- Integrates with Training Specialist
- Fast and free (no LLM calls)

**Remember**: This is a tool to support your decisions, not replace your judgment. Track consistently, trust the process, and adjust based on how you feel and perform!
