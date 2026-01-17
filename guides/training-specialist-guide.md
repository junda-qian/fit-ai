# Training Specialist Agent - Complete Guide

## What Is It?

The Training Specialist is an **intelligent strength training coach** that analyzes your workout performance and prescribes your next session using proven progression algorithms. Think of it as your personal trainer who:

- Tracks session-to-session progress
- Automatically prescribes weight and reps for next workout
- Detects plateaus and regressions
- Recommends deloads and plateau breakers
- Publishes weekly strength summaries (for Nutrition Agent)

**Key Feature**: Like the Nutrition Specialist, this is a **pure algorithmic agent** - NO AI/LLM. All decisions use deterministic if/else logic based on established strength training principles.

## Why Does It Exist?

Effective strength training requires **progressive overload** - consistently increasing the training stimulus. But this is tricky:

**Common Problems**:
- **"When should I add weight?"** → Too soon = failure, too late = wasted time
- **"I failed today's sets - what now?"** → Keep trying? Deload? How much?
- **"I've been stuck at the same weight for weeks"** → Plateau - need a strategy
- **"I'm gaining weight but not getting stronger"** → Nutrition needs to know this!

**The Training Specialist solves these**:
1. **Automates progression decisions** using proven algorithms
2. **Detects problems early** (plateaus, regressions)
3. **Prescribes corrective strategies** (deloads, plateau breakers)
4. **Publishes strength trends** for Nutrition Agent to use

---

## Two Progression Models

The agent supports two well-established progression models. Users choose which model to use per exercise.

### Model 1: Linear Progressive Overload (LP)

**Best for**: Beginners and novices on main compound lifts

**The Rule**: Simple binary decision each session
```
IF hit rep target:
    Add increment next session
ELSE:
    Deload to last successful weight (reactive deload)
```

**Example Progression**:
```
Week 1: 100kg × 5 reps ✓ (hit target!)
Week 2: 102.5kg × 5 reps (add 2.5kg increment)
Week 2: 102.5kg × 5 reps ✓ (hit target!)
Week 3: 105kg × 5 reps (add 2.5kg)
Week 3: 105kg × 4 reps ✗ (missed target!)
Week 4: 102.5kg × 5 reps (reactive deload to last successful weight)
```

**Why it works**:
- Relentless forward pressure (add weight every success)
- Immediate deload on failure (prevents grinding stall)
- Works great for beginners (rapid neural adaptations)

**Why it eventually fails**:
- Increments become too large as you advance
- Binary success/fail is too rigid
- Frequent deloads become frustrating

**When to switch**: When failure rate hits 50%+ → Switch to Rep Range

---

### Model 2: Rep Range Progression

**Best for**: Intermediate/advanced lifters, exercises with small jumps

**The Rule**: Build reps, then add weight
```
IF hit top of rep range:
    Add weight, reset to bottom of range
ELSE IF making rep progress:
    Keep same weight, try for more reps
ELSE IF plateau (2+ sessions no progress):
    Implement plateau breaker
ELSE IF regression (reps decreased):
    Implement plateau breaker
```

**Example Progression** (5-10 rep range):
```
Week 1: 80kg × 7 reps (middle of range)
Week 2: 80kg × 9 reps (building reps)
Week 3: 80kg × 10 reps ✓ (hit top!)
Week 4: 82.5kg × 5 reps (add weight, reset to bottom)
Week 5: 82.5kg × 7 reps (building again)
Week 6: 82.5kg × 8 reps (still building)
Week 7: 82.5kg × 8 reps (same as last week - plateau!)
Week 8: 91kg × 5 reps (plateau breaker: +10% weight, low reps)
```

**Why it works**:
- Smaller effective jumps (gradually earn the next weight increment)
- More volume accumulation (building reps = more sets near failure)
- Less frustrating (always aiming for achievable targets)
- Built-in plateau detection

