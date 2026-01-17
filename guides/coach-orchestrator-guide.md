# Coach Orchestrator Agent - Complete Guide

## What Is It?

The Coach Orchestrator is a **conversational AI fitness coach** that answers your questions by intelligently coordinating data sources and specialist agents. Think of it as your personal trainer who:

- Understands natural language questions
- Automatically fetches relevant data (workouts, nutrition, body composition)
- Consults specialist agents (Nutrition, Training) for expert analysis
- Searches evidence-based knowledge base for scientific information
- Synthesizes personalized, comprehensive answers

**Key Difference**: Unlike the deterministic agents (Nutrition, Training), this agent **uses AI/LLM** (OpenAI GPT-4) for natural conversation and intelligent tool selection.

## Why Does It Exist?

Users have questions about their fitness journey:
- **"Am I making progress?"** → Needs personal data analysis
- **"Should I adjust my calories?"** → Needs Nutrition Specialist analysis
- **"What's the optimal training volume?"** → Needs knowledge base search
- **"Why did my bench press plateau?"** → Needs Training Specialist + personal data

A single question often requires **multiple data sources**:
```
User: "Am I gaining muscle or just fat?"

Coach needs to:
1. Check weight trend (body composition data)
2. Check strength progress (Training Specialist)
3. Check nutrition adherence (nutrition logs)
4. Synthesize into an answer
```

The Coach Orchestrator solves this by **intelligently routing** to the right tools and agents.

---

## Architecture Overview

### Two-Layer System

```
┌─────────────────────────────────────────┐
│        Coach Orchestrator (AI)          │
│  - Natural language understanding       │
│  - Tool selection & orchestration       │
│  - Response synthesis                   │
└─────────────────┬───────────────────────┘
                  │
        ┌─────────┴─────────┐
        │                   │
┌───────▼────────┐  ┌──────▼─────────┐
│  Deterministic │  │   Data Access  │
│    Agents      │  │     Tools      │
│                │  │                │
│ - Nutrition    │  │ - User Profile │
│ - Training     │  │ - Workout Logs │
│                │  │ - Nutrition    │
│                │  │ - Body Comp    │
│                │  │ - RAG/KB       │
└────────────────┘  └────────────────┘
```

**Layer 1: Orchestrator (AI)**
- Uses GPT-4 for conversation
- Decides which tools to call
- Synthesizes multi-source information

**Layer 2: Execution (Deterministic)**
- Specialist agents run algorithms
- Data access tools fetch from database
- RAG searches knowledge base

---

## Function Calling (The Magic)

### How It Works

**OpenAI Function Calling** lets the LLM intelligently select and execute tools:

```
1. User asks question
   ↓
2. GPT-4 analyzes question
   ↓
3. GPT-4 decides which tool(s) to call
   ↓
4. Tools execute and return data
   ↓
5. GPT-4 synthesizes answer from results
```

**Example**:
```
User: "Should I adjust my calories?"

GPT-4 thinks:
  → This is about nutrition adjustment
  → Need to call get_nutrition_recommendation()

Calls: get_nutrition_recommendation(user_id="user_123")

Receives:
  {
    "recommended_calories": 2250,
    "adjustment_category": "increase",
    "reasoning": "Weight gain slower than target..."
  }

GPT-4 synthesizes:
  "Based on your progress, I recommend increasing to 2250 calories.
   You're gaining 0.3%/week but your target is 0.5%/week as an
   intermediate lifter. The extra calories will support muscle growth..."
```

### Available Tools (7 Total)

**Personal Data Tools** (4):
1. `get_user_profile()` - Goals, targets, body stats
2. `get_nutrition_logs(days)` - Recent eating history
3. `get_workout_logs(days, exercise)` - Training history
4. `get_body_logs(days)` - Weight & composition tracking

**Knowledge Base** (1):
5. `search_knowledge_base(query)` - Evidence-based fitness/nutrition info (RAG)

