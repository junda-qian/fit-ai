# Training Specialist Agent Specification

## Overview

The Training Specialist Agent is an **event-driven, post-workout AI agent** that analyzes completed workout sessions and prescribes the next session's parameters based on algorithmic progression rules.

**Purpose**: Provides session-to-session progression recommendations based on logged workout performance

**Trigger**: Event-driven - invoked after each workout log (NOT scheduled weekly)

**Key Design Principle**:
> This agent analyzes what you DID and prescribes what to DO NEXT. It operates on a per-exercise, per-session basis with algorithmic rules.

---

## Training Philosophy: User-Driven Autoregulation

The app follows a **user-controlled, autoregulated** training philosophy where users execute their workouts and make real-time decisions (like autoregulating weight increases mid-session). The Training Agent's role is to **analyze completed sessions and prescribe the next session's parameters** based on algorithmic progression rules.

Users do NOT follow pre-planned programs. Instead, they:
1. Have specific exercises with rep targets
2. Follow simple progression rules (Linear Progressive or Rep Range)
3. Make session-to-session adjustments based on performance
4. The Training Agent tracks patterns and applies rules automatically

---

## Two Invocation Modes

The Training Specialist Agent runs in two modes:

### Mode 1: Event-Driven (Post-Workout)

**Trigger**: After each workout log
**Purpose**: Session-to-session progression analysis

```
┌─────────────────────────────────────────────────────┐
│   User logs workout via /api/workouts/log           │
└────────────────────┬────────────────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────────────────┐
│   Backend saves workout + invokes Training Agent    │
│   (async Lambda invocation - don't block user)     │
└────────────────────┬────────────────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────────────────┐
│       Training Specialist Agent                      │
│  FOR EACH EXERCISE in workout:                      │
│  1. Get exercise config (progression model, etc)    │
│  2. Analyze first set vs rep target                 │
│  3. Apply Linear/Rep Range progression rules        │
│  4. Prescribe next session (weight, reps, action)   │
│  5. Detect plateaus/regressions                     │
│  6. Update user_exercises table                     │
│  7. Store training recommendation                   │
└────────────────────┬────────────────────────────────┘
                     │
                     ▼
              ┌─────────────────────┐
              │   user_exercises     │
              │ (next_session update)│
              │                      │
              │training_recommendations│
              └─────────────────────┘
```

### Mode 2: Weekly Scheduled (Aggregate Analysis)

**Trigger**: EventBridge cron (Monday 5:55 AM UTC)
**Purpose**: Publish weekly strength trend summary for other agents/features

```
┌─────────────────────────────────────────────────────┐
│   EventBridge Scheduler (Monday 5:55 AM)            │
└────────────────────┬────────────────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────────────────┐
│       Training Specialist Agent (Weekly Mode)        │
│  FOR EACH ACTIVE USER:                              │
│  1. Get recent training recommendations (14 days)   │
│  2. Count exercises: progressing/plateaued/regressing│
│  3. Calculate overall strength trend                │
│  4. Calculate aggregate volume metrics              │
│  5. Publish to training_progress_summaries table    │
└────────────────────┬────────────────────────────────┘
                     │
                     ▼
              ┌──────────────────────────┐
              │training_progress_summaries│
              │  (consumed by Nutrition   │
              │   Agent, Dashboard, etc)  │
              └──────────────────────────┘
```

**Why 5:55 AM?**
Runs 5 minutes before Nutrition Agent (6:00 AM) to ensure fresh strength data is available.

---

## Progression Model 1: Linear Progressive

**Principle**: Linear progression in weight on the first work set. Every session you hit your rep target, add the increment to next session's weight.

### How It Works

- Only the **first work set** is the progression benchmark
- Subsequent sets' reps don't influence weight progression
- Hit rep target in set 1 → add increment next session
- Miss rep target in set 1 → implement reactive deload

### Example