**Why it's better for advanced lifters**:
- Progress is non-linear at advanced stages
- Allows micro-progression within same weight
- Plateau breakers provide novel stimulus

---

## Core Algorithms

### Algorithm 1: Linear Progressive Rules

**Inputs**:
- Today's first set (weight, reps)
- Rep target (e.g., 5)
- Increment (e.g., 2.5kg)
- Last successful weight

**Decision Tree**:
```python
if first_set.reps >= rep_target:
    # SUCCESS: Hit rep target
    next_weight = first_set.weight + increment
    action = "increase_weight"
    message = f"Hit rep target! Next: {next_weight}kg × {rep_target}"

else:
    # FAILURE: Missed rep target
    next_weight = last_successful_weight  # Deload
    action = "reactive_deload"
    message = f"Missed target. Deload to {next_weight}kg × {rep_target}"
```

**Example 1: Success**
```
Input:
- Today: 100kg × 5 reps
- Rep target: 5
- Increment: 2.5kg

Output:
- Next session: 102.5kg × 5 reps
- Action: increase_weight
- Message: "Hit rep target! Next session: 102.5kg × 5 reps"
```

**Example 2: Failure**
```
Input:
- Today: 105kg × 4 reps (missed!)
- Rep target: 5
- Last successful: 102.5kg

Output:
- Next session: 102.5kg × 5 reps
- Action: reactive_deload
- Message: "Missed target. Deload to 102.5kg × 5 reps"
```

**Reactive Deload Explained**:
- Instead of grinding same weight for weeks (causing CNS fatigue)
- Drop back to last successful weight (typically -1 increment)
- Rebuild momentum from there
- Often break through on second attempt (CNS recovery + confidence)

---

### Algorithm 2: Rep Range Rules

**Inputs**:
- Today's first set (weight, reps)
- Rep target (top of range, e.g., 10 for 5-10 range)
- Increment (e.g., 2.5kg)
- Session history (last 4-8 sessions)
- Current weight

**Decision Tree**:
```python
if first_set.reps >= rep_target:
    # Hit top of range! Add weight
    next_weight = first_set.weight + increment
    action = "increase_weight"
    message = f"Hit rep target! Next: {next_weight}kg × {rep_target}"

else:
    # Didn't hit top of range - check for problems

    if regression_detected(session_history):
        # Reps decreased at same weight
        breaker_weight = current_weight * 1.10  # +10%
        action = "plateau_breaker"
        message = f"Reps regressed. Plateau breaker: {breaker_weight}kg × 5"

    elif plateau_detected(session_history):
        # No progress for 2+ sessions
        breaker_weight = current_weight * 1.10
        action = "plateau_breaker"
        message = f"Plateau detected. Plateau breaker: {breaker_weight}kg × 5"

    else:
        # Normal progression - try for more reps
        next_weight = first_set.weight  # Same weight
        action = "add_reps"
        message = f"Build reps: {next_weight}kg × {rep_target}"
```

**Example 1: Hit Top of Range**
```
Input:
- Today: 80kg × 10 reps (hit target!)
- Rep target: 10
- Increment: 2.5kg

Output:
- Next session: 82.5kg × 10 reps
- Action: increase_weight
```

**Example 2: Building Reps**
```
Input:
- Today: 80kg × 7 reps
- Rep target: 10
- Last session: 80kg × 5 reps

Output:
- Next session: 80kg × 10 reps (try for more reps)
- Action: add_reps
```

**Example 3: Plateau Detected**
```
Input:
- Today: 80kg × 7 reps
- Session history:
  - 4 sessions ago: 80kg × 7 reps
  - 3 sessions ago: 80kg × 7 reps
  - 2 sessions ago: 80kg × 7 reps
  - Last session: 80kg × 7 reps
  - Today: 80kg × 7 reps

Analysis:
- No progress for 5 sessions (stuck at 7 reps)
- Plateau detected!

Output:
- Next session: 88kg × 5 reps (plateau breaker: +10% weight, low reps)
- Action: plateau_breaker
- Message: "Plateau detected (5 sessions). Plateau breaker: 88kg × 5 reps"
```