**Specialist Agents** (2):
6. `get_nutrition_recommendation()` - Nutrition Specialist analysis
7. `get_training_summary()` - Training Specialist analysis

---

## Tool Deep Dive

### Tool 1: get_user_profile()

**When GPT-4 calls it**:
- User asks about their goals or targets
- Need baseline info (current weight, body fat, etc.)

**What it returns**:
```json
{
  "user_id": "user_123",
  "name": "John",
  "age": 28,
  "sex": "male",
  "body_weight_kg": 75,
  "body_fat_pct": 15,
  "goal": "build_muscle",
  "training_status": "intermediate",
  "target_calories": 2500,
  "target_protein": 150,
  "target_carbs": 300,
  "target_fats": 80
}
```

**Example Question**: "What are my fitness goals?"

**GPT-4 Response**:
> "Your goal is to build muscle. You're currently 75kg at 15% body fat,
> and your nutrition targets are 2500 calories daily (150g protein, 300g carbs,
> 80g fat). As an intermediate lifter, these targets are designed to support
> steady muscle growth while minimizing fat gain."

---

### Tool 2: get_nutrition_logs(days=7)

**When GPT-4 calls it**:
- User asks about calorie/macro intake
- Questions about nutrition adherence
- Need to see recent eating patterns

**What it returns**:
```json
{
  "logs": [
    {
      "date": "2025-11-15",
      "meal": "Breakfast",
      "calories": 650,
      "protein_g": 40,
      "description": "Oatmeal with protein powder..."
    },
    // ... more logs
  ],
  "summary": {
    "days_logged": 6,
    "avg_calories": 2450,
    "avg_protein": 145
  }
}
```

**Example Question**: "Am I hitting my protein target?"

**GPT-4 Response**:
> "Over the last 7 days, you've logged 6 days and averaged 145g protein
> per day. Your target is 150g, so you're very close! You're consistently
> hitting 97% of your protein goal, which is excellent adherence."

---

### Tool 3: get_workout_logs(days=14, exercise=None)

**When GPT-4 calls it**:
- User asks about recent workouts
- Questions about specific exercises
- Training frequency analysis

**What it returns**:
```json
{
  "logs": [
    {
      "date": "2025-11-15",
      "exercises": [
        {
          "name": "Barbell squat",
          "sets": [
            {"weight": 100, "reps": 5},
            {"weight": 100, "reps": 5},
            {"weight": 100, "reps": 5}
          ]
        }
      ]
    },
    // ... more workouts
  ],
  "summary": {
    "total_workouts": 6,
    "exercises_performed": ["Barbell squat", "Bench press", "Deadlift", ...]
  }
}
```

**Example Question**: "How's my squat progression?"

**GPT-4 calls**: `get_workout_logs(days=14, exercise="squat")`

**GPT-4 Response**:
> "Looking at your last 14 days, you've completed squats 3 times:
> - Nov 1: 95kg × 5 reps
> - Nov 8: 97.5kg × 5 reps
> - Nov 15: 100kg × 5 reps
>
> Great progression! You're consistently adding weight each week. Keep up
> the linear progression!"

---

### Tool 4: get_body_logs(days=14)

**When GPT-4 calls it**:
- Weight or body composition questions
- Trend analysis
- Progress tracking

**What it returns**:
```json
{
  "logs": [
    {
      "date": "2025-11-15",
      "weight_kg": 75.2,
      "body_fat_pct": 15.0,
      "skinfold_sum": 48,
      "waist_cm": 82
    },
    // ... more logs
  ],
  "summary": {
    "days_logged": 10,
    "latest_weight": 75.2,
    "weight_change": 0.8,
    "avg_weight": 74.8
  }
}
```

**Example Question**: "Am I losing weight?"

**GPT-4 Response**:
> "Over the last 14 days, you've tracked weight 10 times. Your current
> weight is 75.2kg, up 0.8kg from 74.4kg at the start of this period.
> Your average has been 74.8kg. You're in a slight upward trend, which
> aligns with your muscle-building goal!"