```
Bench Press: 3 sets, rep target 11, increment 2.5kg

Session 1: 120kg x 11, 8, 7  → Hit target ✓
Session 2: 122.5kg x 11, 7, 6  → Hit target ✓
Session 3: 125kg x 11, 9, 6  → Hit target ✓
Session 4: 127.5kg x 10  → Missed target ✗ (reactive deload)
Session 5: 125kg x 11  → Retry previous successful weight
Session 6: 127.5kg x 11  → Success, continue
```

### Reactive Deloads

If you miss your rep target in the first set:
1. Replace remaining sets with low-rep explosive speed work (3-5 reps at 60-70% 1RM)
2. Mark the session as needing attention (red flag)
3. Next session: return to the weight you previously hit for the rep target
4. Retry the failed weight after successful completion

### Autoregulated Progression

If after set 1 you feel you can still hit the rep target with more weight, increase within the same session to progress faster than 1 increment per session.

---

## Progression Model 2: Rep Range Progression

**Principle**: Progress either in weight OR reps. Hit rep target → add weight. Don't hit rep target → add reps next session.

### How It Works

- First set is the progression benchmark
- When you hit rep target → increase weight by increment next session
- When you don't hit rep target → keep same weight, try for more reps next session
- Experience natural rep decrease when weight increases
- Build reps back up to rep target before adding more weight

### Example

```
Squat: rep target 11, increment 2.5kg

Session 1: 100kg x 11  → Hit target, add weight
Session 2: 102.5kg x 9  → Didn't hit target, add reps
Session 3: 102.5kg x 10  → Added a rep, try again
Session 4: 102.5kg x 11  → Hit target, add weight
Session 5: 105kg x 8  → Didn't hit target, add reps
...
```

### Plateau Breakers

If you don't progress for 2+ sessions (same reps at same weight):
1. **Plateau detected**
2. Next session: increase weight by ~10% (up to max ~3RM for compounds, ~5RM for isolation)
3. Do lower-volume, high-intensity work (3-5 reps max)
4. Then return to the plateaued weight and try to increase reps again

### Reactive Deloads

If reps **regress** (go down instead of up):
1. Replace remaining sets with speed work (3-5 reps at 60-70% 1RM)
2. Next session: implement plateau breaker
3. Then return to building reps

### Example with Plateau Breaker

```
Session 1: 102.5kg x 10
Session 2: 102.5kg x 10  → Plateau detected
Session 3: 113kg x 5  → Plateau breaker (~10% increase)
Session 4: 102.5kg x 11  → Back to plateau weight, hit target
Session 5: 105kg x 8  → Add weight, continue
```

---

## When to Switch Between Models

### Start with Linear Progressive when:
- Your available increment is small enough for consistent progress
- You can hit rep target most sessions (>70% success rate)

### Switch to Rep Range Progression when:
- Your increment becomes too large (failing to hit rep target >50% of sessions)
- You need to "build up" to the next weight increment
- Linear progression causes too many reactive deloads

### Example Scenario

```
User has bench press with 5kg increment (smallest plates available)

Week 1-4: 100kg → 105kg → 110kg → 115kg (linear, hitting targets)
Week 5: 120kg x fail  → 115kg retry → 120kg x fail again
Week 6: Agent suggests "Your 5kg increment is too large. Switch to Rep Range."

Rep Range mode:
Session 1: 115kg x 11 ✓
Session 2: 120kg x 9 (build reps)
Session 3: 120kg x 10 (build reps)
Session 4: 120kg x 11 ✓ (now ready for 125kg)
```

### Switch back to Linear Progressive when:
- You acquire smaller increments (e.g., buy 1.25kg micro-plates)
- Your strength increases enough that the increment is manageable again

---

## Input Context (Per Workout)

