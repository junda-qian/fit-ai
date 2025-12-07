# Coach Orchestrator Agent Specification
## Conversational AI Coach with OpenAI SDK

---

## Executive Summary

The Coach Orchestrator is an **on-demand conversational AI agent** that provides interactive coaching through natural language Q&A. Unlike the deterministic Nutrition and Training agents that run automatically on schedules, the Coach Orchestrator responds to user questions anytime, providing personalized guidance by intelligently calling specialist agents and analyzing user data.

**Key Characteristics:**
- **Trigger**: On-demand (user-initiated chat)
- **Framework**: OpenAI SDK with function calling
- **Purpose**: Natural language interface to the fitness coaching system
- **Intelligence**: AI-powered reasoning and dynamic tool selection

---

## Table of Contents

1. [Objectives](#objectives)
2. [Why OpenAI SDK?](#why-openai-sdk)
3. [Architecture](#architecture)
4. [Use Cases](#use-cases)
5. [Function Tools](#function-tools)
6. [Conversation Flow](#conversation-flow)
7. [Integration with Deterministic Agents](#integration-with-deterministic-agents)
8. [Implementation Details](#implementation-details)
9. [Deployment](#deployment)
10. [Cost Considerations](#cost-considerations)

---

## Objectives

### Primary Goals

1. **Natural Language Interface**
   - Users ask questions in plain English
   - No need to navigate complex menus or understand technical terms
   - Conversational, helpful, and educational tone

2. **Intelligent Data Access**
   - Dynamically fetch relevant user data
   - Call specialist agents when needed
   - Synthesize information from multiple sources

3. **Personalized Coaching**
   - Context-aware responses based on user history
   - Tailored advice considering current goals, progress, and preferences
   - Educational explanations that help users learn

4. **Transparent Reasoning**
   - Explain why recommendations are made
   - Reference specific data points
   - Help users understand the "why" behind their plan

### Secondary Goals

- Reduce cognitive load (users don't need to analyze their own data)
- Increase engagement and adherence
- Provide motivation and encouragement
- Handle edge cases that deterministic agents can't

---

## Why OpenAI SDK?

### The Right Tool for Conversational AI

Unlike the Nutrition and Training agents (which follow deterministic rules), the Coach Orchestrator needs:

| Requirement | Why OpenAI SDK is Optimal |
|-------------|--------------------------|
| **Multi-turn conversations** | Built-in conversation state management |
| **Dynamic tool selection** | AI decides which functions to call based on user question |
| **Context understanding** | Interprets natural language queries accurately |
| **Adaptive responses** | Tailors explanations to user's level of understanding |
| **Function calling** | Native support for calling specialist agents and data tools |
| **Structured outputs** | Forces JSON schema compliance for reliable integrations |

### Comparison: Why NOT Pure Python for Chat?

**Pure Python (Deterministic):**
```python
if "calories" in user_question and "reduce" in user_question:
    return "Call nutrition agent"
# ❌ Brittle, can't handle variations
# ❌ Can't understand context or nuance
# ❌ Limited to predefined patterns
```

**OpenAI SDK (AI-Powered):**
```python
# AI understands variations:
"Should I eat less?" → Calls nutrition agent
"I'm gaining weight too fast" → Calls nutrition + body composition analysis
"What's wrong with my diet?" → Analyzes nutrition logs + calls specialist
# ✅ Flexible, context-aware
# ✅ Handles unexpected questions
# ✅ Learns from conversation
```

### Why NOT Other AI Frameworks?

| Framework | Pros | Cons | Verdict |
|-----------|------|------|---------|
| **OpenAI SDK** | Native function calling, great docs, proven patterns | Requires OpenAI API key | ✅ **Best choice** |
| **AWS Bedrock + Claude** | AWS-native, no external API | No built-in agent framework (manual tool calling) | ⚠️ More work to implement |
| **LangChain** | Full-featured, model-agnostic | Heavy dependency, overkill for this use case | ❌ Too complex |
| **LlamaIndex** | Great for RAG/documents | Not focused on conversational agents | ❌ Wrong use case |

**Decision: OpenAI SDK** because it's purpose-built for conversational agents with function calling.

---

## Architecture

### System Overview

```
┌─────────────────────────────────────────────────────────────────┐
│                 CONVERSATIONAL COACH LAYER                       │
│                      (OpenAI SDK)                                │
└─────────────────────────────────────────────────────────────────┘
                              │
                              │ User asks question
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│              Coach Orchestrator Agent (OpenAI SDK)               │
│  - Multi-turn conversation management                           │
│  - Natural language understanding                               │
│  - Dynamic function calling                                     │
│  - Context-aware responses                                      │
└────────────────────┬────────────────────────────────────────────┘
                     │
                     │ Calls function tools as needed
                     ▼
┌─────────────────────────────────────────────────────────────────┐
│                    Function Tools Layer                          │
│  ┌─────────────────────────────────────────────────────────┐   │
│  │ Data Retrieval Tools:                                   │   │
│  │ • get_user_profile()                                    │   │
│  │ • get_nutrition_logs(days=7)                            │   │
│  │ • get_workout_logs(days=14)                             │   │
│  │ • get_body_logs(days=14)                                │   │
│  │ • get_weekly_analysis(week)                             │   │
│  └─────────────────────────────────────────────────────────┘   │
│  ┌─────────────────────────────────────────────────────────┐   │
│  │ Specialist Agent Tools:                                 │   │
│  │ • get_nutrition_recommendation()                        │   │
│  │ • get_training_status(exercise)                         │   │
│  │ • analyze_progress(metric, timeframe)                   │   │
│  └─────────────────────────────────────────────────────────┘   │
│  ┌─────────────────────────────────────────────────────────┐   │
│  │ Plan Management Tools:                                  │   │
│  │ • preview_calorie_adjustment(new_calories)              │   │
│  │ • explain_weekly_changes()                              │   │
│  │ • get_macro_breakdown()                                 │   │
│  └─────────────────────────────────────────────────────────┘   │
└────────────────────┬────────────────────────────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────────────────────────────┐
│              DETERMINISTIC AGENT LAYER                           │
│  (Pure Python - Fast, Reliable, Testable)                       │
│                                                                  │
│  ┌──────────────────┐  ┌──────────────────┐  ┌──────────────┐  │
│  │    Nutrition     │  │    Training      │  │Communication │  │
│  │   Specialist     │  │   Specialist     │  │  Specialist  │  │
│  │  (Deterministic) │  │  (Deterministic) │  │  (Bedrock)   │  │
│  └──────────────────┘  └──────────────────┘  └──────────────┘  │
└─────────────────────────────────────────────────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────────────────────────────┐
│                      Database Layer                              │
│  • user_profiles    • body_logs         • weekly_analyses       │
│  • nutrition_logs   • workout_logs      • active_plans          │
└─────────────────────────────────────────────────────────────────┘
```

### Agent Flow

```
User Question → Coach Orchestrator → AI Reasoning → Function Calls → Response
                       ↓
                Context Memory
                  (Thread)
```

**Example Flow:**

1. **User**: "Why did my calories change this week?"
2. **Coach**: *Analyzes question* → Calls `get_weekly_analysis(latest)`
3. **Coach**: *Reads analysis* → Calls `get_body_logs(14 days)` for context
4. **Coach**: *Synthesizes* → Generates personalized explanation
5. **User**: "Will I have energy for workouts?"
6. **Coach**: *Uses conversation context* → Calls `get_training_status()`
7. **Coach**: *Responds* with calorie/performance analysis

---

## Use Cases

### 1. Understanding Plan Changes

**User Question:**
> "My meal plan changed today. Why?"

**Coach Actions:**
1. Calls `get_weekly_analysis(latest)`
2. Calls `get_nutrition_logs(days=14)`
3. Calls `get_body_logs(days=14)`

**Coach Response:**
> "Great question! Your calories were adjusted from 2200 to 2000 based on Monday's weekly analysis. Here's why:
>
> **What I observed:**
> - Your weight has been stable at 78.5kg for 14 days
> - Your skinfold measurements decreased from 50mm to 46mm (-4mm)
> - You're averaging 2180 calories/day
>
> **What this means:**
> You're in body recomposition! You're losing fat while gaining muscle, which is why the scale isn't moving. To see more visible weight loss while preserving that muscle gain, I reduced your target to 2000 calories (a 200 cal deficit).
>
> **Bottom line:** This should give you 0.25kg/week loss while keeping those strength gains. Your body fat is trending down, which is exactly what we want! 💪"

### 2. Progress Check-ins

**User Question:**
> "Am I making progress?"

**Coach Actions:**
1. Calls `get_user_profile()` → Reads goal
2. Calls `analyze_progress(metric='weight', timeframe='30_days')`
3. Calls `analyze_progress(metric='strength', timeframe='30_days')`
4. Calls `get_body_logs(days=30)`

**Coach Response:**
> "Let me pull your last 30 days... yes, you're making solid progress! 📈
>
> **Body Composition:**
> - Weight: 81kg → 78.5kg (-2.5kg / -3%)
> - Skinfolds: 55mm → 46mm (-9mm)
> - Estimated fat loss: ~2kg, muscle preserved
>
> **Strength:**
> - Squat: 100kg → 110kg (+10%)
> - Bench: 70kg → 75kg (+7%)
> - Deadlift: 120kg → 130kg (+8%)
>
> **Verdict:** You're crushing it! Losing fat while getting stronger is the dream scenario. Your current plan is working perfectly. Keep doing what you're doing! 🔥"

### 3. Nutrition Questions

**User Question:**
> "I'm going to a wedding this weekend. Should I adjust my plan?"

**Coach Actions:**
1. Calls `get_user_profile()` → Reads current goal, calories
2. Calls `get_nutrition_logs(days=7)` → Checks recent adherence
3. Calls `get_weekly_analysis(latest)` → Reviews progress

**Coach Response:**
> "Wedding weekend - fun! Here's my advice:
>
> **Context:** You're on a 2000 calorie cut, and you've been consistent (6/7 days last week). Your progress is on track.
>
> **My recommendation:**
> 1. **Friday-Sunday:** Eat at maintenance (~2400 cal)
>    - Enjoy the wedding guilt-free
>    - This won't derail your progress
>
> 2. **Monday:** Back to 2000 cal as normal
>
> **Why this works:**
> - 3 days at maintenance = ~1200 extra calories total
> - This equals ~0.15kg of fat (minimal impact)
> - Mental break helps long-term adherence
> - One weekend won't undo weeks of progress
>
> **Pro tip:** Hit your protein target (160g) even on high-cal days. This preserves muscle and keeps you satisfied.
>
> Enjoy the wedding! 🎉"

### 4. Training Questions

**User Question:**
> "My squat feels stuck. What should I do?"

**Coach Actions:**
1. Calls `get_training_status(exercise='squat')`
2. Calls `get_workout_logs(days=28, exercise='squat')`
3. Calls `get_nutrition_logs(days=7)` → Checks if in deficit

**Coach Response:**
> "Let me check your squat progression... I see what's happening.
>
> **Your squat history (last 4 weeks):**
> - Week 1: 100kg x 5 reps ✅
> - Week 2: 102.5kg x 5 reps ✅
> - Week 3: 105kg x 4 reps ⚠️
> - Week 4: 105kg x 4 reps ⚠️ (plateau)
>
> **Possible causes:**
> 1. **You're in a calorie deficit** (-500 cal/day)
>    - Harder to gain strength while losing weight
>    - This is normal and expected
>
> 2. **Volume might be too low**
>    - You're doing 3 sets of squats per week
>    - Could benefit from 4-6 sets
>
> **My recommendations:**
> 1. **Deload this week:** Drop to 95kg x 5 reps (90% of current)
> 2. **Add a second squat day:** Light squats (80kg x 8 reps)
> 3. **After deload:** Try 105kg again with more recovery
>
> **Reality check:** You're losing fat, so strength plateaus are normal. The fact that you're maintaining 105kg while in a deficit is actually impressive! Once you switch to maintenance/bulk, strength will jump up.
>
> Want me to adjust your training plan with these changes?"

### 5. Motivation & Encouragement

**User Question:**
> "I'm not seeing results anymore. Should I quit?"

**Coach Actions:**
1. Calls `get_weekly_analysis(latest)`
2. Calls `get_body_logs(days=30)`
3. Calls `get_user_profile()` → Checks how long they've been tracking
4. Calls `analyze_progress(metric='all', timeframe='60_days')`

**Coach Response:**
> "Hey, I get it - plateaus are frustrating. But let's look at the actual data before making any decisions.
>
> **Last 60 days (the full picture):**
> - Weight: 82kg → 78.5kg (-3.5kg)
> - Skinfolds: 58mm → 46mm (-12mm)
> - Squat: 95kg → 110kg (+15kg)
> - You've logged 54/60 days (90% adherence)
>
> **Last 2 weeks (the plateau):**
> - Weight: 78.5kg → 78.6kg (+0.1kg)
> - Skinfolds: 46mm → 44mm (-2mm)
>
> **What's actually happening:**
> You're NOT stuck. Your weight plateaued because you're building muscle while losing fat (body recomposition). Your skinfolds keep dropping, which means fat loss is still happening!
>
> **This is completely normal around week 8-10 of a cut.** Your body adapts, water retention fluctuates, and the scale lies.
>
> **Two options:**
> 1. **Keep going** - You're still losing fat (skinfolds prove it)
> 2. **Take a diet break** - 2 weeks at maintenance to reset
>
> You've lost 3.5kg in 60 days while getting stronger. That's textbook great progress. Don't let two weeks of scale fluctuations make you quit 60 days of solid work!
>
> What would feel better for you right now?"

### 6. Meal Planning

**User Question:**
> "What should I eat to hit my macros?"

**Coach Actions:**
1. Calls `get_user_profile()` → Gets target macros
2. Calls `get_nutrition_logs(days=1)` → What they've eaten today
3. Calls `get_macro_breakdown()` → Calculates remaining macros

**Coach Response:**
> "Let me check what you've logged today...
>
> **Your targets:** 2000 cal | 160g protein | 200g carbs | 67g fat
> **So far today:** 1200 cal | 80g protein | 120g carbs | 40g fat
>
> **You have left for dinner:**
> - 800 calories
> - 80g protein ⚠️ (need to hit this!)
> - 80g carbs
> - 27g fat
>
> **Meal ideas that fit:**
>
> **Option 1: Chicken & Rice**
> - 200g chicken breast (380 cal, 70g protein)
> - 150g white rice (200 cal, 45g carbs)
> - 1 tbsp olive oil (120 cal, 14g fat)
> - Veggies (100 cal, 20g carbs)
> - **Total:** 800 cal | 70g P | 65g C | 14g F ✅
>
> **Option 2: Salmon & Sweet Potato**
> - 180g salmon (360 cal, 40g protein, 20g fat)
> - 200g sweet potato (180 cal, 40g carbs)
> - Greek yogurt (150 cal, 25g protein)
> - **Total:** 690 cal | 65g P | 40g C | 20g F ✅
>
> Both get you close! The chicken option hits protein target better. Want more options?"

### 7. Blending Personal Data + Knowledge Base (RAG)

**User Question:**
> "My weight isn't changing. Is body recomposition real or just a myth?"

**Coach Actions:**
1. Calls `get_body_logs(days=14)` → Personal weight/skinfold data
2. Calls `get_weekly_analysis(latest)` → Current status
3. Calls `search_knowledge_base("body recomposition science evidence")` → RAG research

**Coach Response:**
> "Great question! Let me check YOUR data first, then explain the science.
>
> **Your Data (last 14 days):**
> - Weight: 80kg → 80.1kg (stable)
> - Skinfolds: 52mm → 48mm (-4mm) 📉
> - Bench press: 75kg → 77.5kg (+2.5kg) 📈
>
> **What this means:**
> You ARE in body recomposition right now! Your weight is stable but you're losing fat (skinfolds down) and gaining strength (bench up).
>
> **The Science (from research):**
> Body recomposition is absolutely real, not a myth. According to sports science research, it's most effective for:
>
> 1. **Beginners** - New training stimulus triggers rapid muscle growth
> 2. **Returning trainees** - "Muscle memory" effect accelerates regrowth
> 3. **Higher body fat** - More energy available from fat stores
> 4. **Optimized nutrition** - Sufficient protein + small deficit
>
> **Why it works:**
> - Fat loss requires energy deficit (calories out > calories in)
> - Muscle gain requires training stimulus + protein
> - Your body can use stored fat as energy for muscle building
> - This simultaneous process is slower than pure cutting or bulking
>
> **Your situation:**
> You're a textbook case! Intermediate lifter with good body fat level (18%), hitting protein targets, training consistently. This is exactly when body recomp happens.
>
> **Bottom line:** Don't let the scale discourage you. Your skinfolds and strength gains prove you're making excellent progress. Keep doing exactly what you're doing! 💪
>
> Want to know more about optimizing body recomposition?"

---

## Function Tools

### Data Retrieval Tools

```python
@function_tool
def get_user_profile(user_id: str) -> dict:
    """
    Get user profile including goals, targets, and preferences.

    Returns:
        {
            "name": "Alex",
            "goal": "lose_weight",
            "target_calories": 2000,
            "target_protein": 160,
            "body_weight_kg": 78.5,
            "body_fat_pct": 18.5,
            "training_status": "intermediate"
        }
    """

@function_tool
def get_nutrition_logs(user_id: str, days: int = 7) -> list:
    """
    Get recent nutrition logs with calories and macros.

    Returns:
        [
            {
                "date": "2025-11-14",
                "calories": 2050,
                "protein_g": 165,
                "carbs_g": 205,
                "fats_g": 68,
                "meals": [...]
            },
            ...
        ]
    """

@function_tool
def get_workout_logs(user_id: str, days: int = 14, exercise: str = None) -> list:
    """
    Get recent workout logs, optionally filtered by exercise.

    Returns:
        [
            {
                "date": "2025-11-14",
                "exercises": [
                    {
                        "name": "Squat",
                        "sets": [
                            {"weight": 100, "reps": 5},
                            {"weight": 100, "reps": 5},
                            {"weight": 100, "reps": 4}
                        ]
                    }
                ]
            },
            ...
        ]
    """

@function_tool
def get_body_logs(user_id: str, days: int = 14) -> list:
    """
    Get body composition logs (weight, skinfolds, etc).

    Returns:
        [
            {
                "date": "2025-11-14",
                "weight_kg": 78.5,
                "skinfolds": {
                    "tricep": 11,
                    "abdomen": 18,
                    "thigh": 17
                },
                "skinfold_sum": 46
            },
            ...
        ]
    """

@function_tool
def get_weekly_analysis(user_id: str, week: str = "latest") -> dict:
    """
    Get weekly analysis results from Nutrition Specialist.

    Returns:
        {
            "week_starting": "2025-11-11",
            "status": "completed",
            "data_summary": {
                "weight_change_kg": -0.3,
                "skinfold_change_mm": -2,
                "avg_calories": 2180
            },
            "issues_detected": [
                {
                    "type": "weight_plateau",
                    "description": "No weight change in 14 days",
                    "recommended_action": "reduce_calories"
                }
            ],
            "plan_updated": true,
            "updates": {
                "nutrition": {
                    "old_calories": 2200,
                    "new_calories": 2000,
                    "reasoning": "Weight plateau detected..."
                }
            }
        }
    """
```

### Specialist Agent Tools

```python
@function_tool
def get_nutrition_recommendation(user_id: str) -> dict:
    """
    Get current nutrition recommendation from Nutrition Specialist.
    Calls the deterministic nutrition agent.

    Returns:
        {
            "recommended_calories": 2000,
            "recommended_macros": {
                "protein_g": 160,
                "carbs_g": 200,
                "fats_g": 67
            },
            "adjustment_category": "decrease",
            "reasoning": "Weight plateau detected. Reduce by 200 cal...",
            "confidence": 1.0
        }
    """

@function_tool
def get_training_status(user_id: str, exercise: str = None) -> dict:
    """
    Get training status and progression recommendations.
    Calls the deterministic training agent.

    Returns:
        {
            "exercise": "Squat",
            "current_status": "plateau",
            "last_session": {
                "weight": 100,
                "reps": [5, 5, 4],
                "target_reps": 5
            },
            "next_session_prescription": {
                "weight": 102.5,
                "target_reps": 5,
                "action": "progress"
            },
            "notes": "Hit target reps. Increase weight."
        }
    """

@function_tool
def analyze_progress(user_id: str, metric: str, timeframe: str) -> dict:
    """
    Analyze progress for specific metric over timeframe.

    Args:
        metric: "weight", "strength", "body_composition", "all"
        timeframe: "7_days", "30_days", "60_days", "90_days"

    Returns:
        {
            "metric": "weight",
            "timeframe": "30_days",
            "starting_value": 81.0,
            "current_value": 78.5,
            "change": -2.5,
            "change_pct": -3.1,
            "trend": "decreasing",
            "is_on_track": true
        }
    """
```

### Plan Management Tools

```python
@function_tool
def preview_calorie_adjustment(user_id: str, new_calories: int) -> dict:
    """
    Preview what would happen if calories were adjusted.

    Returns:
        {
            "current_calories": 2000,
            "proposed_calories": 1800,
            "estimated_deficit_pct": 25,
            "estimated_weekly_loss_kg": 0.4,
            "expected_impact": "Moderate increase in fat loss rate",
            "warnings": ["This is aggressive for your body fat level"]
        }
    """

@function_tool
def explain_weekly_changes(user_id: str) -> str:
    """
    Generate detailed explanation of why plans changed this week.

    Returns natural language explanation combining data from
    weekly analysis, nutrition logs, and body composition.
    """

@function_tool
def get_macro_breakdown(user_id: str, date: str = "today") -> dict:
    """
    Get macro breakdown for a specific date.

    Returns:
        {
            "date": "2025-11-14",
            "targets": {
                "calories": 2000,
                "protein_g": 160,
                "carbs_g": 200,
                "fats_g": 67
            },
            "consumed": {
                "calories": 1200,
                "protein_g": 80,
                "carbs_g": 120,
                "fats_g": 40
            },
            "remaining": {
                "calories": 800,
                "protein_g": 80,
                "carbs_g": 80,
                "fats_g": 27
            }
        }
    """
```

### Knowledge Base Tools (RAG)

```python
@function_tool
def search_knowledge_base(query: str, top_k: int = 5) -> dict:
    """
    Search evidence-based fitness/health knowledge base using RAG.

    This tool provides access to scientific research, training principles,
    nutrition science, and evidence-based fitness information.

    Use this when users ask:
    - General fitness/health questions (not about their personal data)
    - "What is..." or "How does..." questions
    - Questions about training principles, nutrition science, sleep optimization
    - Questions about specific exercises, techniques, or methods
    - Requests to debunk myths or explain scientific concepts

    Args:
        query: User's question or search query
        top_k: Number of relevant documents to retrieve (default 5)

    Returns:
        {
            "context": str,  # Formatted context from retrieved documents
            "sources": [
                {
                    "source": "Renaissance Periodization - Training Volume Landmarks",
                    "page": 12,
                    "text": "Optimal training volume for hypertrophy...",
                    "urls": ["https://..."]
                },
                ...
            ],
            "answer": str  # AI-generated answer based on retrieved context
        }

    Examples:
        - "What's the optimal training volume for muscle growth?"
        - "How should I structure my macronutrients for fat loss?"
        - "What are evidence-based sleep optimization strategies?"
        - "Is intermittent fasting effective?"
        - "What's the best rep range for strength?"
    """
```

---

## Conversation Flow

### OpenAI SDK Conversation Pattern

```python
from openai import OpenAI

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

def handle_user_question(user_id: str, question: str, thread_id: str = None):
    """
    Handle user question using OpenAI SDK with function calling.
    """

    # Define available function tools
    tools = [
        {
            "type": "function",
            "function": {
                "name": "get_user_profile",
                "description": "Get user profile including goals and targets",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "user_id": {"type": "string"}
                    },
                    "required": ["user_id"]
                }
            }
        },
        {
            "type": "function",
            "function": {
                "name": "get_weekly_analysis",
                "description": "Get latest weekly analysis from Nutrition Specialist",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "user_id": {"type": "string"},
                        "week": {"type": "string", "default": "latest"}
                    },
                    "required": ["user_id"]
                }
            }
        },
        # ... more tools ...
    ]

    # System prompt defines agent behavior
    system_prompt = """You are an expert fitness coach with deep knowledge of
    nutrition, training, and body composition. You help users understand their
    progress, explain plan changes, and provide personalized guidance.

    Key traits:
    - Data-driven: Reference specific metrics when explaining
    - Educational: Help users understand the "why" behind recommendations
    - Encouraging: Celebrate wins, normalize plateaus and setbacks
    - Honest: Set realistic expectations, don't overpromise
    - Concise: Get to the point, avoid jargon

    You have access to function tools to fetch user data and call specialist agents.
    Use them to provide accurate, personalized responses.
    """

    # Create or continue conversation
    messages = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": question}
    ]

    # Initial API call
    response = client.chat.completions.create(
        model="gpt-4-turbo-preview",
        messages=messages,
        tools=tools,
        tool_choice="auto"  # Let AI decide which tools to call
    )

    # Handle function calls
    while response.choices[0].finish_reason == "tool_calls":
        # Extract tool calls
        tool_calls = response.choices[0].message.tool_calls

        # Execute each tool call
        for tool_call in tool_calls:
            function_name = tool_call.function.name
            function_args = json.loads(tool_call.function.arguments)

            # Call the actual function
            if function_name == "get_user_profile":
                result = get_user_profile(**function_args)
            elif function_name == "get_weekly_analysis":
                result = get_weekly_analysis(**function_args)
            # ... handle other functions ...

            # Add tool result to conversation
            messages.append({
                "role": "tool",
                "tool_call_id": tool_call.id,
                "content": json.dumps(result)
            })

        # Continue conversation with tool results
        response = client.chat.completions.create(
            model="gpt-4-turbo-preview",
            messages=messages,
            tools=tools,
            tool_choice="auto"
        )

    # Return final response
    return response.choices[0].message.content
```

### Example Execution Flow

```
User: "Why did my calories change?"
   │
   ▼
Coach Orchestrator receives question
   │
   ▼
AI decides to call: get_weekly_analysis(user_id)
   │
   ▼
Function returns: {weight_plateau detected, calories reduced}
   │
   ▼
AI decides to call: get_body_logs(user_id, days=14)
   │
   ▼
Function returns: {skinfolds decreased -2mm}
   │
   ▼
AI synthesizes response:
"Your calories changed because your weight plateaued at 78.5kg
for 14 days, but your skinfolds decreased by 2mm. This means
you're in body recomposition (gaining muscle, losing fat)..."
   │
   ▼
Response sent to user
```

---

## Integration with Deterministic Agents

### Clear Separation of Concerns

```
┌─────────────────────────────────────────────────────────────┐
│         Coach Orchestrator (OpenAI SDK)                      │
│  Responsibilities:                                           │
│  • Natural language understanding                           │
│  • Conversational responses                                 │
│  • Data fetching and synthesis                              │
│  • Educational explanations                                 │
│                                                              │
│  Does NOT:                                                   │
│  • Make nutrition/training decisions (defers to specialists)│
│  • Update plans automatically (read-only)                   │
│  • Run on schedules (only on-demand)                        │
└─────────────────────────────────────────────────────────────┘
                         │
                         │ Function calls
                         ▼
┌─────────────────────────────────────────────────────────────┐
│     Deterministic Specialists (Pure Python)                  │
│  Responsibilities:                                           │
│  • Make evidence-based decisions (Tables 1-3)               │
│  • Update plans automatically on schedule                   │
│  • Provide structured recommendations                       │
│                                                              │
│  Examples:                                                   │
│  • Nutrition Specialist: Returns calorie/macro targets      │
│  • Training Specialist: Returns next session prescription   │
└─────────────────────────────────────────────────────────────┘
```

### Function Call Pattern

When Coach Orchestrator needs specialist advice:

```python
# Coach Orchestrator calls function tool
result = get_nutrition_recommendation(user_id="user_123")

# Nutrition Specialist (deterministic) executes
# Returns structured recommendation
{
    "recommended_calories": 2000,
    "adjustment_category": "decrease",
    "reasoning": "Weight plateau detected. Body fat decreasing..."
}

# Coach Orchestrator uses this data to craft response
# But does NOT modify the recommendation
# It explains it in natural language
```

**Key principle:** Coach explains, Specialists decide.

---

## Implementation Details

### Project Structure

```
ai_agents/
├── shared/
│   ├── models.py           # Pydantic models
│   └── db_client.py        # Database interface
│
├── nutrition_specialist/   # Deterministic (Pure Python)
│   ├── lambda_handler.py
│   └── algorithm.py
│
├── training_specialist/    # Deterministic (Pure Python)
│   ├── lambda_handler.py
│   └── algorithm.py
│
├── communication_specialist/  # AI-powered (Bedrock)
│   ├── lambda_handler.py
│   └── prompts.py
│
└── coach_orchestrator/     # AI-powered (OpenAI SDK) ⭐
    ├── lambda_handler.py   # API Gateway handler
    ├── agent.py            # OpenAI SDK conversation logic
    ├── tools.py            # Function tool definitions
    ├── prompts.py          # System prompts
    └── test_coach.py       # Unit tests
```

### Lambda Handler

```python
# ai_agents/coach_orchestrator/lambda_handler.py

import json
import os
from .agent import CoachAgent

def lambda_handler(event, context):
    """
    Handle user questions via API Gateway.

    POST /api/coach/ask
    Body: {
        "user_id": "user_123",
        "question": "Why did my calories change?",
        "thread_id": "thread_abc" (optional, for multi-turn)
    }
    """

    # Parse request
    body = json.loads(event['body'])
    user_id = body['user_id']
    question = body['question']
    thread_id = body.get('thread_id')

    # Initialize coach agent
    coach = CoachAgent(
        openai_api_key=os.getenv('OPENAI_API_KEY'),
        user_id=user_id
    )

    # Get response
    response = coach.handle_question(question, thread_id)

    # Return response
    return {
        'statusCode': 200,
        'body': json.dumps({
            'response': response['message'],
            'thread_id': response['thread_id']
        })
    }
```

### Agent Implementation

```python
# ai_agents/coach_orchestrator/agent.py

from openai import OpenAI
from .tools import get_available_tools, execute_tool
from .prompts import get_system_prompt

class CoachAgent:
    def __init__(self, openai_api_key: str, user_id: str):
        self.client = OpenAI(api_key=openai_api_key)
        self.user_id = user_id
        self.model = "gpt-4-turbo-preview"

    def handle_question(self, question: str, thread_id: str = None):
        """Handle user question with function calling"""

        # Build conversation
        messages = [
            {"role": "system", "content": get_system_prompt()},
            {"role": "user", "content": question}
        ]

        # Get available tools
        tools = get_available_tools()

        # Initial API call
        response = self.client.chat.completions.create(
            model=self.model,
            messages=messages,
            tools=tools,
            tool_choice="auto"
        )

        # Handle function calls
        while response.choices[0].finish_reason == "tool_calls":
            tool_calls = response.choices[0].message.tool_calls

            for tool_call in tool_calls:
                # Execute tool
                result = execute_tool(
                    tool_call.function.name,
                    json.loads(tool_call.function.arguments),
                    self.user_id
                )

                # Add to conversation
                messages.append({
                    "role": "tool",
                    "tool_call_id": tool_call.id,
                    "content": json.dumps(result)
                })

            # Continue conversation
            response = self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                tools=tools
            )

        return {
            "message": response.choices[0].message.content,
            "thread_id": thread_id  # For future multi-turn support
        }
```

### System Prompt

```python
# ai_agents/coach_orchestrator/prompts.py

def get_system_prompt() -> str:
    return """You are an expert fitness coach helping users achieve their goals.

Your expertise:
- Nutrition science and energy balance
- Progressive overload and training principles
- Body composition and measurement techniques
- Behavior change and adherence strategies

Your approach:
1. **Data-driven**: Reference specific metrics (weight, skinfolds, strength)
2. **Educational**: Explain the "why" behind recommendations
3. **Encouraging**: Celebrate progress, normalize plateaus
4. **Realistic**: Set honest expectations, acknowledge challenges
5. **Concise**: Be clear and direct, avoid unnecessary jargon

Key facts about the system:
- Nutrition and Training Specialists run automatically every week
- They use evidence-based algorithms (not AI) to adjust plans
- Your job is to explain their decisions and help users understand
- You have read-only access (you explain, you don't modify plans)

When users ask questions:
1. Use function tools to fetch relevant data
2. Synthesize information from multiple sources
3. Provide clear, actionable answers
4. Reference specific numbers to build trust
5. Encourage continued adherence

Remember: You're a supportive coach, not a drill sergeant. Build trust through transparency and education."""
```

---

## Deployment

### AWS Lambda Configuration

```hcl
# terraform/lambda_coach_orchestrator.tf

resource "aws_lambda_function" "coach_orchestrator" {
  function_name = "${local.name_prefix}-coach-orchestrator"
  role          = aws_iam_role.coach_orchestrator_role.arn

  runtime = "python3.11"
  handler = "lambda_handler.lambda_handler"
  timeout = 30  # Function calling may take longer

  environment {
    variables = {
      OPENAI_API_KEY            = var.openai_api_key
      DYNAMODB_TABLE_PREFIX     = local.name_prefix
      NUTRITION_SPECIALIST_ARN  = aws_lambda_function.nutrition_specialist.arn
      TRAINING_SPECIALIST_ARN   = aws_lambda_function.training_specialist.arn
    }
  }
}

# API Gateway endpoint
resource "aws_apigatewayv2_route" "coach_ask" {
  api_id    = aws_apigatewayv2_api.main.id
  route_key = "POST /api/coach/ask"

  target = "integrations/${aws_apigatewayv2_integration.coach_orchestrator.id}"
}
```

### Environment Variables

```bash
# Required
OPENAI_API_KEY=sk-...                    # OpenAI API key
DYNAMODB_TABLE_PREFIX=fitness-app-dev    # Table name prefix

# Optional
OPENAI_MODEL=gpt-4-turbo-preview         # Model to use
OPENAI_MAX_TOKENS=1024                   # Max response length
CONVERSATION_TIMEOUT_HOURS=24            # Thread expiry
```

### IAM Permissions

```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Action": [
        "dynamodb:GetItem",
        "dynamodb:Query"
      ],
      "Resource": [
        "arn:aws:dynamodb:*:*:table/fitness-app-*"
      ]
    },
    {
      "Effect": "Allow",
      "Action": [
        "lambda:InvokeFunction"
      ],
      "Resource": [
        "arn:aws:lambda:*:*:function:fitness-app-nutrition-specialist",
        "arn:aws:lambda:*:*:function:fitness-app-training-specialist"
      ]
    }
  ]
}
```

---

## Cost Considerations

### OpenAI API Pricing (as of 2024)

| Model | Input | Output | Use Case |
|-------|--------|--------|----------|
| GPT-4 Turbo | $10 / 1M tokens | $30 / 1M tokens | Production |
| GPT-3.5 Turbo | $0.50 / 1M tokens | $1.50 / 1M tokens | Development |

### Estimated Costs

**Assumptions:**
- Average conversation: 3 turns (user → AI → user → AI → user → AI)
- Average input: 500 tokens per turn
- Average output: 300 tokens per turn
- Average function calls: 2 per conversation

**Cost per conversation (GPT-4 Turbo):**
```
Input:  3 turns × 500 tokens = 1,500 tokens = $0.015
Output: 3 turns × 300 tokens =   900 tokens = $0.027
Function calls: 2 × 200 tokens =   400 tokens = $0.006
─────────────────────────────────────────────────────
Total per conversation:                        $0.048
```

**Monthly costs:**
```
1,000 users × 4 conversations/month × $0.048 = $192/month
```

**Cost optimization strategies:**
1. **Use GPT-3.5 Turbo for simple questions** (80% cheaper)
2. **Cache system prompts** (reduce input tokens)
3. **Implement conversation limits** (e.g., 10 questions/user/day)
4. **Stream responses** (better UX, same cost)

---

## Success Metrics

### User Engagement
- Number of questions asked per user per week
- Conversation completion rate
- User satisfaction ratings

### System Performance
- Average response time (<3 seconds)
- Function calling accuracy (>95%)
- Conversation coherence score

### Business Impact
- Increased user retention (compared to no chat)
- Reduced support ticket volume
- Higher plan adherence rates

---

## Future Enhancements

### Phase 7: Advanced Features

1. **Multi-turn Memory**
   - Remember user preferences across sessions
   - Reference past conversations
   - Personalize tone and detail level

2. **Proactive Coaching**
   - AI detects when users might be struggling
   - Sends encouragement before they ask
   - Suggests interventions based on patterns

3. **Voice Interface**
   - Integrate with OpenAI Whisper (speech-to-text)
   - Enable voice conversations
   - Hands-free coaching during workouts

4. **Image Analysis**
   - Analyze progress photos
   - Estimate body composition from images
   - Provide visual feedback

5. **Integration with Wearables**
   - Fetch sleep data, heart rate variability
   - Adjust recommendations based on recovery
   - Detect overtraining earlier

---

## Summary

The Coach Orchestrator with OpenAI SDK provides:

✅ **Natural language interface** to the fitness system
✅ **Intelligent data access** via function calling
✅ **Personalized explanations** of plan changes
✅ **Educational coaching** that helps users learn
✅ **Seamless integration** with deterministic agents

**Best of both worlds:**
- **Deterministic core** (Nutrition, Training) = Fast, reliable, testable
- **AI conversation layer** (Coach) = Flexible, adaptive, engaging

This architecture ensures:
- Critical decisions (nutrition, training) remain deterministic
- User experience is enhanced with natural conversation
- System is scalable, maintainable, and cost-effective

**Implementation timeline:** Phase 6 (Week 7) after core agents are complete.