---

### Tool 5: search_knowledge_base(query, top_k=5)

**When GPT-4 calls it**:
- General fitness/health questions (not personal)
- User asks "what is..." or "how does..."
- Questions about training principles, nutrition science

**How it works**: RAG (Retrieval-Augmented Generation)
```
1. Embed user's question as vector
2. Search vector database for similar content
3. Retrieve top K most relevant documents
4. Return context to GPT-4
5. GPT-4 synthesizes answer with sources
```

**What it returns**:
```json
{
  "context": "...(relevant document excerpts)...",
  "sources": [
    {
      "title": "Training Volume Landmarks - Renaissance Periodization",
      "author": "Dr. Mike Israetel",
      "relevance_score": 0.92
    }
  ],
  "summary": "Found 5 relevant sources about training volume..."
}
```

**Example Question**: "What's the optimal training volume for muscle growth?"

**GPT-4 calls**: `search_knowledge_base(query="optimal training volume muscle growth")`

**GPT-4 Response**:
> "According to Renaissance Periodization research, the optimal training
> volume varies by individual but generally falls into these landmarks:
>
> - **MV (Maintenance Volume)**: ~4-6 sets/muscle/week to maintain
> - **MEV (Minimum Effective Volume)**: ~8-10 sets/week for growth
> - **MAV (Maximum Adaptive Volume)**: ~12-20 sets/week (optimal zone)
> - **MRV (Maximum Recoverable Volume)**: ~20-25+ sets/week (overtraining risk)
>
> For most intermediate lifters, aiming for 10-15 sets per muscle group
> per week is a good starting point. Monitor your recovery and adjust up
> or down based on results.
>
> Source: Dr. Mike Israetel, Renaissance Periodization"

---

### Tool 6: get_nutrition_recommendation()

**When GPT-4 calls it**:
- User asks if they should adjust calories/macros
- Questions about nutrition plan effectiveness
- Requests for personalized nutrition advice
- Questions about WHY a recommendation was made

**What it does**:
1. Fetches last 14 days of data (weight, body comp, nutrition, training)
2. Runs Nutrition Specialist's deterministic algorithm
3. Returns calorie/macro recommendation with detailed reasoning

**What it returns**:
```json
{
  "recommended_calories": 2250,
  "recommended_macros": {
    "protein_g": 150,
    "carbs_g": 250,
    "fat_g": 70
  },
  "current_avg_calories": 2000,
  "adjustment_category": "increase",
  "reasoning": "Weight gain slower than target (0.3%/week vs 0.5%/week).
               Increase to 2250 cal (10% surplus) for muscle growth.",
  "body_composition_status": "muscle_gain",
  "data_quality": {
    "weight_logs": 10,
    "nutrition_days_logged": 12,
    "sufficient_data": true
  }
}
```

**Example Question**: "Should I adjust my calories?"

**GPT-4 Response**:
> "Yes, I recommend increasing your calories to 2250 per day. Here's why:
>
> Based on your last 14 days of data, you're averaging 2000 calories and
> gaining weight at 0.3% per week. As an intermediate lifter bulking, your
> target gain rate should be 0.5% per week for optimal muscle growth.
>
> You're gaining slower than ideal, which means you need a larger surplus.
> The Nutrition Specialist algorithm recommends a 10% surplus, bringing you
> to 2250 calories.
>
> New macro targets:
> - Protein: 150g (unchanged - you need 1.8g/kg)
> - Carbs: 250g (increased for energy)
> - Fat: 70g (for hormone health)
>
> Your data quality is excellent (10 weight logs, 12 nutrition days tracked),
> so this recommendation is highly reliable."

**Key Feature**: The `reasoning` field contains the **exact algorithmic logic**
that the Nutrition Specialist used, so GPT-4 can explain it transparently.

---

### Tool 7: get_training_summary()

**When GPT-4 calls it**:
- User asks about training progress
- Questions about strength gains or plateaus
- Need aggregate exercise analysis

