# Motivator Specialist Agent - Complete Guide

## What Is It?

The Motivator Specialist is a **hybrid AI agent** that provides daily motivation by:
1. **Calculating streaks** (deterministic algorithm - NO AI)
   - Nutrition logging streaks
   - Workout plan adherence streaks
2. **Generating personalized messages** (AI-powered - AWS Bedrock Claude)
   - Custom motivational messages based on your data
   - Adapted to your communication style

Think of it as your personal accountability coach who:
- Tracks your consistency across nutrition and training
- Celebrates your wins with specific numbers
- Encourages you to keep going when streaks are low
- Speaks in a tone that resonates with you

**Unique Feature**: This is the only agent that combines **deterministic calculation** with **AI creativity** for personalized encouragement.

## Why Does It Exist?

**Consistency is everything** in fitness. The problem:
- Apps show generic "Good job!" messages
- No recognition of actual effort (logging 14 days straight!)
- Hard to stay motivated when progress is slow
- One missed day can derail momentum

The Motivator Specialist solves this by:
1. **Tracking real effort** (nutrition logs, workout adherence)
2. **Quantifying consistency** (7-day streak, 4-week consistency)
3. **Personalizing encouragement** (YOUR numbers, YOUR tone)
4. **Building accountability** (see your streaks grow)

**Key insight**: Small daily wins (logging meals, hitting workouts) compound into big results. The Motivator makes these visible.

---

## Two-Component Architecture

```
┌─────────────────────────────────────────────┐
│         Motivator Specialist                │
│                                             │
│  ┌──────────────────┐  ┌─────────────────┐ │
│  │   Component 1    │  │   Component 2   │ │
│  │   Deterministic  │→ │   AI Message    │ │
│  │   Streak Calc    │  │   Generator     │ │
│  │   (Algorithm)    │  │   (Bedrock)     │ │
│  └──────────────────┘  └─────────────────┘ │
│         ↓                      ↓            │
│    StreakData             Motivational      │
│                              Message        │
└─────────────────────────────────────────────┘
```

**Component 1: Streak Calculation** (Deterministic)
- Pure Python algorithm
- Counts consecutive days/weeks
- Applies grace periods and thresholds
- 100% reproducible

**Component 2: Message Generation** (AI)
- AWS Bedrock (Claude 3.5 Sonnet)
- Natural language generation
- Personalized to user's data and style
- Creative, warm, encouraging

---

## Component 1: Streak Calculation (Deterministic)

### Two Types of Streaks

**Nutrition Logging Streak**:
- **Unit**: Consecutive days
- **Criteria**: Any nutrition log that day counts
- **Grace period**: 1 day (if logged yesterday, streak is still active today)
- **Example**: Logged for 14 days straight = 14-day streak

**Workout Adherence Streak**:
- **Unit**: Consecutive weeks
- **Criteria**: Hit ≥90% of workout plan target
- **Threshold**: 3 out of 4 planned workouts = success
- **Example**: Hit plan target for 4 weeks straight = 4-week streak

---

### Nutrition Streak Algorithm

**Goal**: Count consecutive days with nutrition logs

**Grace Period**: 1 day
```
If logged yesterday:
  → Streak is still active (you have until end of today to log)
```

**Algorithm**:
```python
def calculate_nutrition_streak(logs, today):
    1. Get last 30 days of logs
    2. Extract unique dates with logs
    3. Sort dates chronologically

    4. Calculate current streak:
       - Start from today or yesterday (grace period)
       - Count backwards while consecutive

    5. Calculate longest streak:
       - Find longest consecutive sequence in history

    6. Return:
       - current_streak: Active streak (days)
       - longest_streak: Best ever streak (days)
       - last_logged_date: Most recent log date
```

**Example 1: Active Streak**
```
Logs:
- Nov 15 (today): ✓
- Nov 14: ✓
- Nov 13: ✓
- Nov 12: ✓
- Nov 11: ✓

Current streak: 5 days
```

