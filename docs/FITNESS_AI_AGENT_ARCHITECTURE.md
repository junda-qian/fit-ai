# Fitness AI Agent Architecture
## Multi-Agent System with Tools and MCP Servers

Inspired by ALEX Financial Planner's multi-agent architecture, adapted for fitness coaching.

---

## Executive Summary

This document outlines a multi-agent AI fitness coaching system that:
- **Proactively monitors** user progress with weekly automated analysis
- Uses **specialized agents** for nutrition, training, recovery, and analytics
- **Automatically adjusts** meal and training plans based on detected trends
- Integrates **function tools** for calculations and data access
- Leverages **MCP servers** for external data (USDA food DB, exercise library)
- Follows **OpenAI Agents SDK patterns** from the ALEX project
- Deploys as **AWS Lambda functions** with EventBridge scheduling
- Provides **intelligent coordination** between potentially conflicting advice
- Uses **14-day trend analysis** to filter out daily noise (water retention, sleep variance)

### **Key Paradigm Shift: Proactive vs Reactive**

**Traditional AI Coach (Reactive):**
- ❌ User notices plateau → asks "what should I do?"
- ❌ Requires user to diagnose their own problems
- ❌ Reactive intervention only

**This AI Coach (Proactive):** ⭐
- ✅ AI monitors progress automatically every week
- ✅ AI detects plateaus, anomalies, overtraining signals
- ✅ AI adjusts plans automatically with transparent reasoning
- ✅ User just logs data and follows updated plan
- ✅ Like having a real coach checking in weekly

**User Experience:**
1. User logs workouts, nutrition, weight, and body composition consistently
2. Every Monday: AI analyzes last 14 days of data (weight, body fat %, workouts, nutrition)
3. AI detects issues (plateau, body recomposition, too fast/slow progress, overtraining)
4. AI updates meal/training plan if needed using personalized deficit/surplus calculations
5. User receives notification with changes + reasoning (e.g., "Body fat decreased despite weight plateau - keep current calories!")
6. User follows updated plan (no diagnosis required)

---

## Key Learnings from ALEX Backend

### 1. **Orchestrator Pattern**
- **Planner agent** coordinates specialist agents via function tools
- Each specialist has a single responsibility
- Orchestrator decides which agents to invoke based on context

### 2. **Structured Output with Pydantic**
- Use `output_type` parameter for validated responses
- Pydantic models ensure data quality
- Field validators enforce business rules (e.g., macros sum to 100%)

### 3. **Pre-processing Before AI**
- Handle deterministic logic outside agents (e.g., `handle_missing_instruments`)
- Only use AI for decisions requiring reasoning
- Reduces costs and improves reliability

### 4. **Context Wrapper Pattern**
- `RunContextWrapper[ContextClass]` provides clean context access to tools
- Tools are stateless, context provides state
- Easy to test and reason about

### 5. **MCP Server Integration**
- Playwright MCP for web research in ALEX Researcher
- Clean async context manager pattern
- Proper lifecycle management in Lambda

### 6. **Lambda as Microservices**
- Each agent = separate Lambda function
- Function tools invoke other Lambdas
- Enables independent scaling and deployment

---

## Coaching Model: Proactive vs Reactive

### **Primary Mode: Proactive Weekly Analysis** ⭐

The AI coach operates like a real coach - monitoring your progress automatically and adjusting your plan as needed.

**How it works:**
1. **Every Monday at 6 AM**: EventBridge triggers weekly analysis for all active users
2. **14-day trend analysis**: Pulls last 2 weeks of data (weight, workouts, sleep, nutrition)
3. **Issue detection**: Identifies plateaus, anomalies, overtraining signals
4. **Automatic adjustments**: Updates meal/training plans if needed
5. **Notification**: User receives summary of changes and reasoning

**Why 14 days?**
- Daily weight fluctuates due to water retention, sodium intake, hormones
- Workout performance varies with sleep, stress, recovery
- 7-14 days is minimum timeframe to detect true trends
- Matches real-world coaching check-in frequency

**User experience:**
- ✅ User's job: Log data consistently
- ✅ Agent's job: Monitor trends, detect issues, adjust plans
- ✅ User just follows the updated plan without diagnosis/thinking

### **Secondary Mode: On-Demand Chat**

Users can still ask questions anytime for:
- Exercise form tips
- Meal substitutions
- Motivation and encouragement
- Understanding why changes were made
- Specific scenarios (e.g., "I have a wedding next month")

But NOT needed for routine plan adjustments - those happen automatically.

---

## Proposed Architecture

### **Agent Structure**

```
┌─────────────────────────────────────────────────────┐
│     EventBridge Scheduler (Every Monday 6 AM)        │
│          Triggers weekly analysis cron               │
└────────────────────┬────────────────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────────────────┐
│       Weekly Analysis Coordinator                    │
│  - Fetch all active users                           │
│  - Trigger analysis Lambda for each user            │
└────────────────────┬────────────────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────────────────┐
│       Weekly Progress Analyzer Agent ⭐              │
│  FOR EACH USER:                                     │
│  1. Pull last 14 days of data                       │
│  2. Calculate trends (weight, strength, volume)     │
│  3. Detect anomalies/plateaus                       │
│  4. Determine if plan adjustment needed             │
│  5. If yes → invoke specialist agents               │
└────────────────────┬────────────────────────────────┘
                     │
     ┌───────────────┼──────────┬──────────────┐
     │               │          │              │
     ▼               ▼          ▼              ▼
┌─────────┐ ┌────────────┐ ┌──────────┐ ┌─────────┐
│Nutrition│ │  Training  │ │ Recovery │ │Analytics│
│Specialist│ │ Specialist │ │Specialist│ │Specialist│
└────┬────┘ └─────┬──────┘ └────┬─────┘ └────┬────┘
     │            │              │            │
     │       Function Tools      │            │
     ▼            ▼              ▼            ▼
┌─────────────────────────────────────────────────────┐
│               Function Tools Layer                   │
│  - calculate_tdee()                                  │
│  - calculate_macros()                                │
│  - analyze_weight_trend(days=14)                     │
│  - detect_strength_plateau(weeks=3)                  │
│  - calculate_1rm()                                   │
│  - detect_overtraining()                             │
│  - analyze_volume_trend(weeks=2)                     │
└─────────────┬───────────────────────────────────────┘
              │
     ┌────────┼─────────┬─────────────┐
     ▼        ▼         ▼             ▼
┌──────┐ ┌────────┐ ┌────────┐ ┌──────────┐
│ USDA │ │Exercise│ │Metrics │ │DynamoDB  │
│ MCP  │ │  MCP   │ │ Tools  │ │ Client   │
└──────┘ └────────┘ └────────┘ └──────────┘
                                     │
                     ┌───────────────┴──────────────┐
                     ▼                              ▼
              ┌──────────────┐            ┌─────────────────┐
              │ active_plans │            │ weekly_analyses │
              │   (table)    │            │     (table)     │
              └──────────────┘            └─────────────────┘
```

---

## Agent Specifications

### **1. Weekly Progress Analyzer Agent** ⭐ (Primary - Orchestrator)

**Purpose**: Orchestrate weekly check-ins by coordinating specialist agents and managing plan updates

**Trigger**: EventBridge cron (every Monday 6 AM UTC)

**Key Design Principle**:
> The analyzer is an **orchestrator**, not a decision-maker. It gathers data and coordinates specialists who make domain-specific decisions using their expert algorithms. This avoids the problem of using fixed thresholds that don't account for individual differences (body fat %, training status, sex, etc.).

**Responsibilities**:
- Pull last 14-28 days of user data (weight, body composition, workouts, nutrition, sleep)
- Calculate trends and prepare shared context for all specialists
- **Always invoke specialist agents** with full context (they decide if changes are needed)
- Coordinate multiple specialists (Nutrition, Training, Recovery, Analytics)
- Resolve conflicts between specialist recommendations
- Aggregate updates from all specialists
- Generate integrated user notification with reasoning
- Store weekly analysis results in DynamoDB
- Track adjustment history to prevent over-correction

**Why Always Invoke Specialists?**
- ✅ Specialists have domain expertise and context-aware algorithms
- ✅ No fixed thresholds - each user's "plateau" is different based on body composition, goals, training status
- ✅ Specialists can detect nuances (e.g., body recomposition vs true plateau)
- ✅ Enables multi-factor decision making (weight + body fat + strength + recovery)
- ✅ Cost is negligible (~$0.001 per invocation × once/week)
- ✅ Simple orchestrator code - all complexity in specialists where it belongs

**Function Tools**:
- `analyze_weight_trend(user_id, days=14)` → TrendAnalysis
- `analyze_body_composition_trend(user_id, days=14)` → BodyCompositionAnalysis
- `analyze_strength_trends(user_id, weeks=4)` → StrengthAnalysis
- `analyze_volume_trend(user_id, weeks=2)` → VolumeAnalysis
- `calculate_recovery_metrics(user_id)` → RecoveryMetrics
- `invoke_nutrition_specialist(user_id, context)` → NutritionRecommendation
- `invoke_training_specialist(user_id, context)` → TrainingRecommendation
- `invoke_recovery_specialist(user_id, context)` → RecoveryRecommendation
- `invoke_analytics_specialist(user_id, context)` → ProgressReport

**Data Quality Requirements**:
```python
# Minimum data requirements for meaningful analysis
min_weight_logs = 5                     # Need 5+ logs in 14 days
min_body_composition_logs = 2           # Need 2+ measurements in 14 days (skinfolds/waist/BF%)
min_workout_logs = 2                    # Need 2+ workouts in 14 days
min_nutrition_logs = 10                 # Need 10+ days of nutrition tracking

# If minimum data not met, notify user to improve tracking consistency
# Still invoke specialists - they can handle missing data gracefully
```