```python
{
    # Exercise configuration (from user_exercises table)
    "exercise_config": {
        "progression_model": "rep_range",  # "linear" or "rep_range"
        "rep_target": 11,
        "num_sets": 3,
        "available_increments": [1.25, 2.5, 5],  # kg (user's equipment)
        "selected_increment": 2.5
    },

    # Today's logged sets
    "today_sets": [
        {"weight": 100, "reps": 11},
        {"weight": 100, "reps": 8},
        {"weight": 100, "reps": 7}
    ],

    # Recent session history (last 4-8 sessions of this exercise)
    "session_history": [
        {"date": "2025-10-20", "first_set": {"weight": 97.5, "reps": 11}},
        {"date": "2025-10-23", "first_set": {"weight": 100, "reps": 9}},
        {"date": "2025-10-27", "first_set": {"weight": 100, "reps": 10}},
        # Today's session will be added after analysis
    ],

    # Current exercise state (from user_exercises table)
    "current_state": {
        "current_weight": 100,
        "last_successful_weight": 97.5,  # Last weight where rep target was hit
        "plateau_count": 0  # Number of consecutive sessions without progress
    }
}
```

---

## Responsibilities

- **Analyze first set performance** against rep target
- **Apply progression rules** (linear or rep range) algorithmically
- **Detect plateaus** (no progress for 2+ sessions in rep range)
- **Detect regressions** (reps decreased from last session)
- **Prescribe next session** (weight, target reps, action type)
- **Flag reactive deloads** when performance regresses significantly
- **Suggest plateau breakers** when stalled
- **Recommend progression model switches** when increment becomes issue

---

## Function Tools

```python
@function_tool
async def analyze_exercise_session(
    wrapper: RunContextWrapper[FitnessContext],
    exercise: str,
    sets_logged: List[Set],
    config: ExerciseConfig,
    history: List[Session]
) -> NextSessionRecommendation:
    """
    Main analysis function that routes to appropriate progression model.
    """
    # Returns: NextSessionRecommendation with next session prescription
```

```python
@function_tool
async def apply_linear_progressive_rules(
    wrapper: RunContextWrapper[FitnessContext],
    first_set: Set,
    rep_target: int,
    increment: float,
    last_session: Session
) -> NextSession:
    """
    Apply Linear Progressive rules.

    Rules:
    - Hit rep target in first set → add increment
    - Miss rep target → reactive deload (return to last successful weight)
    """
    # Returns: NextSession with weight, reps, action
```

```python
@function_tool
async def apply_rep_range_rules(
    wrapper: RunContextWrapper[FitnessContext],
    first_set: Set,
    rep_target: int,
    increment: float,
    history: List[Session]
) -> NextSession:
    """
    Apply Rep Range Progression rules.

    Rules:
    - Hit rep target → add weight
    - Didn't hit rep target → try for more reps next session
    - Plateau (2+ sessions no progress) → plateau breaker
    - Regression (reps decreased) → reactive deload + plateau breaker
    """
    # Returns: NextSession with weight, reps, action
```

```python
@function_tool
async def detect_plateau(
    wrapper: RunContextWrapper[FitnessContext],
    recent_sessions: List[Session],
    progression_model: str
) -> PlateauAnalysis:
    """
    Detect if user is plateaued (no progress for 2+ sessions).
    Only applies to Rep Range progression.
    """
    # Returns: PlateauAnalysis with plateau detected flag, duration
```

```python
@function_tool
async def detect_regression(
    wrapper: RunContextWrapper[FitnessContext],
    today_reps: int,
    last_session_reps: int
) -> bool:
    """
    Detect if reps decreased from last session (at same weight).
    """
    # Returns: bool (true if regressed)
```

```python
@function_tool
async def calculate_plateau_breaker_weight(
    wrapper: RunContextWrapper[FitnessContext],
    current_weight: float,
    exercise_type: str
) -> float:
    """
    Calculate plateau breaker weight (~10% increase).

    Max safe increase:
    - Compound exercises: ~3RM territory
    - Isolation exercises: ~5RM territory
    """
    # Returns: float (plateau breaker weight)
```

