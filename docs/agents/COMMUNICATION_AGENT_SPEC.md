# Communication Specialist Agent Specification

## Overview

The Communication Specialist Agent is an **AI-powered weekly messaging agent** that translates technical recommendations into personalized, motivating communications for users.

**Purpose**: Generate personalized weekly progress summaries with nutrition and training feedback

**Trigger**: EventBridge cron (Monday 6:05 AM UTC - after Nutrition/Training agents complete) or SNS topic subscription

**Key Design Principle**:
> This agent focuses purely on user experience and communication. It does NOT make nutrition or training decisions - it explains and motivates based on what other agents decided.

---

## Why a Separate Communication Agent?

### 1. **Clear Separation of Concerns**
- **Nutrition Agent** → Makes nutritional decisions (deterministic)
- **Training Agent** → Makes training decisions (deterministic)
- **Communication Agent** → Makes communication decisions (AI-powered)

### 2. **Reusability**
The Communication Agent handles messages for:
- Nutrition plan changes
- Training adjustments
- Weekly summaries (even when no changes occur)
- Milestone celebrations
- Educational tips
- Motivation during plateaus

### 3. **Independent Evolution**
- Improve nutrition/training algorithms → No impact on messaging
- A/B test communication styles
- Support multiple languages
- Personalize based on user preferences

### 4. **Cost Efficiency**
- Only ONE AI agent needed for communication ($0.02/user/week)
- Nutrition and Training agents remain deterministic (free)
- Total: ~$20/month for 1000 users

---

## Weekly Communication Flow

```
┌─────────────────────────────────────────────────────┐
│     EventBridge (Monday 6:05 AM UTC)                 │
│     Triggered AFTER Nutrition/Training agents        │
└────────────────────┬────────────────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────────────────┐
│         Communication Specialist Agent               │
│  FOR EACH USER WITH PENDING COMMUNICATION:          │
│  1. Read weekly analysis from Nutrition Agent       │
│  2. Read training recommendations from Training Agent│
│  3. Gather user history (past weeks, achievements)  │
│  4. Calculate metrics (streak, compliance, progress)│
│  5. Generate personalized message using AI          │
│     - Acknowledge progress                          │
│     - Explain nutrition changes                     │
│     - Review training performance                   │
│     - Motivate for upcoming week                    │
│     - Provide tips/education                        │
│  6. Store communication in database                 │
│  7. Mark analysis as communicated                   │
└────────────────────┬────────────────────────────────┘
                     │
                     ▼
              ┌─────────────────┐
              │weekly_communications│
              │weekly_analyses   │
              │  (update flags)  │
              └─────────────────┘
```

---

## Input Context

The agent gathers data from multiple sources:

```python
{
    # Current week's analysis
    "nutrition_recommendation": {
        "adjustment_category": "decrease",
        "old_calories": 2200,
        "new_calories": 2000,
        "reasoning": "Weight loss too slow (0.3%/week). Decrease to 2000 cal (20% deficit).",
        "body_composition_status": "fat_loss"
    },

    # Training summary for this week
    "training_summary": {
        "sessions_completed": 4,
        "exercises_progressed": ["squat", "bench_press"],
        "exercises_plateaued": ["deadlift"],
        "total_volume_kg": 15000,
        "volume_change_pct": 5.2
    },

    # User data trends
    "trends": {
        "weight_trend": {
            "starting_weight": 78.5,
            "current_weight": 78.3,
            "weekly_rate_pct": -0.25,
            "trend": "decreasing"
        },
        "body_comp_trend": {
            "method": "skinfolds",
            "starting_sum": 50,
            "current_sum": 48,
            "trend": "decreasing"
        },
        "compliance": {
            "nutrition_logs": 12,
            "workout_logs": 4,
            "body_logs": 6,
            "compliance_pct": 86
        }
    },

    # User history
    "user_history": {
        "weeks_on_program": 8,
        "past_analyses": [
            {"week": "2025-11-04", "adjustment": "none", "weight_change": -0.5},
            {"week": "2025-10-28", "adjustment": "decrease", "weight_change": -0.3}
        ],
        "achievements": [
            {"type": "consistency", "description": "4 weeks of 90%+ logging"},
            {"type": "strength", "description": "Squat 1RM up 10kg"}
        ],
        "streak_days": 28,
        "total_weight_lost": 3.2,
        "total_workouts": 32
    },

    # User profile
    "user_profile": {
        "goal": "lose_weight",
        "communication_style": "encouraging",  # "encouraging", "direct", "scientific"
        "language": "en"
    }
}
```