**Example Flow**:
```python
# Monday 6 AM: EventBridge triggers weekly analysis for user_123

# Step 1: Gather ALL data and calculate trends (deterministic)
context = {
    "user_profile": {
        "goal": "lose_weight",
        "sex": "male",
        "body_fat_pct": 20.5,
        "training_status": "intermediate"
    },
    "weight_trend": {
        "starting_weight": 78.5,
        "current_weight": 78.4,
        "weekly_rate_kg": -0.07,  # Very slow loss
        "weekly_rate_pct": 0.09,  # 0.09% per week
    },
    "body_comp_trend": {
        "method": "skinfolds",
        "starting_sum": 50,
        "current_sum": 48,
        "change_mm": -2,  # Fat decreasing!
        "trend": "decreasing"
    },
    "nutrition_summary": {
        "avg_calories": 2180,
        "days_logged": 12
    },
    "workout_summary": {
        "sessions": 4,
        "squat_1rm_estimate": 100,  # No change in 4 weeks
        "squat_1rm_4weeks_ago": 100
    }
}

# Step 2: Always invoke specialists with full context
# (They make the decisions, not the orchestrator)

nutrition_rec = await invoke_nutrition_specialist(user_id, context)
# Nutrition Specialist applies Nutrition Agent Reasoning algorithm:
# - Sees weight plateau (0.09% weekly) BUT skinfolds decreasing (-2mm)
# - Recognizes: Body recomposition happening!
# - Decision: MAINTAIN current calories
# Returns: {"adjustment_category": "none", "reasoning": "..."}

training_rec = await invoke_training_specialist(user_id, context)
# Training Specialist:
# - Sees squat plateau (no progression in 4 weeks)
# - Decision: Modify program to break plateau
# Returns: {"has_recommendations": true, "changes": [...]}

recovery_rec = await invoke_recovery_specialist(user_id, context)
# Returns: {"sleep_adequate": true, "needs_deload": false}

analytics_report = await invoke_analytics_specialist(user_id, context)
# Returns: Progress summary, charts, insights

# Step 3: Resolve conflicts (if any)
# (None in this case - nutrition says maintain, training says adjust program)

# Step 4: Aggregate updates
updates = {
    "nutrition": None,  # No change needed (recomp happening)
    "training": training_rec.changes,  # Apply squat program change
    "recovery": None
}

# Step 5: Store analysis
await db.weekly_analyses.insert({
    "user_id": user_123,
    "week_starting": "2025-11-04",
    "context": context,
    "recommendations": {
        "nutrition": nutrition_rec,
        "training": training_rec,
        "recovery": recovery_rec
    },
    "updates_applied": updates,
    "analyzed_at": datetime.now()
})

# Step 6: Send integrated notification
await send_notification(user_id, {
    "title": "Weekly Check-In (Nov 4, 2025)",
    "nutrition": "✅ Maintaining calories (2180) - body recomposition happening!",
    "training": "🔧 Squat program adjusted to break plateau",
    "analytics": analytics_report.summary
})
```

**Structured Output**:
```python
class WeeklyAnalysisResult(BaseModel):
    user_id: str
    week_starting: date

    # Context gathered (deterministic data)
    context: AnalysisContext  # Weight trends, body comp, workouts, nutrition, recovery

    # Specialist recommendations (AI decisions)
    recommendations: SpecialistRecommendations
    #   nutrition: NutritionRecommendation
    #   training: TrainingRecommendation
    #   recovery: RecoveryRecommendation
    #   analytics: ProgressReport

    # Updates actually applied (after conflict resolution)
    updates_applied: Dict[str, Any]  # {"nutrition": None, "training": {...}, "recovery": None}

    # Metadata
    plan_updated: bool  # True if any specialist recommended changes
    notification_sent: bool
    analyzed_at: datetime
```

**Lambda**: `fitness-weekly-analyzer`

---

### **2. Coach Orchestrator Agent** (Secondary - On-Demand Chat)

**Purpose**: Handle user questions and provide coaching advice on-demand

**Trigger**: User submits question via `/api/coach/ask`

**Responsibilities**:
- Understand user's question/goal
- Determine which specialists to consult
- Resolve conflicting advice if needed
- Generate cohesive coaching response
- Handle specific scenarios (e.g., "I have a vacation coming up")

**Function Tools**:
- `invoke_nutrition_specialist()`
- `invoke_training_specialist()`
- `invoke_recovery_specialist()`
- `invoke_analytics_specialist()`
- `invoke_motivation_agent()`

**Example Questions**:
- "Can I substitute chicken with tofu in my meal plan?"
- "My knee hurts during squats, what should I do?"
- "How can I stay on track during vacation?"
- "Why did you reduce my calories this week?"

**Lambda**: `fitness-coach-orchestrator`

---

### **3. Nutrition Specialist Agent**

**Purpose**: Analyzes nutrition data and provides evidence-based calorie/macro recommendations

**Input Context**:
- User profile (age, weight, height, sex, activity level, body fat %, goal)
- Recent nutrition logs (last 14-30 days)
- Weight trend data (14-day analysis)
- Body fat trend data (14-day analysis)
- Current training status (novice/intermediate/advanced)
- Strength progression data (for bulking scenarios)

**Responsibilities**:
- Detect calorie/macro plateau patterns
- Calculate optimal deficit/surplus using evidence-based tables (see **Nutrition Agent Reasoning** section)
- Distinguish between weight plateau and body recomposition
- Recommend personalized calorie adjustments based on:
  - Body fat percentage
  - Observed weight loss/gain rate
  - Training status
  - Strength progression
- Generate meal plans using USDA MCP
- Suggest macro splits based on goals
- Coordinate with Training Specialist when needed (e.g., bulking with poor strength gains)

**Algorithm Overview**:

**For Cutting (Fat Loss):**
1. Analyze 14-day weight and body fat trends
2. If plateau: Check body fat change
   - Fat unchanged → create deficit based on body fat % (5-50% depending on leanness)
   - Fat decreasing → no changes (body recomposition occurring)
3. If weight loss happening:
   - Calculate observed weekly loss rate
   - Estimate current deficit from loss rate
   - Compare to optimal deficit for body fat level
   - Adjust calories to match optimal deficit

**For Bulking (Muscle Gain):**
1. Analyze weight, body fat, and strength trends
2. Apply surplus based on training status (5-15% novice, 2-7% intermediate, 1-3% advanced)
3. Monitor for excessive fat gain
4. Coordinate with Training Specialist if strength not progressing

**See "Nutrition Agent Reasoning" section for complete decision trees and tables.**

**Function Tools**:
- `calculate_tdee(weight, height, age, sex, activity_level)` → float
- `calculate_macros(calories, goal)` → MacroSplit
- `analyze_weight_trend(days=14)` → TrendAnalysis (weekly rate, plateau detection)
- `analyze_body_composition_trend(days=14)` → BodyCompositionAnalysis (method, trend, confidence)
  - Prioritizes skinfolds > waist > body fat % > inference
  - Returns trend direction and confidence level
- `estimate_maintenance_calories(current_intake, weight_loss_rate)` → float
- `calculate_optimal_deficit(body_fat_pct, sex)` → float (%)
- `calculate_optimal_surplus(training_status)` → float (%)
- `search_high_protein_foods(max_calories)` → List[Food] (via USDA MCP)

**Structured Output**:
```python
class NutritionRecommendation(BaseModel):
    # Current state
    current_calorie_average: float
    current_body_fat_pct: Optional[float]
    observed_weekly_weight_change_pct: float

    # Recommendations
    recommended_calories: float
    recommended_deficit_or_surplus_pct: float
    optimal_deficit_or_surplus_pct: float  # Target based on body fat/training status
    recommended_macros: MacroSplit

    # Reasoning
    reasoning: str
    body_composition_status: str  # "plateau", "recomp", "cutting", "bulking"
    adjustment_category: str  # "none", "increase", "decrease", "maintain"

    # Optional meal plan
    meal_plan: Optional[List[Meal]]
    confidence: float  # 0.0-1.0
```

**Lambda**: `fitness-nutrition-specialist`

---

### **4. Training Specialist Agent**

**Purpose**: Analyzes workout data and provides program recommendations

**Input Context**:
- User profile (experience level, available equipment)
- Recent workout logs (last 4-8 weeks)
- Exercise performance trends
- Current goals (strength/hypertrophy/endurance)

**Responsibilities**:
- Detect strength plateaus per exercise
- Recommend progressive overload strategies
- Suggest exercise substitutions for injuries
- Generate workout programs
- Identify deload needs

**Function Tools**:
- `calculate_1rm(weight, reps)` → float
- `analyze_volume_progression(exercise_logs)` → VolumeAnalysis
- `detect_strength_plateau(exercise, logs)` → PlateauAnalysis
- `search_exercise_alternatives(exercise, constraint)` → List[Exercise] (via Exercise MCP)

**Structured Output**:
```python
class TrainingRecommendation(BaseModel):
    plateaued_exercises: List[str]
    recommended_changes: List[ProgramChange]
    progressive_overload_strategy: str
    deload_needed: bool
    reasoning: str
    confidence: float
```

**Lambda**: `fitness-training-specialist`

---

### **5. Recovery Specialist Agent**

**Purpose**: Monitors recovery indicators and prevents overtraining

**Input Context**:
- Sleep logs
- Body composition logs (weight, measurements)
- Workout frequency and intensity
- Subjective recovery scores (if available)

**Responsibilities**:
- Detect overtraining symptoms
- Recommend rest days
- Suggest deload weeks
- Monitor weight loss/gain rate safety
- Identify recovery deficits

**Function Tools**:
- `calculate_training_volume(workout_logs)` → VolumeMetrics
- `detect_overtraining(volume, sleep, weight_trend)` → OvertrainingRisk
- `recommend_deload(training_history)` → DeloadRecommendation

**Structured Output**:
```python
class RecoveryRecommendation(BaseModel):
    overtraining_risk: str  # "low", "moderate", "high"
    recommended_rest_days: int
    deload_recommended: bool
    reasoning: str
    sleep_quality_score: Optional[float]
```

**Lambda**: `fitness-recovery-specialist`

---

### **6. Analytics Specialist Agent**

**Purpose**: Provides insights and predictions from historical data

**Input Context**:
- All historical logs (nutrition, workouts, body metrics)
- User goals and targets
- Time-series data

**Responsibilities**:
- Generate weekly/monthly summaries
- Predict goal achievement timeline
- Identify patterns and correlations
- Provide data-driven insights
- Track milestone progress

**Function Tools**:
- `calculate_trend(data_points)` → TrendMetrics
- `predict_goal_date(current_rate, target)` → PredictionResult
- `find_correlations(nutrition, training, body_metrics)` → List[Insight]

**Structured Output**:
```python
class AnalyticsInsight(BaseModel):
    weekly_summary: WeeklySummary
    goal_progress: GoalProgress
    predictions: List[Prediction]
    insights: List[str]  # e.g., "You plateau every 4 weeks on average"
    recommendations: List[str]
```