```python
@function_tool
async def suggest_progression_model_switch(
    wrapper: RunContextWrapper[FitnessContext],
    failure_rate: float,
    increment: float
) -> ModelSwitchSuggestion:
    """
    Suggest switching progression models if increment is causing issues.

    Trigger:
    - Failure rate > 50% in Linear Progressive
    - Multiple consecutive failures
    """
    # Returns: ModelSwitchSuggestion or None
```

```python
@function_tool
async def calculate_1rm(
    wrapper: RunContextWrapper[FitnessContext],
    weight: float,
    reps: int
) -> float:
    """
    Calculate estimated 1 rep max using Epley formula.
    Used for plateau breaker calculations.
    """
    if reps == 1:
        return weight
    return weight * (1 + reps / 30.0)
```

---

## Structured Output

```python
class NextSessionRecommendation(BaseModel):
    exercise_name: str
    progression_model: str  # "linear" or "rep_range"

    # Today's analysis
    today_first_set: Set  # {weight: 100, reps: 11}
    hit_rep_target: bool
    plateau_detected: bool
    regression_detected: bool
    reactive_deload_implemented: bool

    # Next session prescription (algorithmic)
    next_weight: float
    next_rep_target: int
    action_type: str  # "increase_weight", "add_reps", "plateau_breaker", "reactive_deload", "retry"

    # User-facing messages
    message: str  # "Hit rep target! Next session: 102.5kg x 11"
    reasoning: str

    # Optional suggestions
    model_switch_suggestion: Optional[ModelSwitchSuggestion]
    increment_adjustment_suggestion: Optional[float]

    confidence: float


class Set(BaseModel):
    weight: float
    reps: int


class Session(BaseModel):
    date: str
    first_set: Set


class ModelSwitchSuggestion(BaseModel):
    from_model: str
    to_model: str
    reason: str
```

---

## API Integration

```python
# After user logs workout via /api/workouts/log
# Backend invokes Training Specialist Lambda asynchronously:

lambda_client.invoke(
    FunctionName="fitness-training-specialist",
    InvocationType="Event",  # Async (don't block user)
    Payload=json.dumps({
        "user_id": user_id,
        "workout_id": workout_id,
        "exercises": exercises_logged
    })
)
```

### API Endpoint: `/api/workouts/log`

```python
# backend/server.py

@app.post("/api/workouts/log")
async def log_workout(workout: WorkoutLog):
    """
    User logs completed workout.
    Saves to DynamoDB and triggers Training Agent asynchronously.
    """
    # 1. Save workout to DynamoDB
    workout_id = str(uuid.uuid4())
    db.workout_logs.create({
        "user_id": workout.user_id,
        "workout_id": workout_id,
        "exercises": workout.exercises,
        "timestamp": datetime.utcnow().isoformat()
    })

    # 2. Invoke Training Specialist Lambda (async - don't block)
    lambda_client.invoke(
        FunctionName="fitness-training-specialist",
        InvocationType="Event",
        Payload=json.dumps({
            "user_id": workout.user_id,
            "workout_id": workout_id,
            "exercises": workout.exercises
        })
    )

    # 3. Return immediately to user
    return {
        "workout_id": workout_id,
        "message": "Workout logged! Analyzing your session..."
    }
```

---

## Weekly Strength Summary Publication

### Purpose

The Training Agent publishes aggregate strength trend metrics that:
- **Nutrition Agent** uses to assess bulk effectiveness
- **Dashboard** displays for user progress tracking
- **Communication Agent** includes in weekly summaries
- **Coach Orchestrator** references when answering questions

### Published Data Structure

Training Agent writes to `training_progress_summaries` table:

```python
{
    "user_id": "user_123",
    "week": "2025-W47",  # ISO week format (YYYY-Www)
    "published_by": "training_agent",
    "published_at": "2025-11-22T05:55:00Z",

    # Overall strength trend (Training Agent's expert assessment)
    "overall_strength_trend": "improving",  # "improving" | "stable" | "declining" | "insufficient_data"

    # Exercise-level breakdown
    "exercises_analyzed": 5,
    "exercises_progressing": 4,  # Hit rep targets consistently
    "exercises_plateaued": 1,     # No progress for 2+ sessions
    "exercises_regressing": 0,    # Performance decreased

    # Optional aggregate metrics
    "avg_weekly_volume_kg": 12500,  # Total kg lifted
    "trend_confidence": 0.85,  # 0.0-1.0 (based on data quality)

    # Context for the assessment
    "days_of_data": 14,
    "workouts_completed": 3,
    "data_quality": "good"  # "good" | "fair" | "poor"
}
```