**Example 4: Regression Detected**
```
Input:
- Today: 80kg × 5 reps
- Last session: 80kg × 8 reps (reps decreased!)

Analysis:
- Reps went DOWN at same weight (8 → 5)
- Regression detected!

Output:
- Next session: 88kg × 5 reps (plateau breaker)
- Action: plateau_breaker
- Message: "Reps regressed. Plateau breaker: 88kg × 5 reps"
```

---

## Plateau Detection

**What is a plateau?**
No progress for 2+ consecutive sessions (Rep Range only)

**Progress is defined as**:
- Weight increased, OR
- Reps increased at same weight

**Algorithm**:
```python
def detect_plateau(recent_sessions, progression_model):
    if progression_model != "rep_range" or len(recent_sessions) < 2:
        return PlateauAnalysis(plateau_detected=False)

    sessions_without_progress = 0

    for i in range(len(recent_sessions) - 1, 0, -1):
        current = recent_sessions[i]
        previous = recent_sessions[i - 1]

        weight_increased = current.weight > previous.weight
        reps_increased = (current.weight == previous.weight and
                         current.reps > previous.reps)

        if weight_increased or reps_increased:
            # Found progress! Stop counting
            break
        else:
            sessions_without_progress += 1

    plateau_detected = sessions_without_progress >= 2

    return PlateauAnalysis(
        plateau_detected=plateau_detected,
        duration_sessions=sessions_without_progress
    )
```

**Example: Plateau**
```
Session history (newest to oldest):
- Today: 80kg × 7 reps
- Session 2: 80kg × 7 reps (no change)
- Session 3: 80kg × 8 reps (progress - reps increased!)

Analysis:
- Sessions without progress: 2 (today and session 2)
- Plateau detected: Yes
```

**Example: Not a Plateau**
```
Session history:
- Today: 80kg × 7 reps
- Session 2: 80kg × 6 reps (reps increased today!)

Analysis:
- Sessions without progress: 0 (made progress today)
- Plateau detected: No
```

---

## Plateau Breaker Strategy

**What is it?**
A planned overload session to shock the system out of adaptation

**How it works**:
```
1. Increase weight by ~10%
2. Drop reps to 5 (heavy, low-rep work)
3. Perform for 1 session
4. Return to normal progression
```

**Why it works**:
- **Novel stimulus**: Different intensity zone (>90% 1RM)
- **Neural adaptation**: Teaches CNS to recruit more motor units
- **Psychological**: Breaking through heavier weights builds confidence
- **Fatigue management**: Low reps = less local muscular fatigue

**Example**:
```
Plateau state:
- Stuck at 80kg × 7 reps for 3 sessions

Plateau breaker:
- 88kg × 5 reps (+10% weight, low reps)

After plateau breaker:
- Return to 80kg × 8-9 reps (often break through!)
```

**Calculation**:
```python
def calculate_plateau_breaker_weight(current_weight):
    increase_pct = 0.10  # 10% increase
    breaker_weight = current_weight * (1 + increase_pct)

    # Round to nearest 2.5kg for practical loading
    breaker_weight = round(breaker_weight / 2.5) * 2.5

    return breaker_weight
```

---

## Model Switching Logic

**Problem**: Linear Progressive works great initially, but eventually increments become too large

**Example**:
```
Novice squatter:
- Week 1: 60kg → 62.5kg (+2.5kg) ✓ Easy
- Week 4: 80kg → 82.5kg (+2.5kg) ✓ Still manageable
- Week 8: 100kg → 102.5kg (+2.5kg) ✗ Starting to fail
- Week 12: 120kg → 122.5kg (+2.5kg) ✗ Failing frequently

Problem: +2.5kg on 60kg = 4.1% jump (easy)
        +2.5kg on 120kg = 2.1% jump (hard!)

Same absolute jump, different relative difficulty.
```