**What it does**:
1. Fetches latest training progress summary (published weekly by Training Specialist)
2. Returns overall strength trend and exercise breakdowns

**What it returns**:
```json
{
  "overall_strength_trend": "improving",
  "exercises_analyzed": 8,
  "exercises_progressing": 6,
  "exercises_plateaued": 2,
  "exercises_regressing": 0,
  "workouts_completed": 6,
  "avg_weekly_volume_kg": 12500.0,
  "trend_confidence": 0.85,
  "data_quality": "good",
  "week": "2025-W47",
  "summary": "Overall trend: improving. 6 exercises progressing, 2 plateaued, 0 regressing."
}
```

**Example Question**: "Am I getting stronger?"

**GPT-4 Response**:
> "Yes! Your training trend is **improving**. Here's the breakdown:
>
> Over the last week, the Training Specialist analyzed 8 of your exercises:
> - **6 exercises progressing** (hitting rep targets consistently)
> - **2 exercises plateaued** (stuck at same weight/reps)
> - **0 exercises regressing**
>
> You completed 6 workouts with a total volume of 12,500kg lifted. This is
> excellent progress! The fact that 75% of your exercises are progressing
> indicates you're building strength effectively.
>
> For the 2 plateaued exercises, I'd recommend reviewing your progression
> strategy. Consider switching from Linear Progressive to Rep Range if you're
> hitting 50%+ failure rate on those lifts."

---

## System Prompt (The Coach's Personality)

The system prompt defines **how** the Coach behaves:

```
You are an expert fitness coach helping users achieve their health
and fitness goals.

Your expertise:
- Nutrition science and energy balance
- Progressive overload and training principles
- Body composition and measurement techniques
- Behavior change and adherence strategies
- Evidence-based fitness research

Your approach:
1. Data-driven: Reference specific metrics when analyzing
2. Educational: Explain the "why" behind recommendations
3. Encouraging: Celebrate progress, normalize plateaus
4. Realistic: Set honest expectations
5. Concise: Clear and direct, avoid jargon

Key facts:
- Nutrition/Training Specialists run automatically weekly
- They use evidence-based algorithms (not AI)
- Your job: explain their decisions
- You have read-only access (explain, don't modify)
```

**Why this matters**:
- **Data-driven**: Forces references to actual numbers
- **Educational**: Builds user understanding (teach to fish)
- **Encouraging**: Maintains motivation
- **Read-only**: Coach explains, doesn't override algorithms

---

## Multi-Turn Conversations

The Coach supports **context-aware conversations**:

```
User: "What's my current weight?"
Coach: (calls get_body_logs)
       "Your latest weight is 75.2kg as of Nov 15."

User: "Has it changed this month?"
Coach: (uses context from previous call)
       "Yes, you've gained 0.8kg since the start of November,
        going from 74.4kg to 75.2kg. This is a healthy gain rate
        for someone bulking!"
```

**How it works**:
```python
# Conversation history is maintained
messages = [
    {"role": "system", "content": system_prompt},
    {"role": "user", "content": "What's my current weight?"},
    {"role": "assistant", "content": "Your latest weight is 75.2kg..."},
    {"role": "user", "content": "Has it changed this month?"}
]

# GPT-4 sees full context and can reference previous data
```

---

## Tool Selection Intelligence

### How GPT-4 Decides Which Tools to Call

**Single-tool questions**:
```
"What's my protein intake?" → get_nutrition_logs()
"Am I getting stronger?" → get_training_summary()
"What is progressive overload?" → search_knowledge_base()
```

**Multi-tool questions**:
```
"Am I gaining muscle or fat?"
→ get_body_logs() (check weight trend)
→ get_training_summary() (check strength progress)
→ Synthesize: "You're gaining weight (0.5%/week) and strength is
   improving (6/8 exercises progressing). This indicates primarily
   muscle gain with minimal fat!"
```