### Algorithm: Calculate Overall Strength Trend

```python
def calculate_overall_strength_trend(user_id: str, days: int = 14) -> dict:
    """
    Analyze recent workouts to determine overall strength trend.

    This is the Training Agent's expert assessment based on session-to-session
    progression data collected from the event-driven flow.
    """
    # Get all user exercises
    exercises = db.user_exercises.find_by_user_id(user_id)

    # Get recent training recommendations (last 14 days)
    recent_recommendations = db.training_recommendations.find_recent(
        user_id=user_id,
        days=days
    )

    if len(recent_recommendations) < 2:
        return {
            "overall_strength_trend": "insufficient_data",
            "exercises_analyzed": 0,
            "exercises_progressing": 0,
            "exercises_plateaued": 0,
            "exercises_regressing": 0,
            "data_quality": "poor"
        }

    # Count exercises in each state
    progressing_count = 0
    plateaued_count = 0
    regressing_count = 0

    for exercise in exercises:
        recent_recs = [
            r for r in recent_recommendations
            if r["exercise_name"] == exercise["exercise_name"]
        ]

        if not recent_recs:
            continue

        # Check if exercise is progressing
        hit_target_count = sum(
            1 for r in recent_recs
            if r["today_analysis"]["hit_rep_target"]
        )
        plateau_detected = any(
            r["today_analysis"]["plateau_detected"]
            for r in recent_recs
        )
        regression_detected = any(
            r["today_analysis"]["regression_detected"]
            for r in recent_recs
        )

        if regression_detected:
            regressing_count += 1
        elif plateau_detected:
            plateaued_count += 1
        elif hit_target_count >= len(recent_recs) * 0.7:  # Hit target in 70%+ of sessions
            progressing_count += 1
        else:
            plateaued_count += 1

    total = progressing_count + plateaued_count + regressing_count

    if total == 0:
        return {
            "overall_strength_trend": "insufficient_data",
            "exercises_analyzed": 0,
            "exercises_progressing": 0,
            "exercises_plateaued": 0,
            "exercises_regressing": 0,
            "data_quality": "poor"
        }

    # Determine overall trend
    progressing_pct = progressing_count / total
    regressing_pct = regressing_count / total

    if regressing_pct > 0.3:  # >30% of exercises regressing
        overall_trend = "declining"
    elif progressing_pct >= 0.6:  # >=60% of exercises progressing
        overall_trend = "improving"
    else:
        overall_trend = "stable"

    return {
        "overall_strength_trend": overall_trend,
        "exercises_analyzed": total,
        "exercises_progressing": progressing_count,
        "exercises_plateaued": plateaued_count,
        "exercises_regressing": regressing_count,
        "trend_confidence": min(total / 5.0, 1.0),  # More exercises = higher confidence
        "data_quality": "good" if total >= 3 else "fair"
    }
```

### Lambda Handler (Weekly Mode)