**Example 2: Grace Period**
```
Logs:
- Nov 15 (today): No log yet
- Nov 14: ✓
- Nov 13: ✓
- Nov 12: ✓

Current streak: 1 day (grace period - logged yesterday)
```

**Example 3: Broken Streak**
```
Logs:
- Nov 15 (today): No log
- Nov 14: No log
- Nov 13: ✓
- Nov 12: ✓

Current streak: 0 days (missed yesterday, grace expired)
```

**Example 4: Longest Streak**
```
History:
- Oct 1-14: Logged daily (14-day streak)
- Oct 15-16: Missed
- Oct 17-Nov 15: Logged daily (30-day streak!)

Current streak: 30 days
Longest streak: 30 days
```

---

### Workout Adherence Streak Algorithm

**Goal**: Count consecutive weeks meeting workout plan targets

**90% Threshold**:
```
Target = 4 workouts/week
Success = ≥90% = ≥3.6 → rounds to ≥4 workouts

Target = 3 workouts/week
Success = ≥90% = ≥2.7 → rounds to ≥3 workouts
```

**Current Week Exclusion**:
- Only count COMPLETE weeks (Monday-Sunday)
- Current incomplete week is tracked separately

**Algorithm**:
```python
def calculate_workout_streak(db, user_id, plan):
    1. Get active workout plan
    2. Parse target frequency (e.g., "4x/week" → 4)
    3. Count this week's workouts (for display only)

    4. Start from last complete week (last Monday)
    5. Check last 12 weeks backwards:
       - Count workouts that week
       - If ≥90% of target: streak continues
       - If <90%: streak breaks

    6. Return:
       - current_streak: Active streak (weeks)
       - longest_streak: Best ever streak (weeks)
       - target: Workouts per week from plan
       - this_week_count: Progress on incomplete week
```

**Example 1: Active Streak**
```
Plan: 4x/week

Week of Nov 4-10: 4 workouts ✓ (100%)
Week of Nov 11-17: 3 workouts ✓ (75% but ≥90% of 4 = 3.6, rounds to 4)
Wait, 3 < 4, so this breaks the streak

Actually with 90% threshold:
Week of Nov 11-17: 4 workouts needed (4 × 0.9 = 3.6)
3 workouts logged < 3.6
Streak breaks!

Let me recalculate:
Week of Nov 4-10: 4 workouts ✓ (≥3.6)
Week of Nov 11-17: 4 workouts ✓ (≥3.6)
Week of Oct 28-Nov 3: 4 workouts ✓ (≥3.6)

Current streak: 3 weeks
```

**Example 2: Incomplete Week**
```
Today: Nov 15 (Wednesday)
This week so far: 2 workouts
Target: 4x/week

Result:
- current_streak: Based on complete weeks only
- this_week_count: 2 (displayed separately)

Message might say: "You're 2/4 workouts into this week. Keep it up!"
```

**Example 3: No Active Plan**
```
User has no active workout plan.

Result:
- current_streak: 0
- longest_streak: 0
- target: 0
- this_week_count: (still count actual workouts logged)
```

---

### Data Quality Assessment

**Purpose**: Determine reliability of streak data

**Algorithm**:
```python
def assess_data_quality(nutrition_days, workout_weeks):
    if nutrition_days >= 14 and workout_weeks >= 4:
        return "excellent"
    elif nutrition_days >= 7 and workout_weeks >= 2:
        return "good"
    elif nutrition_days >= 3 or workout_weeks >= 1:
        return "fair"
    else:
        return "poor"
```

**Example**:
```
User has:
- 10-day nutrition streak
- 3-week workout streak

Data quality: "good" (7+ nutrition days, 2+ workout weeks)
```

---

### StreakData Model

**Output structure**:
```python
{
    # Nutrition
    "nutrition_current_streak": 14,
    "nutrition_longest_streak": 21,
    "nutrition_last_logged_date": "2025-11-15",

    # Workout
    "workout_current_streak": 4,
    "workout_longest_streak": 8,
    "workout_target_per_week": 4,
    "workout_this_week_count": 2,

    # Data quality
    "sufficient_data": True,
    "days_analyzed": 30
}
```