**Lambda**: `fitness-analytics-specialist`

---

### **7. Motivation Agent**

**Purpose**: Provides encouragement, celebrates milestones, builds engagement

**Input Context**:
- Recent achievements (PRs, streaks, weight milestones)
- User's current mood/state (from analytics)
- Historical engagement patterns

**Responsibilities**:
- Celebrate personal records
- Encourage during plateaus
- Recognize consistency streaks
- Provide motivational context
- Generate achievement badges

**No complex tools needed** - mostly templates and simple logic

**Structured Output**:
```python
class MotivationMessage(BaseModel):
    message: str
    achievements_unlocked: List[Achievement]
    encouragement_context: str
    tone: str  # "celebration", "encouragement", "challenge"
```

**Lambda**: `fitness-motivation-agent`

---

## MCP Server Implementations

### **1. USDA Food Database MCP Server**

**Tools Exposed**:
```python
@mcp_tool
async def search_foods(
    query: str,
    filters: Optional[FoodFilters] = None
) -> List[Food]:
    """Search USDA FoodData Central"""

@mcp_tool
async def get_nutrition_facts(
    food_id: str,
    portion_grams: float
) -> NutritionFacts:
    """Get detailed nutrition for specific food"""

@mcp_tool
async def find_high_protein_foods(
    max_calories: int,
    min_protein_grams: int
) -> List[Food]:
    """Find protein-rich foods within calorie budget"""

@mcp_tool
async def calculate_recipe_macros(
    ingredients: List[Ingredient]
) -> RecipeMacros:
    """Calculate total macros for a recipe"""
```

**Implementation**:
```python
# mcp/usda_food_mcp.py
from agents.mcp import MCPServerStdio

def create_usda_mcp_server():
    """Create USDA Food Database MCP server"""
    params = {
        "command": "python",
        "args": ["-m", "mcp_servers.usda_food_server"]
    }
    return MCPServerStdio(params=params)
```

**Server Code** (`mcp_servers/usda_food_server.py`):
```python
import os
import requests
from mcp.server import Server
from mcp.types import Tool, TextContent

app = Server("usda-food-database")

USDA_API_KEY = os.getenv("USDA_API_KEY")
USDA_API_URL = "https://api.nal.usda.gov/fdc/v1"

@app.list_tools()
async def list_tools():
    return [
        Tool(
            name="search_foods",
            description="Search USDA FoodData Central",
            inputSchema={
                "type": "object",
                "properties": {
                    "query": {"type": "string"},
                    "max_results": {"type": "number", "default": 10}
                },
                "required": ["query"]
            }
        )
    ]

@app.call_tool()
async def call_tool(name: str, arguments: dict):
    if name == "search_foods":
        query = arguments["query"]
        max_results = arguments.get("max_results", 10)

        response = requests.get(
            f"{USDA_API_URL}/foods/search",
            params={
                "api_key": USDA_API_KEY,
                "query": query,
                "pageSize": max_results
            }
        )

        foods = response.json().get("foods", [])

        results = []
        for food in foods:
            results.append({
                "fdc_id": food["fdcId"],
                "description": food["description"],
                "calories": next((n["value"] for n in food.get("foodNutrients", [])
                                if n["nutrientName"] == "Energy"), None),
                "protein": next((n["value"] for n in food.get("foodNutrients", [])
                              if n["nutrientName"] == "Protein"), None)
            })

        return [TextContent(type="text", text=str(results))]
```

---

### **2. Exercise Database MCP Server**

**Tools Exposed**:
```python
@mcp_tool
async def search_exercises(
    muscle_group: str,
    equipment: Optional[str] = None,
    difficulty: Optional[str] = None
) -> List[Exercise]:
    """Search exercise library by criteria"""

@mcp_tool
async def get_exercise_details(exercise_id: str) -> ExerciseDetails:
    """Get full details including form cues, muscles worked"""

@mcp_tool
async def find_exercise_alternatives(
    exercise_id: str,
    constraint: str  # e.g., "no barbell", "low impact"
) -> List[Exercise]:
    """Find alternative exercises with constraints"""

@mcp_tool
async def get_progression_path(exercise_id: str) -> ProgressionPath:
    """Get easier/harder variations"""
```

**Data Source**: ExerciseDB API (RapidAPI) or custom database

**Implementation Pattern**: Similar to USDA MCP above

---

## Function Tools Layer

### **Metrics Calculation Tools**

```python
from agents import function_tool, RunContextWrapper
from dataclasses import dataclass
from typing import Optional

@dataclass
class FitnessContext:
    """Context for fitness tools"""
    user_id: str
    db: Any  # DynamoDB client

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
    # BMR calculation
    if sex.lower() == "male":
        bmr = 10 * weight_kg + 6.25 * height_cm - 5 * age + 5
    else:
        bmr = 10 * weight_kg + 6.25 * height_cm - 5 * age - 161

    # Activity multipliers
    multipliers = {
        "sedentary": 1.2,
        "light": 1.375,
        "moderate": 1.55,
        "active": 1.725,
        "very_active": 1.9
    }

    tdee = bmr * multipliers.get(activity_level, 1.55)
    return round(tdee, 0)


@function_tool
async def calculate_1rm(
    wrapper: RunContextWrapper[FitnessContext],
    weight: float,
    reps: int
) -> float:
    """Calculate estimated 1 rep max using Epley formula"""
    if reps == 1:
        return weight
    return weight * (1 + reps / 30.0)


@function_tool
async def analyze_weight_trend(
    wrapper: RunContextWrapper[FitnessContext],
    days: int = 14
) -> dict:
    """
    Analyze weight trend from body logs.
    Returns plateau detection, average rate of change.
    """
    user_id = wrapper.context.user_id
    db = wrapper.context.db

    # Get recent body logs
    logs = db.body_logs.find_recent(user_id, days=days)

    if len(logs) < 3:
        return {"error": "Insufficient data", "days_of_data": len(logs)}

    weights = [float(log["weight"]) for log in logs]

    # Simple linear regression
    import numpy as np
    x = np.arange(len(weights))
    y = np.array(weights)
    slope, intercept = np.polyfit(x, y, 1)

    # Detect plateau (slope close to zero)
    is_plateau = abs(slope) < 0.05  # Less than 0.05 kg/day change

    # Calculate weekly change as percentage of bodyweight
    avg_weight = np.mean(weights)
    weekly_rate_kg = slope * 7
    weekly_rate_pct = (weekly_rate_kg / avg_weight) * 100 if avg_weight > 0 else 0

    return {
        "days_analyzed": days,
        "data_points": len(weights),
        "starting_weight": weights[0],
        "current_weight": weights[-1],
        "avg_weight": avg_weight,
        "total_change": weights[-1] - weights[0],
        "daily_rate": slope,
        "weekly_rate": weekly_rate_kg,
        "weekly_rate_pct": weekly_rate_pct,  # % of bodyweight
        "is_plateau": is_plateau,
        "trend": "stable" if is_plateau else ("increasing" if slope > 0 else "decreasing")
    }


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
    user_id = wrapper.context.user_id
    db = wrapper.context.db

    # Get recent body logs
    logs = db.body_logs.find_recent(user_id, days=days)

    if len(logs) < 2:
        return {
            "error": "Insufficient data",
            "data_points": len(logs),
            "recommendation": "Need at least 2 body composition measurements in 14 days"
        }

    import numpy as np

    # Method 1: Skinfold measurements (PREFERRED)
    logs_with_skinfolds = [log for log in logs if "skinfolds" in log and log["skinfolds"] is not None]

    if len(logs_with_skinfolds) >= 2:
        # Calculate sum of skinfolds for each measurement
        skinfold_sums = []
        for log in logs_with_skinfolds:
            # Sum all skinfold sites (tricep, abdomen, thigh, etc.)
            total = sum(log["skinfolds"].values())
            skinfold_sums.append(total)

        starting_sum = skinfold_sums[0]
        current_sum = skinfold_sums[-1]
        total_change = current_sum - starting_sum

        # Linear regression for trend
        x = np.arange(len(skinfold_sums))
        y = np.array(skinfold_sums)
        slope, _ = np.polyfit(x, y, 1)

        is_stable = abs(total_change) < 2  # Less than 2mm total change

        return {
            "method": "skinfolds",
            "confidence": "high",
            "days_analyzed": days,
            "data_points": len(skinfold_sums),
            "starting_skinfold_sum_mm": starting_sum,
            "current_skinfold_sum_mm": current_sum,
            "total_change_mm": total_change,
            "daily_rate_mm": slope,
            "is_stable": is_stable,
            "trend": "stable" if is_stable else ("increasing" if total_change > 0 else "decreasing"),
            "interpretation": "Fat mass decreasing" if total_change < -2 else ("Fat mass increasing" if total_change > 2 else "Fat mass stable")
        }

    # Method 2: Waist circumference (ALTERNATIVE)
    logs_with_waist = [log for log in logs if "waist_cm" in log and log["waist_cm"] is not None]

    if len(logs_with_waist) >= 2:
        waist_values = [float(log["waist_cm"]) for log in logs_with_waist]

        starting_waist = waist_values[0]
        current_waist = waist_values[-1]
        total_change = current_waist - starting_waist

        x = np.arange(len(waist_values))
        y = np.array(waist_values)
        slope, _ = np.polyfit(x, y, 1)

        is_stable = abs(total_change) < 1  # Less than 1cm change

        return {
            "method": "waist_circumference",
            "confidence": "medium",
            "days_analyzed": days,
            "data_points": len(waist_values),
            "starting_waist_cm": starting_waist,
            "current_waist_cm": current_waist,
            "total_change_cm": total_change,
            "is_stable": is_stable,
            "trend": "stable" if is_stable else ("increasing" if total_change > 0 else "decreasing"),
            "interpretation": "Fat mass decreasing" if total_change < -1 else ("Fat mass increasing" if total_change > 1 else "Fat mass stable")
        }

    # Method 3: Body fat % (FALLBACK)
    logs_with_bf = [log for log in logs if "body_fat_pct" in log and log["body_fat_pct"] is not None]

    if len(logs_with_bf) >= 2:
        body_fat_values = [float(log["body_fat_pct"]) for log in logs_with_bf]

        starting_bf = body_fat_values[0]
        current_bf = body_fat_values[-1]
        total_change = current_bf - starting_bf

        is_stable = abs(total_change) < 0.5  # Less than 0.5% change (within measurement error)

        return {
            "method": "body_fat_percentage",
            "confidence": "low",
            "warning": "Body fat % estimates are often inaccurate. Consider using skinfold calipers for better trend detection.",
            "days_analyzed": days,
            "data_points": len(body_fat_values),
            "starting_body_fat_pct": starting_bf,
            "current_body_fat_pct": current_bf,
            "total_change_pct": total_change,
            "is_stable": is_stable,
            "trend": "stable" if is_stable else ("increasing" if total_change > 0 else "decreasing"),
            "interpretation": "Trend uncertain due to measurement method" if is_stable else ("Fat mass likely decreasing" if total_change < -0.5 else "Fat mass likely increasing")
        }

    # Method 4: No direct measurements - recommend starting tracking
    return {
        "method": "none",
        "confidence": "none",
        "error": "No body composition data available",
        "recommendation": "Start tracking body composition using skinfold calipers (preferred) or waist circumference",
        "fallback": "Will infer from strength progression if available"
    }


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

    Args:
        current_avg_intake: Average calorie intake over analysis period
        weekly_weight_change_pct: Observed weekly weight change as % of bodyweight
                                  Positive = gaining, Negative = losing

    Returns:
        Estimated maintenance calories
    """
    # Mapping of weekly weight change % to deficit/surplus %
    # Based on Table 2 in Nutrition Agent Reasoning
    deficit_mapping = {
        0.3: 10,
        0.7: 20,
        1.1: 30,
        1.5: 50
    }

    # Find closest match or interpolate
    abs_change_pct = abs(weekly_weight_change_pct)

    if abs_change_pct < 0.1:
        # Essentially maintenance
        return current_avg_intake

    # Find estimated deficit/surplus percentage
    estimated_deficit_pct = None
    for threshold, deficit in sorted(deficit_mapping.items()):
        if abs_change_pct <= threshold:
            estimated_deficit_pct = deficit
            break

    if estimated_deficit_pct is None:
        estimated_deficit_pct = 50  # Max deficit/surplus

    # Calculate maintenance
    # If losing weight: current_intake = maintenance * (1 - deficit%)
    # So: maintenance = current_intake / (1 - deficit%)
    # If gaining weight: current_intake = maintenance * (1 + surplus%)
    # So: maintenance = current_intake / (1 + surplus%)

    if weekly_weight_change_pct < 0:  # Losing weight
        maintenance = current_avg_intake / (1 - estimated_deficit_pct / 100)
    else:  # Gaining weight
        maintenance = current_avg_intake / (1 + estimated_deficit_pct / 100)

    return round(maintenance, 0)


@function_tool
async def calculate_optimal_deficit(
    wrapper: RunContextWrapper[FitnessContext],
    body_fat_pct: float,
    sex: str
) -> float:
    """
    Calculate optimal calorie deficit percentage based on body fat level.

    Based on Table 1 in Nutrition Agent Reasoning section.

    Args:
        body_fat_pct: Current body fat percentage
        sex: "male" or "female"

    Returns:
        Optimal deficit percentage (5-50%)
    """
    if sex.lower() == "male":
        if body_fat_pct < 8:
            return 5  # Contest prep
        elif body_fat_pct < 15:
            return 10  # Athletic
        elif body_fat_pct < 21:
            return 20  # Average
        elif body_fat_pct < 26:
            return 30  # Overweight
        else:
            return 50  # Obese
    else:  # Female
        if body_fat_pct < 14:
            return 5  # Contest prep
        elif body_fat_pct < 24:
            return 10  # Athletic
        elif body_fat_pct < 33:
            return 20  # Average
        elif body_fat_pct < 39:
            return 30  # Overweight
        else:
            return 50  # Obese


@function_tool
async def calculate_optimal_surplus(
    wrapper: RunContextWrapper[FitnessContext],
    training_status: str
) -> dict:
    """
    Calculate optimal calorie surplus and target weight gain rate for bulking.

    Based on Table 3 in Nutrition Agent Reasoning section.

    Args:
        training_status: "novice", "intermediate", or "advanced"

    Returns:
        Dict with surplus_pct_min, surplus_pct_max, target_weekly_gain_pct_min, target_weekly_gain_pct_max
    """
    if training_status.lower() == "novice":
        return {
            "surplus_pct_min": 5,
            "surplus_pct_max": 15,
            "target_weekly_gain_pct_min": 0.5,
            "target_weekly_gain_pct_max": 1.0,
            "recommended_surplus_pct": 10  # Midpoint
        }
    elif training_status.lower() == "intermediate":
        return {
            "surplus_pct_min": 2,
            "surplus_pct_max": 7,
            "target_weekly_gain_pct_min": 0.2,
            "target_weekly_gain_pct_max": 0.5,
            "recommended_surplus_pct": 5  # Midpoint
        }
    else:  # Advanced
        return {
            "surplus_pct_min": 1,
            "surplus_pct_max": 3,
            "target_weekly_gain_pct_min": 0,
            "target_weekly_gain_pct_max": 0.3,
            "recommended_surplus_pct": 2  # Midpoint
        }
```