---

## AI Agent Configuration

### System Prompt

```python
COMMUNICATION_AGENT_PROMPT = """
You are a supportive, knowledgeable fitness coach communicating weekly progress to a user.

Your role:
1. Review the user's 14-day data trends (weight, body composition, nutrition, training)
2. Explain any nutrition plan changes in simple, non-technical terms
3. Review training performance and celebrate progress
4. Acknowledge both successes and challenges with empathy
5. Motivate them to stay consistent for the upcoming week
6. Provide educational insights when relevant

Communication Guidelines:
- Tone: {communication_style} (encouraging/direct/scientific)
- Language: {language}
- Length: 3-5 short paragraphs (250-400 words)
- Structure:
  1. Opening: Acknowledge their tracking consistency this week
  2. Progress Review: Weight, body composition, and training trends
  3. Changes: Explain any nutrition or training adjustments and WHY
  4. Motivation: Encourage them for the upcoming week
  5. Tip/Insight: One actionable insight or educational point

User Context:
- Goal: {goal}
- Weeks on program: {weeks_on_program}
- Current streak: {streak_days} days
- Total progress: {total_weight_lost} kg lost, {total_workouts} workouts completed
- Recent achievements: {achievements}

This Week's Data Summary:
- Weight: {starting_weight} kg → {current_weight} kg ({weight_change_pct}%)
- Body composition: {body_comp_method} shows {body_comp_trend}
- Nutrition compliance: {nutrition_compliance}% ({nutrition_logs_count}/14 days)
- Training: {sessions_completed} sessions, {exercises_progressed_count} exercises progressed
- Overall compliance: {overall_compliance}%

Nutrition Changes:
- Action: {nutrition_adjustment_category}
- Previous: {old_calories} cal/day
- New: {new_calories} cal/day
- Technical reason: {technical_reasoning}

Training Performance:
- Volume change: {volume_change_pct}%
- Progressed: {exercises_progressed}
- Plateaued: {exercises_plateaued}
- Key win: {best_lift_improvement}

Generate a personalized weekly summary that:
- Uses the user's name if available
- Starts positive (acknowledge their effort)
- Explains data trends in simple terms (avoid jargon)
- Explains WHY changes are happening (not just WHAT)
- Is specific to THEIR data (not generic advice)
- Addresses likely concerns they might have
- Ends with clear action for next week

Avoid:
- Generic motivational quotes
- Overly technical terms (TDEE, macros, 1RM unless user prefers "scientific")
- Apologizing for bad weeks (be empathetic, not apologetic)
- Making promises ("you will lose 5 lbs next week")
"""
```

### Agent Invocation

```python
async def generate_weekly_message(
    recommendation: dict,
    training_summary: dict,
    trends: dict,
    user_history: dict,
    user_profile: dict
) -> str:
    """
    Use Bedrock Claude to generate personalized weekly message.
    """

    # Build context for prompt
    context = build_communication_context(
        recommendation, training_summary, trends, user_history, user_profile
    )

    # Fill in prompt template
    prompt = COMMUNICATION_AGENT_PROMPT.format(**context)

    # Call Bedrock
    response = bedrock_client.converse(
        modelId="anthropic.claude-3-5-sonnet-20241022-v2:0",
        messages=[
            {
                "role": "user",
                "content": prompt
            }
        ],
        inferenceConfig={
            "maxTokens": 800,
            "temperature": 0.7  # Slightly creative for natural language
        }
    )

    message = response["output"]["message"]["content"][0]["text"]

    return message
```

---

## Function Tools

### 1. Context Building