```python
# ai_agents/training_specialist/lambda_handler.py

def lambda_handler(event, context):
    """
    Training Specialist Agent entry point.

    Handles both:
    1. Event-driven (post-workout): Session-to-session progression
    2. Weekly scheduled: Aggregate strength trend publication
    """

    # Determine invocation mode
    if "source" in event and event["source"] == "aws.events":
        # Weekly scheduled invocation from EventBridge
        return handle_weekly_summary(event, context)
    else:
        # Event-driven invocation from workout log
        return handle_post_workout_analysis(event, context)


def handle_weekly_summary(event, context):
    """
    Weekly scheduled run: Publish strength trend summaries for all active users.
    Runs Monday 5:55 AM UTC (before Nutrition Agent at 6:00 AM).
    """
    users = db.user_profiles.find_all_active()

    summaries_published = 0

    for user in users:
        # Calculate overall strength trend
        trend_data = calculate_overall_strength_trend(user["user_id"], days=14)

        # Calculate aggregate volume
        recent_workouts = db.workout_logs.find_recent(user["user_id"], days=7)
        total_volume = sum(
            set["weight"] * set["reps"]
            for workout in recent_workouts
            for exercise in workout["exercises"]
            for set in exercise["sets"]
        )

        # Publish to training_progress_summaries table
        db.training_progress_summaries.create({
            "user_id": user["user_id"],
            "week": get_iso_week(),  # "2025-W47"
            "published_by": "training_agent",
            "published_at": datetime.utcnow().isoformat(),
            "overall_strength_trend": trend_data["overall_strength_trend"],
            "exercises_analyzed": trend_data["exercises_analyzed"],
            "exercises_progressing": trend_data["exercises_progressing"],
            "exercises_plateaued": trend_data["exercises_plateaued"],
            "exercises_regressing": trend_data["exercises_regressing"],
            "avg_weekly_volume_kg": total_volume,
            "trend_confidence": trend_data["trend_confidence"],
            "days_of_data": 14,
            "workouts_completed": len(recent_workouts),
            "data_quality": trend_data["data_quality"]
        })

        summaries_published += 1

    return {
        "statusCode": 200,
        "mode": "weekly_summary",
        "summaries_published": summaries_published
    }


def handle_post_workout_analysis(event, context):
    """
    Event-driven run: Analyze workout and prescribe next session.
    (Existing implementation - already documented above)
    """
    # ... existing post-workout logic ...
```

### Benefits of This Approach

✅ **Training Agent owns all strength analysis** - Clear domain ownership
✅ **Loose coupling** - Other agents read published data, not raw workout logs
✅ **Single source of truth** - Training Agent is the expert on strength trends
✅ **Reusable** - Dashboard, reports, Communication Agent all consume same data
✅ **Simple scheduling** - One EventBridge cron rule
✅ **Aligned timing** - Nutrition Agent always has fresh strength data

---

## DynamoDB Schema

### New Table: `user_exercises`

Stores exercise configuration and next session prescription (updated by Training Agent after each workout).

```python
{
    "user_id": "string",  # Partition key
    "exercise_name": "bench_press",  # Sort key

    # Exercise configuration (set by user)
    "progression_model": "rep_range",  # "linear" or "rep_range"
    "rep_target": 11,
    "num_sets": 3,
    "available_increments": [1.25, 2.5, 5],  # kg (user's equipment)
    "selected_increment": 2.5,

    # Current state
    "current_weight": 102.5,
    "last_successful_weight": 100,  # Last weight where rep target was hit
    "plateau_count": 0,  # Number of consecutive sessions without progress

    # Next session prescription (updated by Training Agent after each workout)
    "next_session": {
        "weight": 102.5,
        "target_reps": 11,
        "action": "add_reps",  # "increase_weight", "add_reps", "plateau_breaker", "reactive_deload", "retry"
        "message": "Try to hit 11 reps today with 102.5kg",
        "reasoning": "Last session hit 10 reps. Build up to rep target before adding weight."
    },

    "created_at": "2025-01-15",
    "updated_at": "2025-11-08"
}
```

### New Table: `training_progress_summaries`

Stores weekly aggregate strength trend summaries published by Training Agent.
This data is consumed by Nutrition Agent, Dashboard, Communication Agent, etc.