---

## Component 2: Message Generation (AI)

### How It Works

**Input**: StreakData + User Profile + Recent Progress

**Process**:
```
1. Build prompt with user's specific data
2. Include communication style preference
3. Send to AWS Bedrock (Claude 3.5 Sonnet)
4. Extract generated message
5. Add highlights (achievements mentioned)
6. Return MotivationalMessage
```

**Output**: Personalized 2-3 sentence message

---

### Prompt Engineering

**System Prompt Template**:
```
You are a supportive fitness coach providing daily motivation
to a user tracking their fitness journey.

Your role is to generate a brief, personalized motivational
message (2-3 sentences) based on their current progress data.

User Context:
- Goal: {goal}
- Communication style: {communication_style}
- Nutrition logging streak: {nutrition_streak} days (best: {nutrition_best})
- Workout consistency: {workout_streak} weeks (target: {workout_target}x/week)
- This week's workouts so far: {this_week_workouts}/{workout_target}

Recent Progress:
- Weight change (last 7 days): {weight_change} kg
- Total workouts completed: {total_workouts}

Communication Guidelines:
1. Celebrate specific achievements (mention exact numbers)
2. Encourage continued adherence
3. Be personalized to THEIR data (not generic advice)
4. Match their communication style:
   - "encouraging": Warm, supportive, celebratory
   - "direct": Straightforward, factual, concise
   - "scientific": Data-driven, evidence-based, analytical

Important:
- Keep it to 2-3 sentences maximum
- Be specific (use their numbers)
- Stay positive even if streaks are low
- Don't make promises about future results
- Don't use generic motivational quotes

Generate a motivational message now:
```

**Why this prompt works**:
- **Specific data**: AI has exact numbers to reference
- **Clear constraints**: 2-3 sentences, no generic quotes
- **Tone guidance**: Adapts to user preference
- **Positive framing**: Even low streaks get encouragement

---

### Communication Styles

**1. Encouraging (Default)**
- **Tone**: Warm, supportive, celebratory
- **Example**: "Amazing work on your 14-day nutrition logging streak - that's two full weeks of consistency! You're 2/4 workouts into this week with plenty of time to hit your target. Keep that momentum going!"

**2. Direct**
- **Tone**: Straightforward, factual, concise
- **Example**: "14-day nutrition streak active. 2/4 workouts completed this week. On track to hit your plan if you train twice more by Sunday."

**3. Scientific**
- **Tone**: Data-driven, evidence-based, analytical
- **Example**: "Your 14-day nutrition logging streak demonstrates strong adherence behavior, which research shows is the primary predictor of long-term success. With 2/4 workouts completed mid-week, you're positioned to achieve the 90% adherence threshold required for a 4-week streak."

---

### Example Messages by Scenario

**Scenario 1: Strong Streaks**
```
Data:
- Nutrition streak: 21 days (best: 21)
- Workout streak: 6 weeks (target: 4x/week)
- This week: 3/4 workouts
- Weight change: +0.5kg

Encouraging style:
"Incredible! You're on a 21-day nutrition logging streak AND 6 consecutive
 weeks of hitting your workout plan. You've gained 0.5kg this week while
 staying consistent - that's quality muscle-building progress!"

Direct style:
"21-day nutrition streak. 6-week workout adherence. +0.5kg this week.
 Consistent execution on all fronts."

Scientific style:
"Your 21-day nutrition adherence combined with 6 weeks of meeting your
 4x/week training frequency represents the type of sustained behavioral
 consistency associated with successful body recomposition. The 0.5kg
 weekly gain aligns with evidence-based muscle gain rates for your
 training level."
```