```python
def build_communication_context(
    recommendation: dict,
    training_summary: dict,
    trends: dict,
    user_history: dict,
    user_profile: dict
) -> dict:
    """
    Build context dictionary for prompt template.
    """
    return {
        # User settings
        "communication_style": user_profile.get("communication_style", "encouraging"),
        "language": user_profile.get("language", "en"),
        "goal": user_profile["goal"],

        # History
        "weeks_on_program": user_history["weeks_on_program"],
        "streak_days": user_history["streak_days"],
        "total_weight_lost": user_history["total_weight_lost"],
        "total_workouts": user_history["total_workouts"],
        "achievements": format_achievements(user_history["achievements"]),

        # This week's data
        "starting_weight": trends["weight_trend"]["starting_weight"],
        "current_weight": trends["weight_trend"]["current_weight"],
        "weight_change_pct": trends["weight_trend"]["weekly_rate_pct"],
        "body_comp_method": trends["body_comp_trend"]["method"],
        "body_comp_trend": trends["body_comp_trend"]["trend"],
        "nutrition_compliance": trends["compliance"]["compliance_pct"],
        "nutrition_logs_count": trends["compliance"]["nutrition_logs"],
        "sessions_completed": training_summary["sessions_completed"],
        "exercises_progressed_count": len(training_summary["exercises_progressed"]),
        "overall_compliance": trends["compliance"]["compliance_pct"],

        # Nutrition changes
        "nutrition_adjustment_category": recommendation["adjustment_category"],
        "old_calories": recommendation["old_calories"],
        "new_calories": recommendation["new_calories"],
        "technical_reasoning": recommendation["reasoning"],

        # Training performance
        "volume_change_pct": training_summary["volume_change_pct"],
        "exercises_progressed": ", ".join(training_summary["exercises_progressed"]),
        "exercises_plateaued": ", ".join(training_summary["exercises_plateaued"]),
        "best_lift_improvement": find_best_improvement(training_summary)
    }
```

### 2. Metrics Calculation

```python
def calculate_achievements(user_id: str) -> list:
    """
    Calculate user achievements this week.
    """
    achievements = []

    # Consistency achievements
    streak = calculate_streak(user_id)
    if streak >= 7:
        achievements.append({
            "type": "consistency",
            "description": f"{streak} day logging streak"
        })

    # Weight loss milestones
    total_lost = calculate_total_weight_lost(user_id)
    if total_lost >= 5:
        achievements.append({
            "type": "weight_loss",
            "description": f"{total_lost:.1f} kg total weight lost"
        })

    # Strength milestones
    strength_gains = get_recent_strength_gains(user_id)
    for exercise, gain_pct in strength_gains.items():
        if gain_pct >= 10:
            achievements.append({
                "type": "strength",
                "description": f"{exercise.title()} up {gain_pct}%"
            })

    return achievements


def calculate_streak(user_id: str) -> int:
    """
    Calculate consecutive days with complete logging.
    """
    logs = db.daily_summaries.find({
        "user_id": user_id
    }).sort("date", -1).limit(30)

    streak = 0
    for log in logs:
        if log.get("has_nutrition") and log.get("has_body_measurement"):
            streak += 1
        else:
            break

    return streak
```

---

## Structured Output

```python
class WeeklyCommunication(BaseModel):
    user_id: str
    week_starting: str  # ISO date

    # Generated message
    message: str
    message_length: int

    # Summary of changes communicated
    nutrition_changes: Optional[dict]  # {"action": "decrease", "old": 2200, "new": 2000}
    training_highlights: Optional[dict]  # {"progressed": ["squat"], "plateaued": []}

    # Context used
    user_metrics: dict  # Streak, compliance, achievements

    # Metadata
    generated_at: str
    model_used: str
    tokens_used: int
    generation_time_ms: int
```

---

## Lambda Handler Example

```python
# ai_agents/communication_specialist/lambda_handler.py

def lambda_handler(event, context):
    """
    EventBridge triggers this every Monday at 6:05 AM UTC.
    Generates communications for users with pending analyses.
    """

    # 1. Find all weekly analyses needing communication
    pending_analyses = db.weekly_analyses.find({
        "communication_pending": True,
        "week_starting": get_current_week_start()
    })

    results = []
    for analysis in pending_analyses:
        user_id = analysis["user_id"]

        # 2. Gather user profile
        user = db.user_profiles.find_one({"user_id": user_id})

        # 3. Gather training summary (if Training Agent has run)
        training_summary = get_training_summary(user_id, analysis["week_starting"])

        # 4. Gather trends
        trends = analysis["data_summary"]

        # 5. Gather user history
        user_history = {
            "weeks_on_program": calculate_weeks_on_program(user_id),
            "past_analyses": db.weekly_analyses.find(
                {"user_id": user_id}
            ).sort("week_starting", -1).limit(4),
            "achievements": calculate_achievements(user_id),
            "streak_days": calculate_streak(user_id),
            "total_weight_lost": calculate_total_weight_lost(user_id),
            "total_workouts": count_total_workouts(user_id)
        }

        # 6. Generate personalized message using AI
        try:
            message = generate_weekly_message(
                recommendation=analysis["recommendation"],
                training_summary=training_summary,
                trends=trends,
                user_history=user_history,
                user_profile=user
            )

            # 7. Store communication
            communication = {
                "user_id": user_id,
                "week_starting": analysis["week_starting"],
                "message": message,
                "message_length": len(message),
                "nutrition_changes": {
                    "action": analysis["recommendation"]["adjustment_category"],
                    "old": analysis["recommendation"].get("old_calories"),
                    "new": analysis["recommendation"]["recommended_calories"]
                },
                "training_highlights": {
                    "progressed": training_summary["exercises_progressed"],
                    "plateaued": training_summary["exercises_plateaued"]
                },
                "user_metrics": {
                    "streak_days": user_history["streak_days"],
                    "compliance_pct": trends["compliance"]["compliance_pct"],
                    "achievements_count": len(user_history["achievements"])
                },
                "generated_at": datetime.utcnow().isoformat(),
                "model_used": "claude-3-5-sonnet-20241022-v2:0"
            }

            db.weekly_communications.insert(communication)

            # 8. Mark analysis as communicated
            db.weekly_analyses.update(
                {"id": analysis["id"]},
                {
                    "communication_pending": False,
                    "communication_sent": True,
                    "communication_sent_at": datetime.utcnow().isoformat()
                }
            )

            results.append({"user_id": user_id, "status": "success"})

        except Exception as e:
            logger.error(f"Failed to generate communication for {user_id}: {e}")
            results.append({"user_id": user_id, "status": "failed", "error": str(e)})

    return {
        "users_processed": len(results),
        "successful": len([r for r in results if r["status"] == "success"]),
        "failed": len([r for r in results if r["status"] == "failed"])
    }
```