**Solution**: Auto-detect when to switch from Linear → Rep Range

**Trigger**: Failure rate ≥ 50% over last 4 sessions

**Algorithm**:
```python
def suggest_progression_model_switch(failure_rate, increment):
    if failure_rate >= 0.5:
        # Failing 50%+ of sessions
        return ModelSwitchSuggestion(
            from_model="linear",
            to_model="rep_range",
            reason=f"Failure rate {failure_rate*100:.0f}% suggests "
                   f"{increment}kg increment is too large. "
                   f"Switch to Rep Range to build up to next weight."
        )
    return None
```

**Example**:
```
Last 4 sessions:
- 120kg × 5 ✓ (success)
- 122.5kg × 4 ✗ (fail)
- 120kg × 5 ✓ (success after deload)
- 122.5kg × 4 ✗ (fail again)

Analysis:
- Failures: 2 out of 4 sessions
- Failure rate: 50%
- Trigger: YES

Suggestion:
- Switch to Rep Range
- Reason: "Failure rate 50% suggests 2.5kg increment is too large.
          Switch to Rep Range to build up to next weight."
```

**What happens after switch**:
```
User switches to Rep Range:
- Week 1: 120kg × 5 reps (bottom of 5-10 range)
- Week 2: 120kg × 7 reps (building)
- Week 3: 120kg × 9 reps (building)
- Week 4: 120kg × 10 reps ✓ (hit top!)
- Week 5: 122.5kg × 5 reps (add weight, reset)

Now they've EARNED the 122.5kg by accumulating volume!
```

---

## Weekly Strength Summary

**Purpose**: Aggregate strength trends for Nutrition Agent and user dashboard

**Published to**: `training_progress_summaries` table

**Frequency**: Once per week (Sunday or Monday)

**What it includes**:
```python
TrainingProgressSummary(
    user_id="user_123",
    week="2025-W47",  # ISO week format
    overall_strength_trend="improving",  # Key field for Nutrition Agent
    exercises_analyzed=8,
    exercises_progressing=6,
    exercises_plateaued=2,
    exercises_regressing=0,
    avg_weekly_volume_kg=12500.0,
    trend_confidence=0.85,
    data_quality="good"
)
```

**Overall Strength Trend Calculation**:
```python
def calculate_overall_strength_trend(exercises, recommendations):
    # Categorize each exercise
    progressing_count = 0
    plateaued_count = 0
    regressing_count = 0

    for exercise in exercises:
        recent_recs = get_recent_recommendations(exercise)

        # Check hit rate
        hit_rate = count_successes(recent_recs) / len(recent_recs)

        # Check for plateau/regression flags
        if any_regression_detected(recent_recs):
            regressing_count += 1
        elif any_plateau_detected(recent_recs):
            plateaued_count += 1
        elif hit_rate >= 0.7:  # Hit target 70%+ of time
            progressing_count += 1
        else:
            plateaued_count += 1

    # Determine overall trend
    total = progressing_count + plateaued_count + regressing_count
    progressing_pct = progressing_count / total
    regressing_pct = regressing_count / total

    if regressing_pct > 0.3:  # >30% exercises regressing
        return "declining"
    elif progressing_pct >= 0.6:  # ≥60% exercises progressing
        return "improving"
    else:
        return "stable"
```

**Example 1: Improving**
```
User's 8 exercises:
- 6 hitting rep targets 70%+ of time
- 2 plateaued
- 0 regressing

Calculation:
- Progressing: 6/8 = 75%
- Regressing: 0/8 = 0%
- Overall: "improving" (≥60% progressing)
```