```python
{
    "user_id": "string",  # Partition key
    "week": "2025-W47",  # Sort key (ISO week format YYYY-Www)

    # Publication metadata
    "published_by": "training_agent",
    "published_at": "2025-11-22T05:55:00Z",

    # Overall strength trend (Training Agent's expert assessment)
    "overall_strength_trend": "improving",  # "improving" | "stable" | "declining" | "insufficient_data"

    # Exercise-level breakdown
    "exercises_analyzed": 5,
    "exercises_progressing": 4,  # Hit rep targets consistently (>=70% success rate)
    "exercises_plateaued": 1,     # No progress for 2+ sessions
    "exercises_regressing": 0,    # Performance decreased

    # Aggregate metrics
    "avg_weekly_volume_kg": 12500,  # Total kg lifted per week
    "trend_confidence": 0.85,  # 0.0-1.0 (based on data quality and # exercises)

    # Context
    "days_of_data": 14,
    "workouts_completed": 3,
    "data_quality": "good"  # "good" | "fair" | "poor"
}
```

### New Table: `training_recommendations`

Stores agent analysis per workout (audit trail).

```python
{
    "user_id": "string",  # Partition key
    "recommendation_id": "uuid",  # Sort key (or timestamp)
    "workout_id": "uuid",  # FK to workout_logs
    "exercise_name": "bench_press",
    "analyzed_at": "2025-11-08T14:30:00Z",

    # Today's analysis
    "today_analysis": {
        "first_set": {"weight": 100, "reps": 11},
        "hit_rep_target": true,
        "plateau_detected": false,
        "regression_detected": false,
        "reactive_deload_implemented": false
    },

    # Next session prescription
    "next_session": {
        "weight": 102.5,
        "target_reps": 11,
        "action": "increase_weight",
        "reasoning": "Hit rep target - adding 2.5kg increment"
    },

    # Optional suggestions
    "suggestions": {
        "model_switch": null,  # or {"from": "linear", "to": "rep_range", "reason": "..."}
        "increment_adjustment": null
    }
}
```

---

## Lambda Handler Example

```python
# ai_agents/training_specialist/lambda_handler.py

def lambda_handler(event, context):
    """
    Invoked after each workout log.
    Analyzes each exercise and prescribes next session.
    """
    user_id = event["user_id"]
    workout_id = event["workout_id"]
    exercises = event["exercises"]

    recommendations = []

    for exercise in exercises:
        # 1. Get exercise config from user_exercises table
        exercise_config = db.user_exercises.find_one({
            "user_id": user_id,
            "exercise_name": exercise["name"]
        })

        # 2. Get recent session history
        session_history = get_session_history(user_id, exercise["name"], limit=8)

        # 3. Analyze first set performance
        first_set = exercise["sets"][0]

        # 4. Apply progression rules
        if exercise_config["progression_model"] == "linear":
            recommendation = apply_linear_progressive_rules(
                first_set,
                exercise_config["rep_target"],
                exercise_config["selected_increment"],
                session_history[-1] if session_history else None
            )
        else:  # rep_range
            recommendation = apply_rep_range_rules(
                first_set,
                exercise_config["rep_target"],
                exercise_config["selected_increment"],
                session_history
            )

        # 5. Check for plateau/regression
        if exercise_config["progression_model"] == "rep_range":
            plateau = detect_plateau(session_history, "rep_range")
            if plateau.detected:
                recommendation.plateau_detected = True
                # Prescribe plateau breaker
                recommendation.action_type = "plateau_breaker"
                recommendation.next_weight = calculate_plateau_breaker_weight(
                    exercise_config["current_weight"],
                    exercise["type"]
                )

        # 6. Update user_exercises table with next session
        db.user_exercises.update(
            {"user_id": user_id, "exercise_name": exercise["name"]},
            {
                "current_weight": first_set["weight"],
                "last_successful_weight": first_set["weight"] if recommendation.hit_rep_target else exercise_config["last_successful_weight"],
                "plateau_count": recommendation.plateau_detected ? exercise_config["plateau_count"] + 1 : 0,
                "next_session": {
                    "weight": recommendation.next_weight,
                    "target_reps": recommendation.next_rep_target,
                    "action": recommendation.action_type,
                    "message": recommendation.message,
                    "reasoning": recommendation.reasoning
                },
                "updated_at": datetime.utcnow().isoformat()
            }
        )

        # 7. Store training recommendation (audit trail)
        db.training_recommendations.create({
            "user_id": user_id,
            "recommendation_id": str(uuid.uuid4()),
            "workout_id": workout_id,
            "exercise_name": exercise["name"],
            "analyzed_at": datetime.utcnow().isoformat(),
            "today_analysis": {
                "first_set": first_set,
                "hit_rep_target": recommendation.hit_rep_target,
                "plateau_detected": recommendation.plateau_detected,
                "regression_detected": recommendation.regression_detected
            },
            "next_session": {
                "weight": recommendation.next_weight,
                "target_reps": recommendation.next_rep_target,
                "action": recommendation.action_type,
                "reasoning": recommendation.reasoning
            },
            "suggestions": {
                "model_switch": recommendation.model_switch_suggestion,
                "increment_adjustment": recommendation.increment_adjustment_suggestion
            }
        })

        recommendations.append(recommendation)

    return {
        "statusCode": 200,
        "recommendations_generated": len(recommendations)
    }
```