---

## Nutrition Agent Reasoning

The Nutrition Specialist uses evidence-based algorithms to optimize energy intake based on observed body composition changes. This section provides the detailed reasoning framework and decision trees.

### **Overview**

To optimize energy intake, the nutrition agent monitors three key metrics:
1. **Energy intake** (calories consumed)
2. **Body weight** (scale weight)
3. **Body fat percentage** (via measurements, photos, or estimates)

### **Cutting (Fat Loss)**

#### **Table 1: Optimal Deficit by Body Fat Percentage**

| Category | Fat % (Male) | Fat % (Female) | Optimal deficit (%) |
| --- | --- | --- | --- |
| Contest prep | < 8 | < 14 | 5 |
| Athletic | 8 -15 | 14 -24 | 10 |
| Average | 15 - 21 | 24 - 33 | 20 |
| Overweight | 21 - 26 | 33 - 39 | 30 |
| Obese | 26+ | 39+ | 50 |

#### **Table 2: Estimated Energy Deficit from Observed Weight Loss Rate**

| Observed weekly bodyweight loss rate (%) | Estimated energy deficit (%) |
| --- | --- |
| 0.3 | 10 |
| 0.7 | 20 |
| 1.1 | 30 |
| 1.5 | 50 |

#### **Decision Tree: Cutting Algorithm**

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

### **Bulking (Muscle Gain)**

#### **Table 3: Optimal Energy Surplus by Training Status**

| Training status | Initial energy surplus | Planned weekly weight gain rate (% bodyweight) |
| --- | --- | --- |
| Novice | 5-15% | 0.5-1% |
| Intermediate | 2-7% | 0.2-0.5% |
| Advanced | 1-3% | any fat-free |

#### **Decision Tree: Bulking Algorithm**

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
    1. Invoke Training Specialist to adjust program
    2. Decrease energy intake moderately
  - **Reasoning:** Gaining fat without strength gains = suboptimal training stimulus

### **Implementation Notes**

**Body Composition Tracking Methods:**

⭐ **Recommended Primary Method: Skinfold Caliper Measurements**

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

**Secondary Methods:**
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

**What the Algorithm Needs:**

1. **Fat mass TREND** (primary decision factor):
   - Skinfold sum: increasing/decreasing/stable
   - OR waist circumference: increasing/decreasing/stable
   - OR photo comparison: more/less/same body fat

2. **Estimated body fat % CATEGORY** (secondary, for deficit table):
   - Rough category is sufficient: "athletic" (8-15% M, 14-24% F), "average" (15-21% M, 24-33% F), etc.
   - Can be estimated from skinfolds, photos, or circumferences
   - Doesn't need to be precise (±5% error is acceptable)

**Minimum Data Requirements:**
- Weight logs: 5+ data points over 14 days
- **Body composition logs: 2+ measurements over 14 days**
  - **Preferred:** Skinfold measurements (3-7 sites, raw mm values)
  - **Alternative:** Waist circumference
  - **Fallback:** Body fat % estimate (acknowledge higher uncertainty)
- Nutrition logs: 10+ days of calorie tracking
- Training logs: 2+ weeks of workout data (for bulking strength assessment)

**Handling Missing/Unreliable Body Composition Data:**

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

**Function Tools Required:**
- `analyze_weight_trend(days=14)` → weekly rate, plateau detection
- `analyze_body_composition_trend(days=14)` → fat mass trend (skinfolds/waist/BF%), confidence level
- `estimate_maintenance_calories(current_intake, weight_loss_rate)` → TDEE estimate
- `calculate_optimal_deficit(body_fat_pct, sex)` → target deficit %
- `calculate_optimal_surplus(training_status)` → target surplus %

### **Key Advantages of This Approach**

1. **Personalized to individual body composition** - Leaner individuals get smaller deficits to preserve muscle, higher body fat allows more aggressive deficits
2. **Distinguishes fat loss from muscle gain** - Body recomposition is recognized and encouraged
3. **Prevents muscle loss** - Adjusts deficits if weight loss is too rapid for current body fat level
4. **Optimizes muscle gain rate** - Surplus scaled to training status to minimize fat gain
5. **Evidence-based thresholds** - Tables based on coaching best practices and research
6. **Coordinates with training** - Recognizes when poor strength gains indicate training issues
7. **Transparent reasoning** - Users understand why calories are adjusted
8. **Reliable trend detection** ⭐ - Prioritizes skinfold measurements over body fat % estimates for accurate fat mass tracking
9. **Flexible measurement methods** - Supports skinfolds, waist circumference, body fat %, or inference from strength gains
10. **Confidence-aware recommendations** - Adjusts recommendation aggressiveness based on data quality

### **Why Skinfold Measurements Are Critical**

**The Problem with Body Fat % Alone:**
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

**Skinfolds Solve This:**
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

**Practical Example:**
```
User tracking weight + skinfolds:

Week 1: 78kg, skinfolds 50mm
Week 2: 78kg, skinfolds 48mm  ← Nutrition agent: "Body recomp happening, maintain calories"
Week 3: 78kg, skinfolds 46mm  ← Agent: "Still recomping, great progress!"
Week 4: 78kg, skinfolds 46mm  ← Agent: "Skinfolds plateaued, time to reduce calories"

VS. tracking weight + BF% only:

Week 1: 78kg, 20% BF
Week 2: 78kg, 19.7% BF  ← Is this real or noise?
Week 3: 78kg, 20.1% BF  ← Now increased? Hydration? Error?
Week 4: 78kg, 19.5% BF  ← Unclear if progressing or not

Agent: "Uncertain data, making conservative recommendation..."
```