---

## Example Output Messages

### Example 1: User Making Good Progress
```
Hey Sarah! 👋

Great work staying consistent this week - you logged 13 out of 14 days! Your discipline
is really showing up in the results.

Your weight dropped from 78.5 kg to 78.0 kg (about 0.6% this week), and your skinfold
measurements decreased by 2mm. That's exactly the pace we want to see - steady fat loss
while preserving muscle. In the gym, you progressed on squat and bench press, which tells
me your strength is holding strong.

Your nutrition is right on track, so I'm keeping your calories at 2000 per day. No changes
needed - let's ride this wave of progress!

For next week, keep doing what you're doing. One tip: consider taking progress photos
every 4 weeks. When the scale doesn't move, photos often reveal changes that numbers miss.

Keep crushing it! 💪
```

### Example 2: User Hitting Plateau
```
Hi Marcus,

First off - 28 days of consistent logging is incredible. That discipline is building
habits that last a lifetime.

This week, your weight stayed steady at 82.3 kg, but here's what's interesting: your
waist circumference dropped by 1cm. This is body recomposition - you're trading fat for
muscle. It's actually one of the best outcomes possible, even though the scale might feel
frustrating.

You crushed 4 workouts this week and added weight to your squat. That strength gain while
weight is stable? That's proof you're building muscle. I'm keeping your calories at 2300
for now to let this body recomposition continue.

Next week, trust the process. Body recomposition is slower than pure weight loss, but
you end up looking way better at the same weight. The waist measurement and gym
performance don't lie.

You're doing this right. Stay the course! 🎯
```

### Example 3: User Needs Adjustment
```
Hey Alex,

You logged 11 days this week - solid effort! I can see you're putting in the work.

Your weight has been hovering around 75 kg for the past two weeks, and your body fat
measurements have stayed stable too. This tells me your current intake (2400 calories)
is maintaining your weight rather than creating the deficit we need for fat loss.

Here's the adjustment: I'm reducing your target to 2200 calories per day (about 10% less).
This should get things moving again while still being sustainable. At your body fat level,
this pace is safe and effective.

On the training side, you're still making progress on most lifts - nice work! The strength
gains show you're ready for this calorie adjustment.

For next week, focus on hitting that 2200 target consistently. Small adjustments like this
often break through plateaus. You've got this! 💪
```

---

## DynamoDB Schema

### New Table: `weekly_communications`

```python
{
    "user_id": "string",  # Partition key
    "week_starting": "2025-11-18",  # Sort key (ISO date)

    # Generated message
    "message": "Great work this week! Your weight dropped...",
    "message_length": 387,

    # Summary of changes communicated
    "nutrition_changes": {
        "action": "decrease",
        "old_calories": 2200,
        "new_calories": 2000,
        "reason_summary": "Weight loss too slow"
    },
    "training_highlights": {
        "sessions": 4,
        "progressed": ["squat", "bench_press"],
        "plateaued": ["deadlift"],
        "best_improvement": "Squat +5kg"
    },

    # User metrics at time of communication
    "user_metrics": {
        "streak_days": 28,
        "compliance_pct": 86,
        "achievements_count": 3,
        "weeks_on_program": 8
    },

    # Metadata
    "generated_at": "2025-11-18T06:05:23Z",
    "model_used": "claude-3-5-sonnet-20241022-v2:0",
    "tokens_used": 650,
    "generation_time_ms": 2100
}
```