**Example 2: Declining**
```
User's 8 exercises:
- 2 progressing
- 3 plateaued
- 3 regressing (reps decreasing)

Calculation:
- Regressing: 3/8 = 37.5%
- Overall: "declining" (>30% regressing)
```

---

## Integration with Nutrition Specialist

**Why Nutrition needs Training data**:

Two people gaining 0.5kg/week on a bulk:
```
Person A:
- Weight: +0.5kg/week
- Strength: improving (hitting targets on all lifts)
- Nutrition decision: Great bulk! Keep calories

Person B:
- Weight: +0.5kg/week
- Strength: stable/declining (missing targets)
- Nutrition decision: Bad bulk! Reduce calories
```

Same weight gain, different quality!

**How it works**:
```
1. Training Specialist publishes weekly summary
   ↓
2. Saved to training_progress_summaries table
   ↓
3. Nutrition Specialist reads latest summary
   ↓
4. Uses overall_strength_trend in bulking algorithm
```

**Example Bulking Decision**:
```python
# In Nutrition Specialist bulking algorithm

strength_summary = get_latest_strength_summary(user_id)
strength_progressing = (
    strength_summary["overall_strength_trend"] == "improving"
)

if weekly_gain_pct > target_max:
    if body_fat_stable and strength_progressing:
        # Gaining fast BUT efficient (muscle gain)
        recommendation = "maintain"
        reasoning = "Gaining weight faster than target, BUT body fat "
                   "stable and strength increasing. Efficient muscle "
                   "gain. Maintain calories."
    else:
        # Gaining fast AND inefficient (fat gain)
        recommendation = "decrease"
        reasoning = "Gaining too fast without strength progress. "
                   "Reduce surplus to optimize muscle-to-fat ratio."
```

**TrainingProgressSummary Model**:
```python
{
    "user_id": "user_123",
    "week": "2025-W47",
    "overall_strength_trend": "improving",  # ← Key for Nutrition
    "exercises_analyzed": 8,
    "exercises_progressing": 6,
    "exercises_plateaued": 2,
    "exercises_regressing": 0,
    "avg_weekly_volume_kg": 12500.0,
    "trend_confidence": 0.85,
    "data_quality": "good",
    "published_at": "2025-11-22T10:00:00Z"
}
```

---

## Practical Examples

### Example 1: Beginner on Linear Progressive

**Profile**:
- Novice lifter
- Barbell squat: Starting at 60kg
- Progression model: Linear
- Rep target: 5
- Increment: 2.5kg

**Week-by-Week**:
```
Week 1:
  Input: 60kg × 5 reps ✓
  Analysis: Hit rep target
  Output: Next session: 62.5kg × 5 reps
  Action: increase_weight

Week 2:
  Input: 62.5kg × 5 reps ✓
  Analysis: Hit rep target
  Output: Next session: 65kg × 5 reps
  Action: increase_weight

Week 3:
  Input: 65kg × 5 reps ✓
  Output: Next session: 67.5kg × 5 reps

... (continues successfully for several weeks)

Week 10:
  Input: 85kg × 5 reps ✓
  Output: Next session: 87.5kg × 5 reps

Week 11:
  Input: 87.5kg × 4 reps ✗ (missed!)
  Analysis: Missed rep target
  Output: Next session: 85kg × 5 reps (reactive deload)
  Action: reactive_deload
  Message: "Missed target. Deload to 85kg × 5 reps"

Week 12:
  Input: 85kg × 5 reps ✓ (success on retry!)
  Output: Next session: 87.5kg × 5 reps
```

**Result**: Clean linear progression with occasional deload-and-retry

---

### Example 2: Intermediate on Rep Range

**Profile**:
- Intermediate lifter
- Barbell bench press: Starting at 80kg
- Progression model: Rep Range
- Rep target: 10 (range: 5-10)
- Increment: 2.5kg