---

## Integration with Existing Fitness App

### **Current Architecture**
Your app currently has:
- **Frontend**: Next.js with React
- **Backend**: FastAPI Lambda (`/backend`)
- **Database**: DynamoDB tables (user_profiles, nutrition_logs, workout_logs, body_logs, etc.)
- **API**: REST endpoints for CRUD operations

### **Integration Points**

#### **1. EventBridge Scheduled Rule**
```python
# terraform/eventbridge.tf

resource "aws_cloudwatch_event_rule" "weekly_analysis" {
  name                = "fitness-weekly-analysis"
  description         = "Trigger weekly progress analysis for all active users"
  schedule_expression = "cron(0 6 ? * MON *)"  # Every Monday at 6 AM UTC
}

resource "aws_cloudwatch_event_target" "weekly_analysis" {
  rule      = aws_cloudwatch_event_rule.weekly_analysis.name
  target_id = "WeeklyAnalysisLambda"
  arn       = aws_lambda_function.weekly_analyzer.arn
}

resource "aws_lambda_permission" "allow_eventbridge" {
  statement_id  = "AllowExecutionFromEventBridge"
  action        = "lambda:InvokeFunction"
  function_name = aws_lambda_function.weekly_analyzer.function_name
  principal     = "events.amazonaws.com"
  source_arn    = aws_cloudwatch_event_rule.weekly_analysis.arn
}
```

#### **2. New API Endpoints**

**Primary: Get Weekly Analysis Results**
```python
# backend/server.py

@app.get("/api/weekly-analysis/{user_id}/latest")
async def get_latest_analysis(user_id: str):
    """
    Get the most recent weekly analysis for a user
    """
    analysis = db.weekly_analyses.find_latest(user_id)
    return {
        "week_starting": analysis["week_starting"],
        "data_summary": analysis["data_summary"],
        "issues_detected": analysis["issues_detected"],
        "plan_updated": analysis["plan_updated"],
        "updates": analysis.get("updates"),
        "analyzed_at": analysis["analyzed_at"]
    }

@app.get("/api/plans/{user_id}/active")
async def get_active_plan(user_id: str, plan_type: str):
    """
    Get user's current active plan (nutrition or training)
    """
    plan = db.active_plans.find_active(user_id, plan_type)
    return plan
```

**Secondary: On-Demand Chat**
```python
@app.post("/api/coach/ask")
async def ask_coach(request: CoachRequest):
    """
    On-demand coaching questions (secondary mode).
    Invokes the Coach Orchestrator Lambda.
    """
    # Create coaching job in DynamoDB
    job_id = str(uuid.uuid4())

    db.coach_jobs.create({
        "id": job_id,
        "user_id": request.user_id,
        "question": request.question,
        "status": "pending",
        "created_at": datetime.utcnow().isoformat()
    })

    # Invoke Coach Orchestrator Lambda
    lambda_client.invoke(
        FunctionName="fitness-coach-orchestrator",
        InvocationType="RequestResponse",  # Synchronous
        Payload=json.dumps({
            "job_id": job_id,
            "user_id": request.user_id,
            "question": request.question
        })
    )

    # Return job status
    job = db.coach_jobs.find_by_id(job_id)
    return {
        "job_id": job_id,
        "response": job.get("response"),
        "recommendations": job.get("recommendations")
    }
```

#### **3. DynamoDB Schema Additions**