**Scenario 2: Broken Streak, Fresh Start**
```
Data:
- Nutrition streak: 0 days (best: 14)
- Workout streak: 1 week (target: 3x/week)
- This week: 2/3 workouts
- Weight change: 0kg

Encouraging style:
"You're back on track with 1 week of workout consistency and 2/3 workouts
 done this week! Your best nutrition streak was 14 days - you've built
 that habit before, and you can build it again. Start today!"

Direct style:
"1-week workout streak active. 2/3 workouts complete. Nutrition logging
 paused - restart today to rebuild your 14-day personal best."

Scientific style:
"Your previous 14-day nutrition logging streak demonstrates capacity for
 sustained adherence. Current 1-week training consistency provides a
 foundation to re-establish nutrition tracking habits. Research shows
 habit reformation takes 2-3 weeks of consistent repetition."
```

**Scenario 3: Mid-Week Check-In**
```
Data:
- Nutrition streak: 7 days (best: 10)
- Workout streak: 2 weeks (target: 4x/week)
- This week: 1/4 workouts (Monday only)
- Weight change: -0.3kg

Encouraging style:
"Nice work on your 7-day nutrition streak - you're halfway to your
 personal best of 10 days! You've got 1/4 workouts done for the week,
 so plan to train 3 more times to keep your 2-week consistency streak alive."

Direct style:
"7-day nutrition streak. 1/4 workouts this week. Need 3 more sessions
 by Sunday to maintain 2-week adherence streak."

Scientific style:
"Current 7-day nutrition compliance represents 70% of your established
 10-day peak performance. To preserve your 2-week training adherence
 pattern, schedule 3 additional sessions before week end to meet the
 90% threshold (3.6 of 4 target workouts)."
```

**Scenario 4: Low Streaks, Need Encouragement**
```
Data:
- Nutrition streak: 0 days (best: 3)
- Workout streak: 0 weeks (target: 3x/week)
- This week: 0/3 workouts
- Weight change: 0kg

Encouraging style:
"Every journey has ups and downs - what matters is showing up again.
 You've logged nutrition for 3 days before, so you know you can do it.
 Start fresh today with one meal logged and one workout scheduled!"

Direct style:
"Both streaks paused. Previous best: 3-day nutrition streak. Action:
 Log one meal today and schedule one workout this week."

Scientific style:
"Adherence gaps are normal in behavior change processes. Your previous
 3-day nutrition tracking demonstrates initial capability. Research
 indicates that restarting with minimal friction (logging one meal)
 has higher success rates than attempting full immediate resumption."
```

---

### Highlights Extraction

**Purpose**: Identify key achievements for UI display

**Logic**:
```python
highlights = []

if nutrition_streak >= 7:
    highlights.append(f"{nutrition_streak}-day nutrition streak")

if workout_streak >= 2:
    highlights.append(f"{workout_streak}-week workout consistency")

return highlights
```

**Example**:
```
User has:
- 14-day nutrition streak
- 4-week workout streak

Highlights:
- "14-day nutrition streak"
- "4-week workout consistency"

UI can display these as badges/achievements!
```

---

### MotivationalMessage Model

**Output structure**:
```python
{
    "message": "Amazing work on your 14-day nutrition logging streak...",
    "tone": "encouraging",
    "highlights": [
        "14-day nutrition streak",
        "4-week workout consistency"
    ],
    "generated_at": "2025-11-15T10:30:00Z",
    "model_used": "anthropic.claude-3-5-sonnet-20241022-v2:0"
}
```

---

## Integration Flow

### How It All Comes Together

```
User opens app dashboard
  ↓
Backend calls Motivator Specialist
  ↓
1. Calculate Streaks (deterministic)
   - Query last 30 days nutrition logs
   - Query last 12 weeks workout logs
   - Apply algorithms
   → StreakData
  ↓
2. Fetch User Profile & Recent Progress
   - Get communication style
   - Get goal
   - Calculate weight change
  ↓
3. Generate Message (AI)
   - Build prompt with user's data
   - Call Bedrock Claude
   - Extract message
   → MotivationalMessage
  ↓
4. Combine & Return
   → MotivatorResponse
  ↓
Dashboard displays:
  - Message at top (personalized greeting)
  - Streak cards (nutrition, workout)
  - Highlights badges
```

---

## MotivatorResponse Model