**Week-by-Week**:
```
Week 1:
  Input: 80kg × 6 reps
  Analysis: Below target, no plateau
  Output: 80kg × 10 reps (try for more reps)
  Action: add_reps

Week 2:
  Input: 80kg × 8 reps
  Analysis: Progress made (6 → 8 reps)
  Output: 80kg × 10 reps
  Action: add_reps

Week 3:
  Input: 80kg × 10 reps ✓ (hit top!)
  Analysis: Hit rep target
  Output: 82.5kg × 10 reps (add weight)
  Action: increase_weight

Week 4:
  Input: 82.5kg × 5 reps
  Analysis: Bottom of range (expected)
  Output: 82.5kg × 10 reps
  Action: add_reps

Week 5:
  Input: 82.5kg × 7 reps
  Output: 82.5kg × 10 reps

Week 6:
  Input: 82.5kg × 7 reps
  Analysis: No progress (7 → 7 reps)
  Sessions without progress: 1
  Output: 82.5kg × 10 reps

Week 7:
  Input: 82.5kg × 7 reps
  Analysis: Still no progress (stuck at 7)
  Sessions without progress: 2
  Plateau detected: YES
  Output: 91kg × 5 reps (plateau breaker: +10%)
  Action: plateau_breaker
  Message: "Plateau detected (2 sessions). Plateau breaker: 91kg × 5"

Week 8:
  Input: 91kg × 5 reps ✓ (completed plateau breaker!)
  Analysis: Return to normal progression
  Output: 82.5kg × 10 reps (back to regular weight)

Week 9:
  Input: 82.5kg × 9 reps (breakthrough!)
  Output: 82.5kg × 10 reps

Week 10:
  Input: 82.5kg × 10 reps ✓
  Output: 85kg × 10 reps (add weight!)
```

**Result**: Gradual rep building with plateau breaker intervention

---

### Example 3: Model Switch Suggestion

**Profile**:
- Intermediate lifter (was novice)
- Barbell deadlift: Currently at 140kg
- Progression model: Linear
- Rep target: 5
- Increment: 2.5kg
- Problem: Failing frequently

**Last 4 Sessions**:
```
Session 1:
  Input: 137.5kg × 5 reps ✓
  Output: 140kg × 5 reps

Session 2:
  Input: 140kg × 4 reps ✗
  Output: 137.5kg × 5 reps (deload)

Session 3:
  Input: 137.5kg × 5 reps ✓
  Output: 140kg × 5 reps

Session 4:
  Input: 140kg × 4 reps ✗
  Output: 137.5kg × 5 reps (deload again)

Analysis:
- Failures: 2 out of 4 sessions
- Failure rate: 50%
- Model switch trigger: YES

Model Switch Suggestion:
  From: linear
  To: rep_range
  Reason: "Failure rate 50% suggests 2.5kg increment is too large.
          Switch to Rep Range to build up to next weight."
```

**User switches to Rep Range**:
```
Week 1:
  Input: 137.5kg × 5 reps (bottom of 5-10 range)
  Output: 137.5kg × 10 reps

Week 2:
  Input: 137.5kg × 7 reps
  Output: 137.5kg × 10 reps

Week 3:
  Input: 137.5kg × 9 reps
  Output: 137.5kg × 10 reps

Week 4:
  Input: 137.5kg × 10 reps ✓
  Output: 140kg × 10 reps (add weight - now earned!)

Week 5:
  Input: 140kg × 6 reps (successfully handling 140kg!)
```

**Result**: Successfully broke through 140kg by accumulating volume

---

## Technical Details

### File Structure
```
ai_agents/training_specialist/
├── algorithm.py          # Main progression algorithms
├── tools.py              # Helper functions (plateau detection, etc.)
└── weekly_summary.py     # Weekly aggregate strength summary
```

### Pure Deterministic Algorithm

**NO AI is used**:
```python
# This is the entire algorithm:
if hit_target:
    return add_weight()
elif plateau_detected:
    return plateau_breaker()
else:
    return add_reps()
```