**New Table: `weekly_analyses`** ⭐ (Primary)
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
        # OR
        "waist_starting_cm": 85,
        "waist_current_cm": 83,
        "waist_change_cm": -2,
        # OR
        "avg_body_fat_pct": 20.5,
        "body_fat_change_pct": -0.3,

        "body_composition_trend": "decreasing",  # "increasing", "stable", "decreasing"
        "body_composition_interpretation": "Fat mass decreasing",

        # Nutrition metrics
        "avg_calories": 2180,

        # Training metrics
        "total_training_volume": 15000  # kg
    },

    # Issues detected
    "issues_detected": [
        {
            "type": "weight_plateau",
            "severity": "medium",
            "description": "No weight change in 14 days (avg 78.5kg)",
            "recommended_action": "reduce_calories",
            "metadata": {}
        },
        {
            "type": "strength_plateau",
            "severity": "low",
            "description": "Squat: No progression in 3 weeks",
            "recommended_action": "modify_training_program",
            "metadata": {"exercise": "squat"}
        }
    ],

    # Plan updates (if any)
    "plan_updated": true,
    "updates": {
        "nutrition": {
            "old_calories": 2200,
            "new_calories": 2000,
            "reasoning": "Weight plateau detected..."
        },
        "training": {
            "exercise": "squat",
            "old_program": "5x5 @ 100kg",
            "new_program": "3x8 @ 90kg",
            "reasoning": "Breaking plateau with volume phase..."
        }
    },

    # Notification
    "notification_sent": true,
    "notification_sent_at": "2025-10-27T06:15:00Z",

    # Metadata
    "analyzed_at": "2025-10-27T06:00:00Z",
    "analysis_duration_ms": 3500
}
```

**New Table: `active_plans`** ⭐ (Primary)
```python
{
    "user_id": "string",  # Partition key
    "plan_type": "nutrition",  # Sort key: "nutrition" or "training"
    "version": 3,
    "created_at": "2025-10-27T06:00:00Z",
    "active": true,

    # Nutrition plan fields (if plan_type == "nutrition")
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

    # Training plan fields (if plan_type == "training")
    "program_name": "Push Pull Legs",
    "frequency": "4x/week",
    "exercises": [
        {
            "name": "Squat",
            "sets": 3,
            "reps": 8,
            "weight_kg": 90,
            "rest_seconds": 180
        }
    ],

    # Metadata
    "reason_for_update": "Weight plateau detected in weekly analysis",
    "previous_version": 2,
    "updated_by": "weekly_analyzer"  # or "nutrition_specialist"
}
```

**Updated Table: `body_logs`** ⭐ (Enhanced with skinfold support)
```python
{
    "user_id": "string",  # Partition key
    "timestamp": "2025-10-27T08:00:00Z",  # Sort key
    "log_date": "2025-10-27",

    # Basic metrics (existing)
    "weight": 78.5,  # kg
    "height": 175,   # cm (optional, usually static)

    # Body composition tracking (NEW - multiple methods supported)

    # Method 1: Skinfold measurements (PREFERRED) ⭐
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

**Existing Table: `coach_jobs`** (Secondary - On-Demand Chat)
```python
{
    "id": "uuid",
    "user_id": "string",
    "question": "string",
    "status": "pending|processing|completed|failed",
    "response": "string",  # Final coaching response
    "recommendations": {
        "nutrition": {...},
        "training": {...},
        "recovery": {...}
    },
    "specialist_results": {
        "nutrition_specialist": {...},
        "training_specialist": {...},
        ...
    },
    "created_at": "ISO8601",
    "completed_at": "ISO8601"
}
```

#### **4. Lambda Deployment Structure**

```
terraform/
  lambda_ai_agents.tf  # New file for AI agent Lambdas
  eventbridge.tf       # EventBridge cron rules

ai_agents/  # Renamed from alex_backend
  weekly_analyzer/     # ⭐ NEW: Primary proactive agent
    agent.py
    lambda_handler.py
    detection_rules.py
    plan_adjuster.py
  orchestrator/        # Secondary: on-demand chat
    agent.py
    lambda_handler.py
    prompts.py
  nutrition_specialist/
    agent.py
    lambda_handler.py
    tools.py
  training_specialist/
    agent.py
    lambda_handler.py
    tools.py
  recovery_specialist/
    agent.py
    lambda_handler.py
  analytics_specialist/
    agent.py
    lambda_handler.py
  motivation_agent/
    agent.py
    lambda_handler.py
  shared/
    context.py
    models.py          # Pydantic models for structured outputs
    db_client.py
    trend_analysis.py  # Shared trend calculation functions (deterministic)
  mcp_servers/
    usda_food_server.py
    exercise_db_server.py
```

#### **5. Frontend Integration**

**Primary UI: Weekly Analysis Dashboard**
```tsx
// pages/progress.tsx or components/WeeklyAnalysis.tsx

export default function WeeklyAnalysisDashboard() {
  const [analysis, setAnalysis] = useState(null)
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    fetchLatestAnalysis()
  }, [])

  async function fetchLatestAnalysis() {
    const res = await fetch(`/api/weekly-analysis/${currentUser.id}/latest`)
    const data = await res.json()
    setAnalysis(data)
    setLoading(false)
  }

  if (loading) return <Spinner />

  return (
    <div className="weekly-analysis-dashboard">
      <h2>Weekly Check-In</h2>
      <p className="subtitle">Last analyzed: {formatDate(analysis.analyzed_at)}</p>

      {/* Data Summary */}
      <Card title="Your Progress This Week">
        <div className="metrics-grid">
          <Metric label="Avg Weight" value={`${analysis.data_summary.avg_weight_kg}kg`} />
          <Metric label="Weight Change" value={`${analysis.data_summary.weight_change_kg}kg`} trend />
          <Metric label="Workouts" value={analysis.data_summary.workout_logs_count} />
          <Metric label="Avg Calories" value={analysis.data_summary.avg_calories} />
        </div>
      </Card>

      {/* Issues Detected */}
      {analysis.issues_detected.length > 0 && (
        <Card title="What I Noticed">
          <IssuesList issues={analysis.issues_detected} />
        </Card>
      )}

      {/* Plan Updates */}
      {analysis.plan_updated && (
        <Card title="Plan Adjustments" highlight>
          <h3>I've updated your plan based on your progress:</h3>

          {analysis.updates.nutrition && (
            <UpdateCard
              type="nutrition"
              icon="🍽️"
              title="Nutrition Adjustment"
              oldValue={`${analysis.updates.nutrition.old_calories} cal/day`}
              newValue={`${analysis.updates.nutrition.new_calories} cal/day`}
              reasoning={analysis.updates.nutrition.reasoning}
            />
          )}

          {analysis.updates.training && (
            <UpdateCard
              type="training"
              icon="💪"
              title="Training Modification"
              details={analysis.updates.training}
            />
          )}

          <button onClick={() => viewUpdatedPlan()}>
            View Updated Plan
          </button>
        </Card>
      )}

      {!analysis.plan_updated && (
        <Card title="Keep Going!" type="success">
          <p>Your current plan is working well. No changes needed this week.</p>
          <p>Keep logging consistently and I'll check in again next Monday.</p>
        </Card>
      )}
    </div>
  )
}
```

**Secondary UI: On-Demand Chat** (Optional)
```tsx
// components/CoachChat.tsx

export default function CoachChat() {
  const [question, setQuestion] = useState("")
  const [response, setResponse] = useState(null)
  const [loading, setLoading] = useState(false)

  async function askCoach() {
    setLoading(true)
    const res = await fetch("/api/coach/ask", {
      method: "POST",
      headers: {"Content-Type": "application/json"},
      body: JSON.stringify({
        user_id: currentUser.id,
        question: question
      })
    })

    const data = await res.json()
    setResponse(data)
    setLoading(false)
  }

  return (
    <div className="coach-chat">
      <h3>Ask Your Coach</h3>
      <p className="hint">For quick questions about form, substitutions, etc.</p>

      <textarea
        value={question}
        onChange={(e) => setQuestion(e.target.value)}
        placeholder="e.g., Can I substitute chicken with tofu?"
      />
      <button onClick={askCoach} disabled={loading}>
        {loading ? "Thinking..." : "Ask"}
      </button>

      {response && (
        <div className="coach-response">
          <p>{response.response}</p>
        </div>
      )}
    </div>
  )
}
```

---

## Example End-to-End Flow

### **Scenario**: Weekly automated analysis detects plateau and adjusts plan

#### **Step 1: EventBridge triggers weekly analysis**
```python
# Every Monday at 6 AM UTC
# EventBridge invokes: fitness-weekly-analyzer Lambda

# Lambda receives event:
{
  "source": "aws.events",
  "detail-type": "Scheduled Event",
  "time": "2025-10-27T06:00:00Z"
}
```

#### **Step 2: Weekly Analyzer fetches all active users**
```python
# ai_agents/weekly_analyzer/lambda_handler.py

def lambda_handler(event, context):
    # Get all users with active plans
    active_users = db.user_profiles.find_all_active()

    # Process each user (can be parallelized)
    for user in active_users:
        analyze_user_progress(user['user_id'])
```

#### **Step 3: Gather context (user_123)**
```python
# ai_agents/weekly_analyzer/agent.py

async def analyze_user_progress(user_id: str):
    # 1. Pull 14-28 days of data
    user_profile = db.user_profiles.find_one({"user_id": user_id})
    weight_logs = db.body_logs.find_recent(user_id, days=14)
    body_comp_logs = db.body_logs.find_recent(user_id, days=14)
    workout_logs = db.workout_logs.find_recent(user_id, days=28)  # 4 weeks for training analysis
    nutrition_logs = db.nutrition_logs.find_recent(user_id, days=14)
    sleep_logs = db.sleep_logs.find_recent(user_id, days=14)

    # Data for user_123:
    # Weight: [78.5, 78.6, 78.4, 78.5, 78.6, 78.4] kg (6 logs)
    # Skinfolds: [50mm, 49mm, 48mm] (3 logs)
    # Workouts: 4 sessions logged
    # Nutrition: averaging 2180 cal/day

    # 2. Calculate trends (deterministic - no AI)
    context = {
        "user_profile": {
            "goal": user_profile.goal,  # "lose_weight"
            "sex": user_profile.sex,  # "male"
            "body_fat_pct": 20.5,
            "training_status": "intermediate"
        },
        "weight_trend": analyze_weight_trend(weight_logs),
        # Returns: {
        #   "starting_weight": 78.5,
        #   "current_weight": 78.4,
        #   "avg_weight": 78.5,
        #   "weekly_rate_kg": -0.07,  # Nearly flat
        #   "weekly_rate_pct": 0.09  # 0.09% per week
        # }

        "body_comp_trend": analyze_body_composition_trend(body_comp_logs),
        # Returns: {
        #   "method": "skinfolds",
        #   "confidence": "high",
        #   "starting_sum": 50,
        #   "current_sum": 48,
        #   "change_mm": -2,  # Fat decreasing!
        #   "trend": "decreasing"
        # }

        "nutrition_summary": {
            "avg_calories": 2180,
            "avg_protein_g": 160,
            "days_logged": 12,
            "compliance_pct": 86  # 12/14 days
        },

        "workout_summary": analyze_strength_trends(workout_logs),
        # Returns: {
        #   "sessions": 4,
        #   "strength_trends": {
        #     "squat": {"current_1rm": 100, "4weeks_ago": 100, "change_pct": 0},  # Plateau
        #     "bench": {"current_1rm": 80, "4weeks_ago": 77, "change_pct": 3.9}   # Progressing
        #   }
        # }

        "recovery_metrics": calculate_recovery_metrics(sleep_logs, workout_logs)
        # Returns: {
        #   "avg_sleep_hours": 7.5,
        #   "sleep_quality": "good",
        #   "consecutive_workout_days": 3,
        #   "needs_deload": False
        # }
    }

    # 3. NO DECISION MAKING - Always invoke specialists with full context
    await coordinate_specialists(user_id, context)
```

#### **Step 4: Coordinate specialists (always invoke)**
```python
# ai_agents/weekly_analyzer/specialist_coordinator.py

async def coordinate_specialists(user_id: str, context: dict):
    """
    Always invoke all relevant specialists with full context.
    Specialists make the decisions, orchestrator just coordinates.
    """

    # Always invoke Nutrition Specialist (for users with weight goals)
    nutrition_rec = await invoke_nutrition_specialist(
        user_id=user_id,
        context=context
    )
    # Nutrition Specialist applies Nutrition Agent Reasoning algorithm:
    # - Sees weight nearly flat (0.09% weekly) but skinfolds decreasing (-2mm)
    # - Recognizes: Body recomposition happening!
    # - Decision: MAINTAIN current calories
    #
    # Returns: {
    #   "current_calorie_average": 2180,
    #   "current_body_fat_pct": 20.5,
    #   "observed_weekly_weight_change_pct": 0.09,
    #   "skinfold_change_mm": -2,
    #   "recommended_calories": 2180,  # No change (recomp happening)
    #   "recommended_deficit_or_surplus_pct": 0,
    #   "optimal_deficit_or_surplus_pct": 20,  # Would be optimal if true plateau
    #   "recommended_macros": {"protein_g": 160, "carbs_g": 200, "fat_g": 67},
    #   "reasoning": "Weight plateau detected, but skinfolds decreased by 2mm. This indicates successful body recomposition (fat loss + muscle gain). No calorie adjustment needed - maintain current intake.",
    #   "body_composition_status": "recomp",
    #   "adjustment_category": "none"  # ← Specialist says no change needed
    # }

    # Always invoke Training Specialist
    training_rec = await invoke_training_specialist(
        user_id=user_id,
        context=context
    )
    # Training Specialist:
    # - Sees squat plateau (no progression in 4 weeks)
    # - Bench press progressing well
    # - Decision: Modify squat program only
    #
    # Returns: {
    #   "has_recommendations": True,
    #   "changes": [{
    #     "exercise": "squat",
    #     "current_program": "5x5 @ 100kg",
    #     "new_program": "3x8 @ 90kg (volume phase)",
    #     "reasoning": "Breaking plateau with higher rep range and deload"
    #   }]
    # }

    # Always invoke Recovery Specialist
    recovery_rec = await invoke_recovery_specialist(
        user_id=user_id,
        context=context
    )
    # Returns: {"sleep_adequate": True, "needs_deload": False}

    # Always invoke Analytics Specialist
    analytics_report = await invoke_analytics_specialist(
        user_id=user_id,
        context=context
    )
    # Returns: Progress summary, charts, insights

    # Aggregate updates (only apply changes where adjustment_category != "none")
    updates = {}
    if nutrition_rec.adjustment_category != "none":
        updates["nutrition"] = nutrition_rec  # Not applied in this case
    if training_rec.has_recommendations:
        updates["training"] = training_rec  # Applied (squat program change)
    if recovery_rec.needs_deload:
        updates["recovery"] = recovery_rec

    # Resolve conflicts if multiple specialists recommend changes
    # Example: If both nutrition (increase calories) AND training (increase volume)
    # recommend changes, prioritize nutrition and defer training for next week
    updates = resolve_conflicts(updates, context)

    # Store weekly analysis results
    await store_analysis_results(user_id, context, nutrition_rec, training_rec, recovery_rec, updates)

    # Send notification to user
    await send_notification(user_id, updates, analytics_report)

    return updates
```

**Example of Nutrition Specialist Reasoning (Too Fast Weight Loss):**
```python
# Different user scenario - Female losing weight too fast
context_female = {
    "user_profile": {"goal": "lose_weight", "sex": "female", "body_fat_pct": 20, "training_status": "intermediate"},
    "weight_trend": {"weekly_rate_pct": 0.77},  # 0.77% per week
    "nutrition_summary": {"avg_calories": 1600}
}

nutrition_rec = await invoke_nutrition_specialist(user_id, context_female)
# Nutrition Specialist reasoning:
#   1. Weekly loss 0.77% → estimated deficit ~20% (from Table 2 in Nutrition Agent Reasoning)
#   2. Body fat 20% (female, athletic) → optimal deficit 10% (from Table 1)
#   3. Estimated deficit (20%) > Optimal deficit (10%) → losing too fast (risk muscle loss)
#   4. Estimated maintenance: 1600 / (1 - 0.20) = 2000 kcal
#   5. New target: 2000 * 0.9 = 1800 kcal (10% deficit)
#
# Returns: {
#   "adjustment_category": "increase",  # ← Specialist says increase calories
#   "recommended_calories": 1800,  # Up from 1600
#   "reasoning": "Weight loss too fast (0.77%/week). Increase calories to prevent muscle loss."
# }
```

#### **Step 5: Update plans in DynamoDB**
```python
# Update active_plans table (only for specialists that recommended changes)

# Nutrition plan - NO UPDATE
# Nutrition Specialist returned adjustment_category = "none"
# because body recomposition is happening (fat loss + muscle gain)
# Current plan stays active (2200 cal/day)

# Training plan - UPDATE APPLIED
db.active_plans.create({
    "user_id": "user_123",
    "plan_type": "training",
    "version": 4,
    "exercises": [
        {
            "name": "squat",
            "sets": 3,
            "reps": 8,
            "weight_kg": 90,  # Deloaded from 100kg
            "rest_seconds": 180
        }
    ],
    "reason_for_update": "Training Specialist: Squat plateau (no progress 3 weeks) - switching to volume phase",
    "updated_by": "weekly_analyzer",
    "specialist": "training_specialist",
    "created_at": "2025-10-27T06:05:00Z",
    "active": True
})
```

#### **Step 6: Store weekly analysis results**
```python
# weekly_analyses table

db.weekly_analyses.create({
    "user_id": "user_123",
    "week_starting": "2025-10-20",
    "status": "completed",

    "data_summary": {
        "weight_logs_count": 6,
        "workout_logs_count": 4,
        "avg_weight_kg": 78.5,
        "weight_change_kg": -0.07,  # Minimal change (0.09%/week)
        "weight_change_pct": 0.09,
        "skinfold_sum_mm": 72,  # Down from 74mm (week ago)
        "skinfold_change_mm": -2,
        "avg_calories": 2180
    },

    # Orchestrator always invokes specialists, stores their recommendations
    "specialist_recommendations": {
        "nutrition": {
            "adjustment_category": "none",  # ← Specialist says no change
            "current_calories": 2200,
            "recommended_calories": 2200,  # No change
            "reasoning": "Body recomposition detected: Weight nearly flat (0.09%/week) but skinfold sum decreased 2mm. Fat loss + muscle gain happening. MAINTAIN current calories."
        },
        "training": {
            "has_recommendations": True,
            "exercise_updates": [
                {
                    "exercise": "squat",
                    "old_program": "5x5 @ 100kg",
                    "new_program": "3x8 @ 90kg",
                    "reasoning": "No progression in 3 weeks. Switching to volume phase to break plateau."
                }
            ]
        },
        "recovery": {
            "needs_deload": False,
            "reasoning": "Recovery metrics normal. No deload needed."
        },
        "analytics": {
            "key_insights": [
                "Body recomposition in progress (rare and desirable!)",
                "Training intensity may have caused squat plateau"
            ]
        }
    },

    "plan_updated": True,  # Training plan updated (nutrition maintained)
    "updates_applied": ["training"],  # Only training specialist recommendations applied

    "analyzed_at": "2025-10-27T06:00:00Z",
    "notification_sent": True
})
```

#### **Step 7: User sees notification on Monday morning**
```
📱 Notification:

"Weekly Check-In Complete"

Your AI coach analyzed your progress from Oct 20-27:

✅ Logged 6 weigh-ins, 4 workouts
🎯 Body recomposition detected! (fat ↓, muscle ↑)
⚙️ Squat program adjusted (volume phase)

Updates to your plan:
• Nutrition: 2200 cal/day (no change - recomp working!)
• Training: Modified squat program (3x8 @ 90kg)

Tap to see details →
```

#### **Step 8: User views dashboard**

User opens app and sees updated Weekly Analysis Dashboard with:

**Week Oct 20-27 Summary:**
- ✅ 6 weigh-ins, 4 workouts logged
- Weight: 78.5 kg (minimal change: -0.07 kg)
- Skinfold sum: 72 mm (improved: -2 mm) 📉
- Average calories: 2180 cal/day

**Specialist Insights:**

🍎 **Nutrition Specialist:**
> "Body recomposition detected! Weight nearly flat (0.09%/week) but skinfold sum decreased 2mm. This means you're losing fat AND gaining muscle - exactly what we want. MAINTAIN current calories (2200 cal/day)."

🏋️ **Training Specialist:**
> "Squat hasn't progressed in 3 weeks at 5x5 @ 100kg. Switching to volume phase (3x8 @ 90kg) to stimulate new adaptations and break plateau."

💤 **Recovery Specialist:**
> "All recovery metrics normal. No deload needed. Continue current training frequency."

📊 **Analytics:**
> "Body recomposition in progress (rare and desirable outcome!). Training adjustments will complement your current nutrition strategy."

**Action Items:**
- ✅ Nutrition plan: No changes (2200 cal/day)
- ⚙️ Training plan: Updated squat program (tap to view)
- No action needed - just follow the updated plan!

---

## Development & Testing Strategy

### **Key Principle: Build for Manual Triggering First** ⭐

The Weekly Analyzer Lambda is designed to work independently of how it's triggered. This allows you to:
- **Develop and test anytime** (not just Monday 6 AM)
- **No code changes** needed to switch from manual to scheduled
- **Keep manual triggers available** in production for debugging

### **Lambda Design Pattern**

```python
# ai_agents/weekly_analyzer/lambda_handler.py

def lambda_handler(event, context):
    """
    Works the same regardless of trigger source:
    - Manual trigger via AWS CLI
    - Manual trigger via API endpoint
    - Scheduled trigger via EventBridge
    """
    # Optional: filter to specific users for testing
    test_user_ids = event.get("user_ids", None)

    if test_user_ids:
        print(f"Test mode: analyzing users {test_user_ids}")
        users = [{"user_id": uid} for uid in test_user_ids]
    else:
        print("Production mode: analyzing all active users")
        users = db.user_profiles.find_all_active()

    results = []
    for user in users:
        result = analyze_user_progress(user["user_id"])
        results.append(result)

    return {
        "statusCode": 200,
        "users_processed": len(results),
        "results": results
    }
```

### **Development Phase: Manual Triggering**

#### **Option 1: AWS CLI (Recommended)** ⭐

```bash
# Test with specific user
aws lambda invoke \
  --function-name fitness-weekly-analyzer \
  --payload '{"user_ids": ["user_123"]}' \
  --cli-binary-format raw-in-base64-out \
  response.json

# Test with all users (production simulation)
aws lambda invoke \
  --function-name fitness-weekly-analyzer \
  --payload '{}' \
  --cli-binary-format raw-in-base64-out \
  response.json

# View results
cat response.json | jq '.'
```

**Helper Script:**
```bash
#!/bin/bash
# scripts/trigger-weekly-analysis.sh

USER_ID=${1:-""}

if [ -z "$USER_ID" ]; then
  echo "Running weekly analysis for ALL users..."
  PAYLOAD='{}'
else
  echo "Running weekly analysis for user: $USER_ID"
  PAYLOAD="{\"user_ids\": [\"$USER_ID\"]}"
fi

aws lambda invoke \
  --function-name fitness-weekly-analyzer \
  --payload "$PAYLOAD" \
  --cli-binary-format raw-in-base64-out \
  response.json

cat response.json | jq '.'
```

Usage:
```bash
./scripts/trigger-weekly-analysis.sh user_123  # Test specific user
./scripts/trigger-weekly-analysis.sh           # Test all users
```

#### **Option 2: API Endpoint (Optional)**

```python
# backend/server.py

@app.post("/api/admin/trigger-weekly-analysis")
async def trigger_weekly_analysis(
    user_id: Optional[str] = None,
    api_key: str = Header(None)
):
    """Manual trigger for development/testing"""
    if api_key != os.getenv("ADMIN_API_KEY"):
        raise HTTPException(status_code=403)

    payload = {"user_ids": [user_id]} if user_id else {}

    response = lambda_client.invoke(
        FunctionName="fitness-weekly-analyzer",
        InvocationType="RequestResponse",
        Payload=json.dumps(payload)
    )

    return json.loads(response['Payload'].read())
```

Usage:
```bash
curl -X POST "https://api.example.com/api/admin/trigger-weekly-analysis?user_id=user_123" \
  -H "api-key: dev-secret"
```

#### **Option 3: Local Python Script**

```python
# scripts/run_weekly_analysis_local.py

from ai_agents.weekly_analyzer.lambda_handler import lambda_handler

event = {"user_ids": ["user_123"]}  # Or {} for all users
context = None

result = lambda_handler(event, context)
print(f"Users processed: {result['users_processed']}")
```

Run:
```bash
python scripts/run_weekly_analysis_local.py
```

### **Production Phase: Add Scheduling**

When ready for production, add EventBridge - **no Lambda code changes needed**:

```hcl
# terraform/eventbridge.tf

resource "aws_cloudwatch_event_rule" "weekly_analysis" {
  name                = "fitness-weekly-analysis"
  description         = "Trigger weekly analysis every Monday 6 AM UTC"
  schedule_expression = "cron(0 6 ? * MON *)"
}

resource "aws_cloudwatch_event_target" "weekly_analysis" {
  rule      = aws_cloudwatch_event_rule.weekly_analysis.name
  target_id = "WeeklyAnalysisLambda"
  arn       = aws_lambda_function.weekly_analyzer.arn
  input     = "{}"  # Process all users
}

resource "aws_lambda_permission" "allow_eventbridge" {
  statement_id  = "AllowExecutionFromEventBridge"
  action        = "lambda:InvokeFunction"
  function_name = aws_lambda_function.weekly_analyzer.function_name
  principal     = "events.amazonaws.com"
  source_arn    = aws_cloudwatch_event_rule.weekly_analysis.arn
}
```

### **Gradual Enablement with Terraform**

Use a feature flag to enable/disable scheduling:

```hcl
# terraform/variables.tf
variable "enable_weekly_schedule" {
  description = "Enable EventBridge schedule for weekly analysis"
  type        = bool
  default     = false  # Start disabled
}

# terraform/eventbridge.tf
resource "aws_cloudwatch_event_rule" "weekly_analysis" {
  count               = var.enable_weekly_schedule ? 1 : 0
  name                = "fitness-weekly-analysis"
  schedule_expression = "cron(0 6 ? * MON *)"
  # ... rest of config
}
```

**Development:**
```bash
terraform apply -var="enable_weekly_schedule=false"
# Lambda deployed, manual triggers only
```

**Production:**
```bash
terraform apply -var="enable_weekly_schedule=true"
# Same Lambda, now also scheduled
# Manual triggers still work!
```

### **Complete Development Workflow**

```
┌─────────────────────────────────────────────┐
│ Phase 1: Build Lambda                       │
│ - No EventBridge dependency                 │
│ - Accepts optional user_ids parameter       │
│ - Deploy to AWS                             │
└────────────────┬────────────────────────────┘
                 │
                 ▼
┌─────────────────────────────────────────────┐
│ Phase 2: Test Manually                      │
│ - AWS CLI: anytime, any user                │
│ - API endpoint: from Postman/frontend       │
│ - Local script: quick iteration             │
│                                             │
│ Iterate until weekly analyzer works         │
└────────────────┬────────────────────────────┘
                 │
                 ▼
┌─────────────────────────────────────────────┐
│ Phase 3: Add EventBridge (Infrastructure)   │
│ - terraform apply with flag enabled         │
│ - Zero Lambda code changes                  │
│ - Runs Monday 6 AM automatically            │
│ - Manual triggers remain available          │
└─────────────────────────────────────────────┘
```

### **Testing Recommendations**

**During Development:**
- Use AWS CLI with specific user IDs for fast iteration
- Create test users with known plateau scenarios
- Run analysis multiple times to refine detection logic

**Before Production:**
- Test with all users via `aws lambda invoke` with empty payload
- Monitor CloudWatch logs for any errors
- Verify `weekly_analyses` table is populated correctly
- Check that notifications are sent

**In Production:**
- Keep manual trigger API endpoint for debugging specific users
- Monitor EventBridge execution metrics
- Set up CloudWatch alarms for Lambda failures

---

## Implementation Roadmap

### **Phase 1: Foundation & Weekly Analyzer (Week 1-2)** ⭐
- [ ] Set up `ai_agents/` directory structure
- [ ] Create shared models and context wrappers
- [ ] Create function tools: `analyze_weight_trend`, `analyze_body_composition_trend`, `calculate_tdee`, `calculate_macros`
- [ ] Add DynamoDB tables: `weekly_analyses`, `active_plans`
- [ ] Update `body_logs` table schema to support:
  - [ ] Skinfold measurements (preferred method)
  - [ ] Circumference measurements (waist, hips, neck, etc.)
  - [ ] Body fat % estimates with method tracking
  - [ ] Progress photos (S3 URLs)
- [ ] Implement Weekly Progress Analyzer agent (core detection logic)
- [ ] Add EventBridge cron rule for Monday 6 AM
- [ ] Test basic weekly analysis flow end-to-end

### **Phase 2: Nutrition & Training Specialists (Week 3)**
- [ ] Implement Nutrition Specialist agent with evidence-based deficit/surplus algorithm
- [ ] Create nutrition function tools:
  - [ ] `estimate_maintenance_calories(current_intake, weight_loss_rate)`
  - [ ] `calculate_optimal_deficit(body_fat_pct, sex)`
  - [ ] `calculate_optimal_surplus(training_status)`
- [ ] Implement Training Specialist agent
- [ ] Create training function tools: `calculate_1rm`, `detect_strength_plateau`, `analyze_volume_trend`
- [ ] Integrate specialists with Weekly Analyzer
- [ ] Test plan adjustment workflow with body composition scenarios

### **Phase 3: Frontend & Notifications (Week 4)**
- [ ] Build Weekly Analysis Dashboard (primary UI)
- [ ] Create API endpoints: `/api/weekly-analysis/{user_id}/latest`, `/api/plans/{user_id}/active`
- [ ] Add push notifications for weekly check-ins
- [ ] Display plan updates with reasoning
- [ ] Add body composition logging UI:
  - [ ] Skinfold measurement input form (3-7 sites with diagrams)
  - [ ] Waist/circumference measurement input
  - [ ] Progress photo upload
  - [ ] Body composition trend charts (skinfold sum over time)
  - [ ] Onboarding tutorial for caliper usage
- [ ] Test full user experience flow

### **Phase 4: MCP Servers (Week 5)** (Optional for MVP)
- [ ] Build USDA Food Database MCP server
- [ ] Integrate MCP with Nutrition Specialist for meal planning
- [ ] Test meal plan generation with real food data
- [ ] (Optional) Build Exercise Database MCP

### **Phase 5: Additional Specialists (Week 6)**
- [ ] Implement Recovery Specialist (overtraining detection)
- [ ] Implement Analytics Specialist (insights and predictions)
- [ ] Implement Motivation Agent (achievements, encouragement)
- [ ] Add more sophisticated conflict resolution

### **Phase 6: On-Demand Chat (Week 7)** (Secondary)
- [ ] Implement Coach Orchestrator agent for Q&A
- [ ] Add `coach_jobs` DynamoDB table
- [ ] Create `/api/coach/ask` endpoint
- [ ] Build chat UI component (secondary feature)
- [ ] Test common question scenarios

### **Phase 7: Polish & Demo Prep (Week 8)**
- [ ] Add observability (CloudWatch logs, metrics)
- [ ] Performance optimization (parallel user processing)
- [ ] Create demo scenarios with realistic sample data
- [ ] Add error handling and edge cases
- [ ] Prepare presentation materials with before/after examples

---

## Cost Estimates

### **Primary Cost: Weekly Analysis**

**Weekly Lambda Invocations** (Every Monday):
- Weekly Analyzer: 1 invocation per user
- Specialist agents: ~2 invocations per user (avg, only when issues detected)
- Total: ~3 Lambda invocations per user per week

**Bedrock Claude Costs**:
- Weekly Analyzer: ~3K input + 1K output tokens per user
- Specialist agents: ~4K input + 2K output tokens (when invoked)
- Avg cost per user per week: ~$0.03-0.05

**Monthly Cost for 1000 users**:
- 1000 users × 4 weeks × $0.04 avg = **$160/month**
- Lambda compute: ~$5/month
- **Total: ~$165/month**

### **Secondary Cost: On-Demand Chat** (Optional)

**Per Question**:
- Orchestrator: 1 invocation
- Specialist agents: ~2 invocations (avg)
- Cost per question: ~$0.05-0.08

**If 1000 users ask 2 questions/month**:
- 2000 questions × $0.06 = **$120/month**

### **Total Monthly Cost (1000 users)**:
- **Weekly analysis: $165/month** (proactive, all users)
- **On-demand chat: $120/month** (optional, if used)
- **Grand total: ~$285/month**

**Much more cost-effective than:**
- Running persistent containers: ~$500-1000/month
- Human coaches: $100+ per client per month

**Cost scales linearly** with users, enabling freemium model.

---

## Key Advantages of This Architecture

### **1. Proactive Coaching (Not Reactive)** ⭐
- User doesn't need to diagnose problems themselves
- Agent automatically detects plateaus and anomalies
- Weekly rhythm matches real coaching cadence
- Reduces cognitive load for users

### **2. Data-Driven with Noise Filtering**
- 14-day trend analysis filters out daily fluctuations
- Avoids over-reacting to water retention, poor sleep, etc.
- Statistical approach to plateau detection
- Minimum data requirements prevent premature adjustments

### **3. Transparent Plan Adjustments**
- Users see exactly what changed and why
- Reasoning is stored and displayed
- Plan version history for accountability
- Builds trust through transparency

### **4. Separation of Concerns**
- Each agent has one job, easier to test and improve
- Weekly Analyzer coordinates specialist agents
- Specialists focus on domain-specific recommendations

### **5. Scalability**
- Lambda auto-scales, no infrastructure management
- EventBridge handles scheduling for all users
- Parallel processing possible for large user bases

### **6. Cost Efficiency**
- ~$0.04 per user per week for AI coaching
- Pay only for actual AI usage, not idle time
- 100x cheaper than human coaches

### **7. Intelligent Conflict Resolution**
- Detects when recommendations conflict (e.g., cut calories vs add volume)
- Makes trade-offs based on user's primary goal
- Coordinates multi-domain adjustments

### **8. Extensibility**
- Easy to add new specialists (e.g., injury prevention, supplement timing)
- New specialist agents can be added independently without modifying orchestrator
- MCP servers enable external data integration
- Orchestrator pattern: All complexity in specialists, simple coordination logic

### **9. Type Safety & Reliability**
- Pydantic models ensure structured, validated outputs
- Specialist algorithms are independently testable with fixed inputs
- Clear contracts between orchestrator and specialists

### **10. Observability**
- Each agent is independently traceable
- Weekly analysis results stored for audit
- Plan change history preserved

---

## Comparison: ALEX Financial Planner vs Fitness Coach

| Aspect | ALEX (Financial) | Fitness Coach |
|--------|------------------|---------------|
| **Orchestrator** | Planner | Coach Orchestrator |
| **Specialists** | Tagger, Reporter, Charter, Retirement, Researcher | Nutrition, Training, Recovery, Analytics, Motivation |
| **MCP Servers** | Playwright (web research) | USDA Food DB, Exercise Library |
| **Tools** | Market insights, price updates | TDEE calc, 1RM calc, trend analysis |
| **Data Source** | Aurora PostgreSQL | DynamoDB |
| **Conflict Type** | Data validation | Competing recommendations |
| **Output** | Portfolio report + charts | Coaching advice + action plan |

---

## Next Steps

1. **✅ Architecture Updated** - Now reflects proactive weekly analysis model
2. **Decide on implementation order** - Recommended: Start with Phase 1 (Weekly Analyzer + basic detection)
3. **Set up project structure** - Create `ai_agents/` directory
4. **Choose MVP scope** - Weekly analysis + Nutrition + Training specialists (no MCP servers initially)
5. **Begin implementation** - Start with core detection logic and function tools

### **Recommended First Steps:**

**Option A: Start with Weekly Analyzer MVP**
- Create `ai_agents/weekly_analyzer/` directory
- Implement basic detection rules (weight plateau, strength plateau)
- Add DynamoDB tables (`weekly_analyses`, `active_plans`)
- Create function tools (`analyze_weight_trend`, `detect_strength_plateau`)
- Test with sample data locally

**Option B: Start with Specialist Agents**
- Implement Nutrition Specialist agent
- Implement Training Specialist agent
- Create function tools they'll use
- Test in isolation before integrating with Weekly Analyzer

**Option C: Full End-to-End Setup**
- Set up entire project structure
- Create all DynamoDB tables
- Implement EventBridge cron rule
- Build complete flow but with simplified logic

### **What Would You Like Me to Build First?**

I can generate:
- ✨ **Weekly Progress Analyzer agent code** (detection rules, plan adjuster)
- ✨ **Nutrition Specialist implementation**
- ✨ **Training Specialist implementation**
- ✨ **Terraform configs** (Lambda, EventBridge, DynamoDB)
- ✨ **DynamoDB schema definitions**
- ✨ **Shared function tools** (TDEE, macros, trend analysis)
- ✨ **Frontend Weekly Analysis Dashboard** (React/Next.js component)

Let me know which component you'd like to start with!