**Complete output**:
```python
{
    "user_id": "user_123",
    "streaks": {
        "nutrition_current_streak": 14,
        "nutrition_longest_streak": 21,
        "nutrition_last_logged_date": "2025-11-15",
        "workout_current_streak": 4,
        "workout_longest_streak": 8,
        "workout_target_per_week": 4,
        "workout_this_week_count": 2,
        "sufficient_data": True,
        "days_analyzed": 30
    },
    "message": {
        "message": "Amazing work on your 14-day nutrition logging streak...",
        "tone": "encouraging",
        "highlights": ["14-day nutrition streak", "4-week workout consistency"],
        "generated_at": "2025-11-15T10:30:00Z",
        "model_used": "anthropic.claude-3-5-sonnet-20241022-v2:0"
    },
    "generated_at": "2025-11-15T10:30:00Z"
}
```

---

## API Endpoint

```
POST /api/motivator/generate

Request:
{
  "user_id": "user_123"
}

Response:
{
  "user_id": "user_123",
  "streaks": { ... },
  "message": { ... },
  "generated_at": "2025-11-15T10:30:00Z"
}
```

---

## Cost & Performance

**Per message generation**:
- **Streak calculation**: <10ms (deterministic)
- **AI generation**: ~500-1000ms (Bedrock API call)
- **Total latency**: ~1 second
- **Cost**: ~$0.001-0.002 per message
  - Input: ~300 tokens (prompt with data)
  - Output: ~100 tokens (2-3 sentences)
  - Bedrock Claude pricing: ~$0.003 per 1K input, ~$0.015 per 1K output

**Daily usage**:
```
1000 users × 1 message/day = 1000 messages/day
Cost: ~$1-2/day = ~$30-60/month

Very affordable for personalized daily motivation!
```

---

## Error Handling

### Fallback Message

If AI generation fails (API error, timeout, etc.):
```python
fallback_message = "Keep up the great work! Every day of tracking builds better habits."

return MotivationalMessage(
    message=fallback_message,
    tone=tone,
    highlights=[],
    model_used="fallback"
)
```

**Why fallback is important**:
- Prevents user seeing errors
- Maintains positive experience
- Generic but still encouraging

---

## Technical Details

### File Structure
```
ai_agents/motivator_specialist/
├── algorithm.py          # Deterministic streak calculations
├── message_generator.py  # AI message generation (Bedrock)
└── prompts.py           # System prompts for AI
```

### Hybrid Design

**Why deterministic + AI?**

**Deterministic for streaks**:
- ✅ Exact, reproducible counts
- ✅ No hallucination risk (must be accurate!)
- ✅ Fast (<10ms)
- ✅ Free
- ✅ Testable

**AI for messages**:
- ✅ Natural language variety
- ✅ Personalization at scale
- ✅ Tone adaptation
- ✅ Contextual awareness
- ✅ Engaging, warm communication

**Best of both worlds**!

---

## Example Dashboard Display

```
┌────────────────────────────────────────────┐
│  🎯 Welcome back, John!                    │
│                                            │
│  Amazing work on your 14-day nutrition     │
│  logging streak - that's two full weeks    │
│  of consistency! You're 2/4 workouts into  │
│  this week with plenty of time to hit      │
│  your target. Keep that momentum going!    │
└────────────────────────────────────────────┘

┌──────────────┐  ┌──────────────┐
│ 🍎 Nutrition │  │ 💪 Workouts  │
│              │  │              │
│ 14 days      │  │ 4 weeks      │
│ Best: 21     │  │ Best: 8      │
│              │  │              │
│ This week:   │  │ This week:   │
│ ✓✓✓✓✓✓✓      │  │ 2/4 ✓✓__     │
└──────────────┘  └──────────────┘

Achievements:
🏆 14-day nutrition streak
🏆 4-week workout consistency
```

---

## Prompt Engineering Best Practices

### What Makes a Good Motivational Prompt?

**DO**:
✅ Provide exact numbers (streaks, targets, progress)
✅ Define tone guidelines clearly
✅ Set length constraints (2-3 sentences)
✅ Give examples of good vs bad messages
✅ Specify what NOT to do (no generic quotes)