**Adaptive tool calling**:
```
User: "Should I eat more?"

GPT-4: Let me check your nutrition recommendation...
→ get_nutrition_recommendation()

Result: adjustment_category = "increase"

GPT-4: Let me also check your current intake...
→ get_nutrition_logs(days=7)

Result: avg_calories = 2000

GPT-4: "Yes, you should increase to 2250 calories. You're currently
       averaging 2000 cal/day, but your progress data suggests you
       need a bigger surplus for muscle growth..."
```

**Tool chaining**:
```
User: "Why am I not losing weight?"

Chain:
1. get_body_logs() → Check weight trend
2. get_nutrition_logs() → Check calorie intake
3. get_nutrition_recommendation() → Get expert analysis
4. Synthesize answer with all data points
```

---

## Response Synthesis

### How GPT-4 Combines Multiple Sources

**Example: Complex question**
```
User: "I'm gaining weight but my lifts aren't improving. What's wrong?"

Tools called:
1. get_body_logs() →
   - Weight: +0.6kg/week (gaining)

2. get_training_summary() →
   - Strength trend: "stable"
   - 2/8 exercises progressing
   - 4/8 exercises plateaued

3. get_nutrition_logs() →
   - Avg calories: 2800 cal/day
   - High adherence

Coach synthesizes:
"I see the issue. You're gaining weight (0.6kg/week) but your strength
trend is 'stable' - only 2 out of 8 exercises are progressing, with
4 plateaued. This suggests you're gaining more fat than muscle.

Here's what's happening:
- You're eating 2800 cal/day (good adherence!)
- Your weight is increasing (calorie surplus confirmed)
- BUT your lifts aren't improving proportionally

This could mean:
1. **Training issue**: Your program may need adjustment. Plateaued
   exercises need deloads or plateau breakers.

2. **Surplus too large**: You're gaining faster than your body can
   build muscle. Consider reducing to 2500 cal/day.

Recommendation: First, address the training plateaus. Switch stuck
exercises to Rep Range progression if you're on Linear. If that
doesn't help in 2 weeks, reduce your surplus by 10%."
```

**Key aspects**:
- References **specific numbers** (0.6kg/week, 2/8 exercises)
- Explains **causality** (surplus + no strength = fat gain)
- Provides **actionable steps** (fix training, then nutrition)
- Educates user on **why** this is happening

---

## Error Handling

### What happens when tools fail?

**Graceful degradation**:
```python
try:
    result = execute_tool("get_nutrition_logs", args)
except Exception as e:
    result = {
        "error": str(e),
        "message": "Tool execution failed"
    }

# GPT-4 receives error and adapts response
GPT-4: "I encountered an issue accessing your nutrition logs. Could you
        tell me approximately how many calories you've been eating daily?"
```

**Insufficient data**:
```
User: "Should I adjust my calories?"
→ get_nutrition_recommendation()

Returns:
{
  "data_quality": {
    "nutrition_days_logged": 3,
    "sufficient_data": false
  }
}

GPT-4: "I need more data to give you a reliable recommendation. You've
        only logged nutrition for 3 of the last 14 days. Try logging
        consistently for at least 10 days, then ask me again!"
```

---

## Example Conversations

### Conversation 1: Beginner Asking About Progress

```
User: "I just started working out 3 weeks ago. How do I know if I'm
       making progress?"

Tools called:
- get_workout_logs(days=21)
- get_body_logs(days=21)

Coach:
"Great question! Let me look at your last 3 weeks...

Training:
You've completed 9 workouts (3x per week - consistent!). Looking at
your main lifts:
- Squat: 60kg → 67.5kg (+7.5kg in 3 weeks!)
- Bench: 40kg → 45kg (+5kg)
- Deadlift: 80kg → 87.5kg (+7.5kg)

This is excellent progress for a beginner! You're adding weight every
session, which is exactly what should happen in your first few months.

Body Composition:
Your weight went from 72.0kg to 72.8kg (+0.8kg). This small gain is
perfect - you're likely adding muscle while burning some fat (common
for beginners).

You're doing everything right:
✓ Consistent training (3x/week)
✓ Progressive overload (adding weight each session)
✓ Modest weight gain (not too fast)

Keep this up for the next 3-6 months! Enjoy these 'newbie gains' -
progress will slow down eventually, but that's normal."
```