### Updated Table: `weekly_analyses` (Add communication flags)

```python
{
    # ... existing fields ...

    # Communication tracking (NEW)
    "communication_pending": true,  # Set by Nutrition Agent
    "communication_sent": false,    # Set by Communication Agent
    "communication_sent_at": null   # Timestamp when communicated
}
```

---

## API Endpoints

```python
# backend/server.py

@app.get("/api/weekly-communication/{user_id}/latest")
async def get_latest_communication(user_id: str):
    """
    Get the most recent weekly communication for a user.
    This is what the frontend displays in the dashboard.
    """
    communication = db.weekly_communications.find_latest(user_id)

    if not communication:
        return {"message": "No communications yet"}

    return {
        "week_starting": communication["week_starting"],
        "message": communication["message"],
        "nutrition_changes": communication["nutrition_changes"],
        "training_highlights": communication["training_highlights"],
        "user_metrics": communication["user_metrics"],
        "generated_at": communication["generated_at"]
    }


@app.get("/api/weekly-communication/{user_id}/history")
async def get_communication_history(user_id: str, limit: int = 8):
    """
    Get past weekly communications for a user.
    Shows progression over time.
    """
    communications = db.weekly_communications.find(
        {"user_id": user_id}
    ).sort("week_starting", -1).limit(limit)

    return {"communications": list(communications)}
```

---

## Key Advantages

1. **Clear Separation of Concerns** - Communication is completely decoupled from decision-making
2. **Reusable** - Can handle messages for nutrition, training, milestones, etc.
3. **Personalized** - Uses AI to tailor messages to individual user context
4. **Motivational** - Acknowledges progress, addresses concerns, encourages consistency
5. **Educational** - Can provide tips and insights contextually
6. **Cost-Efficient** - $0.02/user/week (only AI agent needed for UX)
7. **A/B Testable** - Easy to test different communication styles
8. **Multi-Language Ready** - Can support localization
9. **Failure-Isolated** - If communication fails, nutrition/training decisions are still stored

---

## Lambda Deployment

**Function name**: `fitness-communication-specialist`

**Runtime**: Python 3.11+

**Trigger**: EventBridge cron rule (every Monday 6:05 AM UTC) or SNS subscription from Nutrition Agent

**Environment variables**:
- `DYNAMODB_TABLE_PREFIX`: Table name prefix
- `BEDROCK_MODEL_ID`: Claude model ID (e.g., `anthropic.claude-3-5-sonnet-20241022-v2:0`)

**IAM Permissions**:
- DynamoDB: Read access to `user_profiles`, `weekly_analyses`, `workout_logs`
- DynamoDB: Write access to `weekly_communications`
- Bedrock: Invoke model

**Timeout**: 60 seconds (allows time for AI generation)

**Memory**: 512 MB

---

## Testing Strategy

### Unit Tests (Mock AI)
```python
def test_build_communication_context():
    """Test context building logic"""
    context = build_communication_context(
        recommendation=sample_recommendation,
        training_summary=sample_training,
        trends=sample_trends,
        user_history=sample_history,
        user_profile=sample_profile
    )

    assert context["streak_days"] == 28
    assert context["nutrition_adjustment_category"] == "decrease"
    assert "squat" in context["exercises_progressed"]
```

### Integration Tests (Real AI)
```python
def test_generate_weekly_message_quality():
    """Test that AI generates appropriate message"""
    message = generate_weekly_message(
        recommendation=sample_recommendation,
        training_summary=sample_training,
        trends=sample_trends,
        user_history=sample_history,
        user_profile={"communication_style": "encouraging"}
    )

    # Quality checks
    assert 200 <= len(message) <= 500  # Reasonable length
    assert "2000" in message  # Mentions new calories
    assert "squat" in message.lower()  # Mentions training progress
    assert message[0].isupper()  # Proper capitalization
    assert "!" in message or "." in message  # Proper punctuation
```

---

## Future Enhancements

1. **Notification Integration** - Send message via email/push notification
2. **Multi-Language Support** - Detect user language preference
3. **Communication Style Learning** - Learn which style user engages with most
4. **Voice Messages** - Generate audio version of message
5. **Milestone Celebrations** - Special messages for achievements
6. **Educational Content** - Link to relevant articles/videos based on user status
7. **Social Features** - Compare progress with community (opt-in)