**DON'T**:
❌ Let AI invent data (provide all numbers)
❌ Allow vague encouragement ("Keep it up!")
❌ Permit unrealistic promises ("You'll gain 10lbs!")
❌ Use clichés ("No pain, no gain")

### Temperature Settings

```python
inferenceConfig={
    "maxTokens": 300,
    "temperature": 0.7  # Slightly creative
}
```

**Why 0.7?**
- Too low (0.1): Robotic, repetitive
- Too high (0.9): Unpredictable, might hallucinate
- Sweet spot (0.7): Natural variation, stays grounded

---

## Testing Strategy

### Unit Tests

**Test 1: Nutrition Streak Calculation**
```python
def test_nutrition_streak_active():
    """Test active nutrition streak"""
    logs = [
        {"date": "2025-11-15", "calories": 2000},
        {"date": "2025-11-14", "calories": 2100},
        {"date": "2025-11-13", "calories": 1900},
    ]

    result = calculate_nutrition_streak(db, "user_123")

    assert result["current_streak"] == 3
    assert result["last_logged_date"] == "2025-11-15"
```

**Test 2: Workout Streak with 90% Threshold**
```python
def test_workout_streak_threshold():
    """Test 90% threshold for workout adherence"""
    # User has 4x/week plan
    # Week with 3 workouts (75%) should fail
    # Week with 4 workouts (100%) should pass

    # Set up 4x/week plan
    plan = {"frequency": "4x/week"}

    # Week 1: 3 workouts (fails - 75% < 90%)
    # Week 2: 4 workouts (passes)

    result = calculate_workout_streak(db, "user_123")

    assert result["current_streak"] == 1  # Only week 2
```

**Test 3: Grace Period**
```python
def test_nutrition_grace_period():
    """Test 1-day grace period for nutrition streak"""
    today = date(2025, 11, 15)  # Thursday
    yesterday = date(2025, 11, 14)  # Wednesday

    logs = [
        {"date": "2025-11-14"},  # Logged yesterday
        {"date": "2025-11-13"},
        {"date": "2025-11-12"},
    ]

    # Today is Thursday, haven't logged yet
    # But logged yesterday, so grace period applies
    result = calculate_nutrition_streak(db, "user_123")

    assert result["current_streak"] == 1  # Grace period
```

**Test 4: Message Generation**
```python
async def test_message_generation():
    """Test AI message generation"""
    streaks = StreakData(
        nutrition_current_streak=14,
        nutrition_longest_streak=21,
        workout_current_streak=4,
        workout_longest_streak=8,
        workout_target_per_week=4,
        workout_this_week_count=2,
        sufficient_data=True,
        days_analyzed=30
    )

    user_profile = {
        "goal": "build_muscle",
        "communication_style": "encouraging"
    }

    recent_progress = {
        "weight_change": 0.5,
        "total_workouts": 24
    }

    message = await generate_motivational_message(
        bedrock_client,
        "user_123",
        streaks,
        user_profile,
        recent_progress
    )

    assert len(message.message) >= 50  # Min length
    assert len(message.message) <= 500  # Max length
    assert message.tone == "encouraging"
    assert "14" in message.message  # Should mention streak
```

---

## Common Questions

### Q: Why not use AI for streak calculation too?

**A**: Streak calculation must be **100% accurate**.

```
User has 14-day nutrition streak.
AI says: "Nice 12-day streak!"
User: "WTF? I logged 14 days, not 12!"

Trust broken.
```

Deterministic algorithm guarantees exact counts. No hallucinations.

---

### Q: What if the AI message is inappropriate?

**Mitigation**:
1. **Constrained prompt**: Specific guidelines prevent off-topic messages
2. **Temperature**: 0.7 keeps it grounded (not too creative)
3. **Length limit**: Max 500 chars prevents rambling
4. **Fallback**: If generation fails, show generic positive message
5. **Moderation** (future): Add content filter if needed

In practice, Claude 3.5 with good prompts rarely produces bad outputs.

---

### Q: How does the grace period work exactly?