---

### Conversation 2: Intermediate Asking About Plateau

```
User: "My bench press has been stuck at 100kg for 4 weeks. What should I do?"

Tools called:
- get_workout_logs(days=28, exercise="bench")
- get_training_summary()

Coach:
"Let me analyze your bench press progression...

Last 4 weeks of bench press:
- Week 1: 100kg × 5, 4, 4 reps
- Week 2: 100kg × 4, 4, 3 reps
- Week 3: 100kg × 5, 4, 4 reps
- Week 4: 100kg × 4, 3, 3 reps

I can see the plateau. You're oscillating between hitting the target
and missing it, but not making forward progress.

Your overall training summary shows you're progressing on 6/8 exercises,
so this isn't a systemic recovery issue - just bench-specific.

Here's what I recommend:

1. **Switch to Rep Range Progression**: You're on Linear Progressive
   (hit 5 reps → add weight, miss → deload). The 2.5kg jump from 100kg
   to 102.5kg is too big right now.

   With Rep Range:
   - Keep 100kg but aim for 10 reps instead of 5
   - Build gradually: 5 → 7 → 9 → 10 reps
   - THEN add 2.5kg and reset to 5 reps

2. **Plateau Breaker** (one session):
   - This week: Do 110kg × 3 reps (heavy, low volume)
   - Next week: Back to 100kg - you'll likely hit 6-7 reps easily

3. **Check technique**:
   - Film your sets
   - Ensure you're touching chest fully
   - Bar path should be straight

Try the Rep Range switch first. If still stuck after 2 weeks, add
a plateau breaker session."
```

---

### Conversation 3: Advanced User Asking About Nutrition Math

```
User: "Why did the Nutrition Specialist recommend 2043 calories? How is
       that calculated?"

Tools called:
- get_nutrition_recommendation()
- get_body_logs(days=14)
- get_nutrition_logs(days=14)

Coach:
"Great question! Let me explain the algorithm's logic step-by-step.

Here's what the Nutrition Specialist analyzed:

**Your Data (last 14 days):**
- Average intake: 1950 cal/day
- Weight change: -0.45kg (-0.7%/week)
- Body fat trend: Decreasing (skinfolds -3mm)
- Goal: Lose weight
- Current body fat: 18% (male)

**Step 1: Estimate Maintenance**
Using your current intake and weight loss rate:
- Losing 0.7%/week ≈ 20% calorie deficit (from Table 2)
- Maintenance = 1950 / (1 - 0.20) = 2438 calories

**Step 2: Optimal Deficit for Your Body Fat**
Table 1 (body fat % based):
- Male, 18% body fat → Optimal deficit = 20%

**Step 3: Compare Actual vs Optimal**
- Estimated deficit: 20% (from your loss rate)
- Optimal deficit: 20% (from your body fat)
- Difference: 0% (perfectly on track!)

**Step 4: Recommendation**
Since you're exactly at optimal pace:
- Recommended calories = Maintenance × (1 - 0.20)
- 2438 × 0.80 = **1950 calories** (maintain current)

Wait, but you asked about 2043...

[Checks recommendation details]

Oh! The algorithm recommended 2043 because it recalculated maintenance
from your observed weight loss and found it's slightly higher than
the initial estimate. This accounts for measurement variance in your
daily intake.

The recommendation is essentially: 'Keep doing what you're doing, but
aim for a slightly higher average to account for logging variability.'

**Bottom line**: You're losing fat at the perfect pace for your body
fat level. The 2043 target provides a small buffer above your current
1950 average to prevent losing too fast."
```

---

## Backend Integration

### API Endpoint