---

## Key Advantages

1. **Simple, algorithmic rules** - No complex AI reasoning needed for progression
2. **Immediate feedback** - User sees next session prescription right after logging
3. **Autoregulated progression** - User can adjust mid-session based on feel
4. **Plateau detection** - Automatically identifies when progress stalls
5. **Model switching** - Suggests switching progression models when appropriate
6. **Per-exercise customization** - Each exercise has its own progression model and increment
7. **Audit trail** - Every recommendation is stored for analysis
8. **Event-driven** - No waiting for weekly analysis, immediate response to performance

---

## Lambda Deployment

**Function name**: `fitness-training-specialist`

**Runtime**: Python 3.11+

**Trigger**: Async invocation from `/api/workouts/log` endpoint

**Environment variables**:
- `DYNAMODB_TABLE_PREFIX`: Table name prefix
- `BEDROCK_MODEL_ID`: Claude model ID (if using AI for edge cases)

**IAM Permissions**:
- DynamoDB: Read/Write access to `user_exercises`, `training_recommendations`, `workout_logs`
- (Optional) Bedrock: Invoke model for complex scenarios

---

## Frontend Integration

### Display Next Session Prescription

```tsx
// components/WorkoutPage.tsx

export default function WorkoutPage() {
  const [exercises, setExercises] = useState([])

  useEffect(() => {
    // Fetch user's exercises with next session prescriptions
    fetchExercises()
  }, [])

  async function fetchExercises() {
    const res = await fetch(`/api/exercises/${currentUser.id}`)
    const data = await res.json()
    setExercises(data)
  }

  return (
    <div className="workout-page">
      <h2>Today's Workout</h2>

      {exercises.map(exercise => (
        <ExerciseCard key={exercise.exercise_name}>
          <h3>{exercise.exercise_name}</h3>

          {/* Show next session prescription */}
          <div className="next-session-prescription">
            <strong>Next Session:</strong>
            <p>{exercise.next_session.message}</p>
            <div className="prescription-details">
              <span>Weight: {exercise.next_session.weight}kg</span>
              <span>Target Reps: {exercise.next_session.target_reps}</span>
              <span>Action: {exercise.next_session.action}</span>
            </div>
            <p className="reasoning">{exercise.next_session.reasoning}</p>
          </div>

          {/* Log workout form */}
          <WorkoutLogForm exercise={exercise} />
        </ExerciseCard>
      ))}
    </div>
  )
}
```

### After Workout Logged

```tsx
// After user submits workout log

async function logWorkout(workout) {
  const res = await fetch("/api/workouts/log", {
    method: "POST",
    body: JSON.stringify(workout)
  })

  const data = await res.json()

  // Show success message
  showToast("Workout logged! Analyzing your session...")

  // Refresh exercises to show updated next session prescription
  setTimeout(() => {
    fetchExercises()
  }, 2000)  // Give Training Agent time to process
}
```