**Benefits**:
- **Explainable**: Every decision traceable
- **Consistent**: Same inputs = same outputs
- **Fast**: <1ms execution
- **Free**: No LLM costs
- **Testable**: Easy unit tests
- **Predictable**: Users know what to expect

---

### Data Models

**Set**:
```python
{
    "weight": 100.0,  # kg
    "reps": 5
}
```

**Session**:
```python
{
    "date": "2025-11-15",
    "first_set": {
        "weight": 100.0,
        "reps": 5
    }
}
```

**ExerciseConfig**:
```python
{
    "progression_model": "linear",  # or "rep_range"
    "rep_target": 5,
    "num_sets": 3,
    "available_increments": [1.25, 2.5, 5.0],
    "selected_increment": 2.5
}
```

**NextSessionRecommendation**:
```python
{
    "exercise_name": "Barbell squat",
    "progression_model": "linear",
    "today_first_set": {"weight": 100, "reps": 5},
    "hit_rep_target": true,
    "plateau_detected": false,
    "regression_detected": false,
    "next_weight": 102.5,
    "next_rep_target": 5,
    "action_type": "increase_weight",
    "message": "Hit rep target! Next: 102.5kg × 5 reps",
    "reasoning": "Linear Progressive: Hit 5 reps (target 5). Adding 2.5kg increment.",
    "model_switch_suggestion": null,
    "confidence": 1.0
}
```

---

### Testing the Algorithm

**Unit tests** (`test_training.py`):
```python
def test_linear_progressive_success():
    """Test LP algorithm when hitting rep target"""
    first_set = Set(weight=100, reps=5)
    config = ExerciseConfig(
        progression_model="linear",
        rep_target=5,
        selected_increment=2.5
    )

    recommendation = analyze_exercise_session(
        exercise_name="Squat",
        sets_logged=[first_set],
        config=config,
        session_history=[],
        current_weight=100,
        last_successful_weight=100
    )

    assert recommendation.next_weight == 102.5
    assert recommendation.action_type == "increase_weight"

def test_rep_range_plateau_detection():
    """Test plateau detection in rep range"""
    # Simulate 3 sessions stuck at same weight/reps
    session_history = [
        Session(date="2025-11-01", first_set=Set(weight=80, reps=7)),
        Session(date="2025-11-08", first_set=Set(weight=80, reps=7)),
        Session(date="2025-11-15", first_set=Set(weight=80, reps=7)),
    ]

    plateau = detect_plateau(session_history, "rep_range")

    assert plateau.plateau_detected == True
    assert plateau.duration_sessions == 2
```

---

## Common Questions

### Q: Which progression model should I use?

**Linear Progressive**:
- ✅ Beginner (< 6 months training)
- ✅ Main compound lifts (squat, bench, deadlift)
- ✅ Want simple binary decision
- ❌ Failing frequently (>50%)

**Rep Range**:
- ✅ Intermediate/advanced
- ✅ Smaller increments needed
- ✅ Stuck on Linear Progressive
- ✅ Isolation exercises
- ❌ Complete beginner (too complex)

**Rule of thumb**: Start with Linear, switch to Rep Range when failure rate hits 50%.

---

### Q: What increment should I use?

**Depends on exercise type**:
```
Big compound lifts (squat, deadlift):
- Beginners: 5kg
- Intermediate: 2.5kg
- Advanced: 1.25kg

Upper body compounds (bench, overhead press):
- Beginners: 2.5kg
- Intermediate: 1.25kg
- Advanced: 0.5kg (microplates)

Isolation exercises:
- All levels: 1.25kg or smaller
```

**When to reduce increment**:
- Failure rate > 50%
- Model switch suggestion appears
- Grinding on same weight for 3+ weeks

---

### Q: What if I regress but it's not a plateau?