```python
POST /api/coach/ask

Request:
{
  "user_id": "user_123",
  "question": "Should I adjust my calories?",
  "thread_id": "thread_abc123",  # Optional for multi-turn
  "conversation_history": [...]  # Optional previous messages
}

Response:
{
  "message": "Based on your progress, I recommend...",
  "thread_id": "thread_abc123",
  "tool_calls": [
    {"tool": "get_nutrition_recommendation", "success": true}
  ],
  "sources": []  # Populated if RAG was used
}
```

### Cost & Performance

**Per conversation**:
- **Latency**: 2-5 seconds (depends on tool calls)
- **Cost**: ~$0.01-0.05 per response
  - Input tokens: ~500-1000 (system prompt + question + history)
  - Output tokens: ~200-500 (response)
  - Tool results: ~500-2000 tokens (data returned)

**Optimization strategies**:
- Cache system prompt (doesn't change)
- Limit conversation history to last 5 turns
- Use smaller model (GPT-3.5) for simple questions
- Batch similar questions

---

## Technical Details

### File Structure
```
ai_agents/coach_orchestrator/
├── agent.py          # Main CoachAgent class
├── prompts.py        # System prompt definition
├── tools.py          # Tool definitions & execution
└── tests/            # Unit tests for each phase
```

### Phase Development

**Phase 1: Basic structure** ✅
- OpenAI SDK integration
- Function calling framework

**Phase 2: RAG integration** ✅
- search_knowledge_base() tool
- Vector database search
- Source attribution

**Phase 3: Personal data** ✅
- get_user_profile()
- get_nutrition_logs()
- get_workout_logs()
- get_body_logs()

**Phase 4: Specialist agents** ✅
- get_nutrition_recommendation()
- get_training_summary()

---

## Prompt Engineering Best Practices

### System Prompt Design

**DO**:
✅ Be specific about capabilities
✅ Give clear behavior guidelines
✅ Explain the agent's role in the system
✅ Provide examples of good responses
✅ Define tone and personality

**DON'T**:
❌ Make vague statements ("be helpful")
❌ Over-constrain (let LLM use judgment)
❌ Ignore edge cases
❌ Forget to explain tool purposes

### Tool Descriptions

**DO**:
✅ Explain WHEN to use the tool
✅ Give concrete examples
✅ Describe return value structure
✅ Mention limitations

**DON'T**:
❌ Just list parameters
❌ Use jargon without explanation
❌ Assume LLM knows context

**Example - Good tool description**:
```python
{
  "name": "get_nutrition_logs",
  "description": """Get user's recent nutrition logs and eating patterns.

  Use this when users ask about:
  - Their calorie or macro intake
  - What they've been eating
  - Nutrition tracking progress

  Examples:
  - "What's my average calorie intake this week?"
  - "How much protein am I eating?"
  - "Am I hitting my nutrition targets?"
  """,
  ...
}
```

**Example - Bad tool description**:
```python
{
  "name": "get_nutrition_logs",
  "description": "Retrieves nutrition data",
  ...
}
```

---

## Testing Strategy

### Unit Tests by Phase

**Phase 2 Test (RAG)**:
```python
def test_knowledge_base_search():
    """Test that RAG returns relevant context"""
    result = search_knowledge_base(
        query="optimal training volume",
        top_k=3
    )

    assert "sources" in result
    assert len(result["sources"]) > 0
    assert "context" in result
```

**Phase 3 Test (Personal Data)**:
```python
def test_get_nutrition_logs():
    """Test nutrition log retrieval"""
    result = get_nutrition_logs(
        user_id="test_user",
        days=7
    )

    assert "logs" in result
    assert "summary" in result
    assert result["summary"]["days_logged"] >= 0
```

**Phase 4 Test (Specialist Agents)**:
```python
def test_nutrition_recommendation():
    """Test Nutrition Specialist integration"""
    result = get_nutrition_recommendation(user_id="test_user")

    assert "recommended_calories" in result
    assert "reasoning" in result
    assert "adjustment_category" in ["increase", "decrease", "none"]
```

---

## Common Questions

### Q: Why use GPT-4 instead of a deterministic agent?

**A**: Different use cases:

**Deterministic agents** (Nutrition, Training):
- Single, well-defined task
- Output must be consistent
- Follow specific algorithms
- Need to be testable/auditable

**LLM Coach**:
- Open-ended conversations
- Needs to synthesize multi-source info
- Natural language understanding
- Personalization and empathy

**The Coach doesn't make decisions** - it explains decisions made by deterministic agents.

---

### Q: Can users modify their plan through the Coach?

**A**: No, the Coach is **read-only**.

```
User: "Can you increase my calories to 3000?"

Coach: "I can't directly modify your nutrition plan - that's handled
        by the Nutrition Specialist algorithm which runs weekly.

        However, I can help you understand if 3000 calories is appropriate
        for your goals. Let me check your current recommendation..."

        [Calls get_nutrition_recommendation()]

        "The Nutrition Specialist currently recommends 2500 calories based
         on your progress data. If you want to manually adjust to 3000,
         you can update your targets in the app settings, but I'd suggest
         following the algorithm's recommendation for now since it's based
         on your actual progress data."
```

**Why read-only?**:
- Prevents conflicting decisions (AI vs algorithm)
- Maintains data integrity
- Algorithms are evidence-based (AI could be wrong)
- User can override manually if needed

---

### Q: What if GPT-4 hallucinates?

**Mitigation strategies**:

1. **Tool-grounded responses**:
   - All data comes from tools (not GPT-4's knowledge)
   - Coach MUST cite sources

2. **System prompt constraints**:
   - "Reference specific numbers from tools"
   - "Don't make up statistics"

3. **Validation**:
   - Tool results are validated before returning
   - Impossible values (negative weight, etc.) filtered

4. **Fallback**:
   - If GPT-4 response seems wrong, user can verify in dashboard

**Example of grounding**:
```
Bad (hallucination risk):
"Most people need 2500 calories per day"

Good (tool-grounded):
"According to your profile, your target is 2500 calories, and over the
 last 7 days you've averaged 2450 calories (98% adherence)."
```

---

### Q: How does conversation history work?

**A**: Messages are accumulated in a list:

```python
# Initial question
messages = [
    {"role": "system", "content": system_prompt},
    {"role": "user", "content": "What's my weight?"}
]

# After first response
messages.append({
    "role": "assistant",
    "content": "Your current weight is 75.2kg..."
})

# Follow-up question
messages.append({
    "role": "user",
    "content": "Has it changed this month?"
})

# GPT-4 sees full context
# Can reference "75.2kg" from previous message
```

**History management**:
- Keep last 5-10 turns (prevent token overflow)
- Prune old tool results (compress to summaries)
- Maintain thread_id for continuity

---

## Summary

The Coach Orchestrator is an **AI-powered conversational interface** that:

1. **Understands natural language**:
   - Questions about personal data
   - General fitness knowledge requests
   - Multi-faceted inquiries

2. **Intelligently routes to tools**:
   - Personal data (profile, logs, body composition)
   - Knowledge base (RAG for evidence-based info)
   - Specialist agents (Nutrition, Training analysis)

3. **Synthesizes comprehensive answers**:
   - Combines multiple data sources
   - Explains algorithmic decisions
   - Provides context and education

4. **Maintains conversation context**:
   - Multi-turn dialogues
   - References previous exchanges
   - Adapts to user's level

**Key Architecture**:
- **Layer 1**: GPT-4 orchestration (conversation, tool selection)
- **Layer 2**: Deterministic execution (specialist agents, data access)

**Design Principles**:
- **Data-driven**: Always reference actual numbers
- **Educational**: Explain the "why"
- **Read-only**: Explain, don't modify
- **Tool-grounded**: Prevent hallucinations

The Coach is the **user-facing interface** that makes the deterministic agents' outputs accessible and understandable through natural conversation!