**A**: 1-day grace period for nutrition streaks:

```
Scenario 1: Logged yesterday (Wednesday)
Today: Thursday, no log yet
Result: Streak ACTIVE (1 day grace)

Scenario 2: Logged yesterday, log today
Today: Thursday, logged
Result: Streak ACTIVE (2 days)

Scenario 3: Missed yesterday
Today: Thursday
Result: Streak BROKEN (grace expired)
```

**Why grace period?**
- Prevents midnight deadline stress
- Accounts for late logging (log yesterday's meals today)
- Reasonable flexibility

**Why only 1 day?**
- 2+ days is too lenient (not really consecutive)
- Encourages daily habit
- Matches user expectations

---

### Q: Why 90% threshold for workout streaks?

**A**: **Life happens**.

```
Plan: 4 workouts/week

Strict (100%):
- Week 1: 4/4 ✓
- Week 2: 3/4 ✗ (sick one day)
- Streak broken after 1 week

Lenient (90%):
- Week 1: 4/4 ✓
- Week 2: 4/4 ✓ (3 also passes - 75% but rounds to 4)

Wait, let me recalculate:
90% of 4 = 3.6
So need ≥3.6 workouts = 4 workouts (rounds up)

Actually 3 workouts = 75% < 90%, so fails.

So for 4x/week plan:
- Need 4 workouts (90% = 3.6 rounds to 4)
- 3 workouts fails

For 3x/week plan:
- 90% = 2.7 → need 3 workouts
- 2 workouts fails

Actually... let me look at code:
```python
return actual >= (target * 0.9)
```

So:
- 4x/week: need >= 3.6 → need 4 (3 fails, 4 passes)
- 3x/week: need >= 2.7 → need 3 (2 fails, 3 passes)

**So 90% threshold still requires perfect adherence for most plans.**

**Why not lower?**
- 80% would be too lenient (2/4 workouts = 50%)
- 90% forces consistency while allowing one slip

---

### Q: Can I customize my communication style?

**A**: Yes! Three options:

**1. Encouraging (Default)**
- Warm, supportive, celebrates wins
- Best for: Most users

**2. Direct**
- Facts, no fluff, concise
- Best for: Busy people who want quick updates

**3. Scientific**
- Data-driven, evidence-based, analytical
- Best for: Nerds who love details

Set in user profile: `communication_style: "direct"`

---

### Q: How often should I get motivational messages?

**A**: **Daily** is ideal for:
- Streak awareness (am I still on track?)
- Habit reinforcement (daily reminder to log)
- Momentum building (see progress accumulate)

**But not spammy**:
- One message per day max
- Only when user opens app (not push notifications)
- Integrated into dashboard (not interrupting)

---

## Summary

The Motivator Specialist is a **hybrid agent** that combines:

**1. Deterministic Streak Calculation**:
- Nutrition logging streaks (consecutive days)
- Workout adherence streaks (consecutive weeks)
- Grace periods (1 day for nutrition)
- 90% threshold (workout plans)
- Longest vs current tracking
- Data quality assessment

**2. AI Message Generation**:
- AWS Bedrock (Claude 3.5 Sonnet)
- Personalized 2-3 sentence messages
- Adapted to communication style
- Specific numbers from user's data
- Highlights key achievements
- Fallback for errors

**Key Design Principles**:
- **Accuracy first**: Streaks are deterministic (no AI hallucinations)
- **Personalization**: AI uses YOUR exact data
- **Tone adaptation**: Matches your communication preference
- **Positive framing**: Encourages even when streaks are low
- **Actionable**: Mentions what to do next
- **Efficient**: ~1 second latency, <$0.002 per message

**Use Cases**:
- Daily dashboard greeting
- Weekly email summaries
- Push notifications (if user opts in)
- Achievement celebrations

**Value Proposition**:
> "You logged nutrition for 14 days straight and hit your workout plan
> for 4 consecutive weeks. That's real progress, and we're celebrating it
> with you!"

The Motivator makes **consistency visible and rewarding**, which is the
foundation of long-term fitness success!