**Common causes of one-off regression**:
- Poor sleep
- Stress
- Inadequate nutrition
- Illness/injury

**What the algorithm does**:
```
Linear Progressive:
- Immediate reactive deload (return to last successful weight)

Rep Range:
- If isolated regression: Implements plateau breaker
- Gives CNS a novel stimulus
- Often recovers on next session
```

**What you should do**:
- Trust the algorithm's prescription
- Address recovery factors (sleep, nutrition, stress)
- If persistent regression (3+ sessions): Check program design

---

### Q: How does the plateau breaker work exactly?

**Mechanism**:
```
1. Increase weight ~10%
2. Drop reps to 5
3. Perform heavy, low-rep work (>90% 1RM)
4. Return to normal progression next session
```

**Example**:
```
Stuck at: 80kg × 7 reps (can't get to 10)
Plateau breaker: 88kg × 5 reps
Next session: 80kg × 8-9 reps (often breaks through!)
```

**Why it works**:
- **Neural adaptation**: Heavier loads recruit high-threshold motor units
- **Novel stimulus**: Breaks habitual adaptation
- **Psychological**: Proving you can handle heavier weights
- **Fatigue dissipation**: Lower reps = less local fatigue

---

### Q: What's the difference between plateau and regression?

**Plateau**:
- No progress for 2+ sessions
- Reps stay the SAME at same weight
- Example: 80kg × 7 reps for 3 sessions straight

**Regression**:
- Reps DECREASED from last session
- At same weight
- Example: Last session 80kg × 8, today 80kg × 5

**Why it matters**:
```
Plateau = Adaptation stalled → Plateau breaker
Regression = Fatigue or recovery issue → Plateau breaker + check recovery
```

---

### Q: Can I manually override the prescription?

**Yes!** The algorithm is a guide, not a dictator.

**When to override**:
- Form breakdown (weight too heavy)
- Injury/pain
- Life stress (reduce load)
- Feeling exceptionally strong (optional: push harder)

**When to trust the algorithm**:
- You're impatient (want faster gains)
- Ego lifting (want to impress)
- Fear of deloading

The algorithm removes emotion from the decision.

---

### Q: Why does Nutrition Agent need my strength trends?

**During bulking**, weight gain quality depends on strength:
```
Gaining 0.5kg/week + strength improving = muscle gain ✓
Gaining 0.5kg/week + strength stagnant = fat gain ✗
```

**What Nutrition does with this**:
```python
if weight_gaining_fast and body_fat_increasing:
    if strength_improving:
        # Good bulk - efficient muscle gain
        recommendation = "maintain calories"
    else:
        # Bad bulk - just getting fatter
        recommendation = "decrease calories"
```

**Published weekly** to `training_progress_summaries` table for Nutrition Agent to read.

---

## Summary

The Training Specialist is a **pure algorithmic agent** that:

1. **Automates progression decisions**:
   - Linear Progressive: Hit target → add weight, miss → deload
   - Rep Range: Build reps → add weight, plateau → plateau breaker

2. **Detects problems early**:
   - Plateau: No progress 2+ sessions
   - Regression: Reps decreased
   - Model inefficiency: Failure rate ≥50%

3. **Prescribes corrective strategies**:
   - Reactive deload (Linear Progressive)
   - Plateau breaker (+10% weight, low reps)
   - Model switching (Linear → Rep Range)

4. **Publishes weekly strength summaries**:
   - Overall trend: improving/stable/declining
   - Exercise breakdowns
   - Consumed by Nutrition Agent for bulk assessment

**Key Advantages**:
- 100% deterministic (explainable, testable)
- Based on proven progression principles
- No AI/LLM (fast, free, consistent)
- Integrates with Nutrition Agent
- Removes emotion from training decisions

**Remember**: Progressive overload is the key to strength gains. The algorithm ensures you're always applying the right stimulus - not too much (overtraining), not too little (undertraining), just enough to force adaptation!
