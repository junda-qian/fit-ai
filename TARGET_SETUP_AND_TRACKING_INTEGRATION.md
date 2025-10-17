# Target Setup and Tracking Integration Plan

## Overview

This document outlines the integration strategy between the **Energy Intake Calculator**, **Workout Planner**, and **Tracking Page** to create a seamless user journey from initial setup to ongoing progress tracking.

---

## User Journey Flow

```
Phase 1: Initial Setup (One-time)
├─ Energy Intake Calculator → Generate calorie & macro targets
└─ Workout Planner → Generate structured workout routine

Phase 2: Ongoing Execution
├─ Tracking Dashboard → View targets & log daily data
├─ Nutrition Tracking → Log meals against macro targets
└─ Workout Tracking → Log exercises against planned routine

Phase 3: AI-Driven Optimization (Future)
├─ Nutrition Coach Agent → Adjust food plans based on progress
└─ Training Coach Agent → Adjust workout plans based on performance
```

This mirrors real-world coaching: **Assess → Plan → Execute → Adjust**

---

## Data Architecture

### New Database Tables/Collections

```python
# User profiles (stores calculator outputs)
user_profiles:
  - id (UUID, primary key)
  - user_id (UUID, foreign key)
  - target_calories (INT) - daily calorie target
  - target_protein (FLOAT) - grams
  - target_carbs (FLOAT) - grams
  - target_fats (FLOAT) - grams
  - bmr (INT) - basal metabolic rate
  - tdee (INT) - total daily energy expenditure
  - activity_level (FLOAT) - multiplier used
  - goal (STRING) - "bulk", "cut", "maintain"
  - body_weight_kg (FLOAT)
  - body_fat_pct (FLOAT)
  - created_at (TIMESTAMP)
  - updated_at (TIMESTAMP)

# Workout plans (stores planner outputs)
workout_plans:
  - id (UUID, primary key)
  - user_id (UUID, foreign key)
  - plan_name (STRING) - e.g., "Upper/Lower Split"
  - description (TEXT) - plan overview
  - frequency (STRING) - e.g., "4x/week", "PPL 6x/week"
  - exercises (JSON) - full exercise array from planner
    [
      {
        "name": "Barbell Squat",
        "sets": 4,
        "reps": "6-8",
        "rpe": 8,
        "muscle_group": "Quads",
        "day": "Lower A"
      },
      ...
    ]
  - duration_weeks (INT) - planned program length
  - active (BOOLEAN) - is this the current plan?
  - generated_at (TIMESTAMP)
  - deactivated_at (TIMESTAMP, nullable)

# Nutrition logs (daily meal tracking)
nutrition_logs:
  - id (UUID, primary key)
  - user_id (UUID, foreign key)
  - date (DATE)
  - meal_type (STRING) - "breakfast", "lunch", "dinner", "snack"
  - time (TIME)
  - calories (INT)
  - protein (FLOAT)
  - carbs (FLOAT)
  - fats (FLOAT)
  - food_items (JSON) - array of foods eaten
  - notes (TEXT, nullable)
  - created_at (TIMESTAMP)

# Workout logs (completed workout sessions)
workout_logs:
  - id (UUID, primary key)
  - user_id (UUID, foreign key)
  - date (DATE)
  - workout_name (STRING) - e.g., "Upper Body A"
  - exercises (JSON) - actual performed exercises
    [
      {
        "name": "Bench Press",
        "sets": [
          {"reps": 8, "weight": 185, "rpe": 7.5},
          {"reps": 8, "weight": 185, "rpe": 8},
          ...
        ]
      },
      ...
    ]
  - duration_minutes (INT)
  - notes (TEXT, nullable)
  - completed (BOOLEAN)
  - created_at (TIMESTAMP)

# Body measurement logs
body_logs:
  - id (UUID, primary key)
  - user_id (UUID, foreign key)
  - date (DATE)
  - weight (FLOAT) - in kg or lbs
  - body_fat_pct (FLOAT, nullable)
  - measurements (JSON, nullable) - chest, waist, arms, etc.
  - photos (ARRAY of URLs, nullable)
  - notes (TEXT, nullable)
  - created_at (TIMESTAMP)

# Daily summaries (pre-computed aggregations for performance)
daily_summaries:
  - id (UUID, primary key)
  - user_id (UUID, foreign key)
  - date (DATE, unique per user)
  - total_calories (INT)
  - total_protein (FLOAT)
  - total_carbs (FLOAT)
  - total_fats (FLOAT)
  - workouts_completed (INT)
  - weight (FLOAT, nullable)
  - created_at (TIMESTAMP)
  - updated_at (TIMESTAMP)
```

---

## Backend API Endpoints

### Energy Calculator Integration

```python
# Save user profile after calculator completes
POST /api/user-profile
Request Body:
{
  "user_id": "uuid",
  "target_calories": 2640,
  "target_protein": 180,
  "target_carbs": 330,
  "target_fats": 73,
  "bmr": 1850,
  "tdee": 2400,
  "activity_level": 1.5,
  "goal": "bulk",
  "body_weight_kg": 80,
  "body_fat_pct": 15
}
Response:
{
  "id": "uuid",
  "message": "Profile saved successfully",
  "created_at": "2025-10-16T10:30:00Z"
}

# Get user profile (for tracking dashboard)
GET /api/user-profile/{user_id}
Response:
{
  "target_calories": 2640,
  "target_protein": 180,
  "target_carbs": 330,
  "target_fats": 73,
  "goal": "bulk",
  "bmr": 1850,
  "tdee": 2400,
  "updated_at": "2025-10-16T10:30:00Z"
}

# Update user profile (when recalculating)
PUT /api/user-profile/{user_id}
Request Body: (same as POST)
Response: (same as POST)
```

### Workout Planner Integration

```python
# Save workout plan after planner generates it
POST /api/workout-plan
Request Body:
{
  "user_id": "uuid",
  "plan_name": "Upper/Lower 4-Day Split",
  "description": "Evidence-based program for intermediate lifters",
  "frequency": "4x/week",
  "exercises": [...],  # Full exercise array from planner
  "duration_weeks": 8
}
Response:
{
  "id": "uuid",
  "message": "Workout plan saved and activated",
  "created_at": "2025-10-16T11:00:00Z"
}

# Get active workout plan (for tracking dashboard)
GET /api/workout-plan/{user_id}/active
Response:
{
  "id": "uuid",
  "plan_name": "Upper/Lower 4-Day Split",
  "frequency": "4x/week",
  "exercises": [...],
  "generated_at": "2025-10-16T11:00:00Z"
}

# Get all workout plans (history)
GET /api/workout-plan/{user_id}/all
Response:
[
  {
    "id": "uuid",
    "plan_name": "Upper/Lower 4-Day Split",
    "active": true,
    "generated_at": "2025-10-16T11:00:00Z"
  },
  {
    "id": "uuid-2",
    "plan_name": "PPL 6-Day Program",
    "active": false,
    "deactivated_at": "2025-10-10T08:00:00Z"
  }
]

# Switch active plan
PUT /api/workout-plan/{plan_id}/activate
Response:
{
  "message": "Plan activated successfully"
}
```

### Tracking Endpoints

```python
# Get nutrition logs (paginated by date range)
GET /api/nutrition/logs?user_id={uuid}&start_date=2025-10-01&end_date=2025-10-16
Query Parameters:
  - user_id (required)
  - start_date (required, max 31 days range)
  - end_date (required)
Response:
{
  "logs": [
    {
      "id": "uuid",
      "date": "2025-10-16",
      "meal_type": "breakfast",
      "time": "08:30",
      "calories": 450,
      "protein": 35,
      "carbs": 60,
      "fats": 12,
      "food_items": [
        {"name": "Oatmeal", "amount": "100g", "calories": 150},
        {"name": "Whey Protein", "amount": "30g", "calories": 120},
        ...
      ]
    },
    ...
  ],
  "total_count": 45
}

# Add nutrition log
POST /api/nutrition/logs
Request Body:
{
  "user_id": "uuid",
  "date": "2025-10-16",
  "meal_type": "breakfast",
  "time": "08:30",
  "calories": 450,
  "protein": 35,
  "carbs": 60,
  "fats": 12,
  "food_items": [...]
}

# Get workout logs
GET /api/workout/logs?user_id={uuid}&start_date=2025-10-01&end_date=2025-10-16
Response:
{
  "logs": [
    {
      "id": "uuid",
      "date": "2025-10-16",
      "workout_name": "Upper Body A",
      "exercises": [...],
      "duration_minutes": 65,
      "completed": true
    },
    ...
  ]
}

# Add workout log
POST /api/workout/logs
Request Body:
{
  "user_id": "uuid",
  "date": "2025-10-16",
  "workout_name": "Upper Body A",
  "exercises": [
    {
      "name": "Bench Press",
      "sets": [
        {"reps": 8, "weight": 185, "rpe": 7.5},
        {"reps": 8, "weight": 185, "rpe": 8}
      ]
    }
  ],
  "duration_minutes": 65,
  "completed": true
}

# Get daily summary (fast aggregated data)
GET /api/summary/daily?user_id={uuid}&date=2025-10-16
Response:
{
  "date": "2025-10-16",
  "total_calories": 2450,
  "total_protein": 185,
  "total_carbs": 255,
  "total_fats": 78,
  "workouts_completed": 1,
  "weight": 80.5,

  # Target comparison (fetched from user_profile)
  "targets": {
    "calories": 2640,
    "protein": 180,
    "carbs": 330,
    "fats": 73
  },

  # Progress percentages
  "progress": {
    "calories_pct": 93,
    "protein_pct": 103,
    "carbs_pct": 77,
    "fats_pct": 107
  }
}

# Get weekly summary
GET /api/summary/weekly?user_id={uuid}&start_date=2025-10-10&end_date=2025-10-16
Response:
{
  "week_start": "2025-10-10",
  "week_end": "2025-10-16",
  "avg_calories": 2380,
  "avg_protein": 178,
  "avg_carbs": 290,
  "avg_fats": 72,
  "training_days": 5,
  "weight_change": -0.5,
  "weight_start": 81.0,
  "weight_end": 80.5
}
```

---

## Frontend Integration Flow

### Step 1: Energy Calculator Completion

**Location:** `frontend/components/energy-calculator.tsx`

**New functionality:**
1. After calculation results are displayed, add "Save & Continue" button
2. On click, POST results to `/api/user-profile`
3. Show success message: "Targets saved! Setting up your workout plan..."
4. Navigate to Workout Planner page

**Updated UI:**
```tsx
<div className="results-section">
  <h2>Your Targets</h2>
  <p>Daily Calories: {results.target_calories} kcal</p>
  <p>Protein: {results.target_protein}g</p>
  <p>Carbs: {results.target_carbs}g</p>
  <p>Fats: {results.target_fats}g</p>

  <div className="actions">
    <button onClick={handleRecalculate}>Recalculate</button>
    <button onClick={handleSaveAndContinue} className="primary">
      Save & Continue to Workout Planner →
    </button>
  </div>
</div>
```

### Step 2: Workout Planner Completion

**Location:** `frontend/components/workout-planner.tsx`

**New functionality:**
1. After workout plan is generated, add "Start This Plan" button
2. On click, POST plan to `/api/workout-plan`
3. Deactivate any previous plans
4. Show success message: "Plan activated! Let's start tracking your progress..."
5. Navigate to Tracking Dashboard

**Updated UI:**
```tsx
<div className="generated-plan">
  <h2>{plan.plan_name}</h2>
  <p>{plan.description}</p>
  <p>Frequency: {plan.frequency}</p>

  <div className="exercises-preview">
    {/* Show exercise summary */}
  </div>

  <div className="actions">
    <button onClick={handleRegenerate}>Generate New Plan</button>
    <button onClick={handleStartPlan} className="primary">
      Start This Plan →
    </button>
  </div>
</div>
```

### Step 3: Tracking Dashboard Display

**Location:** `frontend/app/tracking/dashboard/page.tsx` (new page)

**Data fetching on load:**
```tsx
useEffect(() => {
  // Fetch user targets
  const targets = await fetch(`/api/user-profile/${userId}`);
  setTargets(targets);

  // Fetch active workout plan
  const plan = await fetch(`/api/workout-plan/${userId}/active`);
  setWorkoutPlan(plan);

  // Fetch today's summary
  const today = await fetch(`/api/summary/daily?user_id=${userId}&date=${todayDate}`);
  setTodaySummary(today);
}, [userId]);
```

**Dashboard UI:**
```tsx
<div className="dashboard">
  <h1>Dashboard - {formattedDate}</h1>

  {/* Nutrition Progress */}
  <section className="nutrition-card">
    <h2>🍽️ Nutrition</h2>
    <ProgressBar
      current={todaySummary.total_calories}
      target={targets.target_calories}
    />
    <p>{todaySummary.total_calories} / {targets.target_calories} kcal</p>

    <div className="macros">
      <MacroBar label="Protein" current={todaySummary.total_protein} target={targets.target_protein} />
      <MacroBar label="Carbs" current={todaySummary.total_carbs} target={targets.target_carbs} />
      <MacroBar label="Fats" current={todaySummary.total_fats} target={targets.target_fats} />
    </div>

    <button>+ Log Meal</button>
  </section>

  {/* Workout Progress */}
  <section className="workout-card">
    <h2>💪 Workout</h2>
    <p>Active Plan: {workoutPlan.plan_name}</p>
    <p>Frequency: {workoutPlan.frequency}</p>

    {todaySummary.workouts_completed > 0 ? (
      <p>✅ Completed today</p>
    ) : (
      <p>⏳ Not logged yet</p>
    )}

    <button>+ Log Workout</button>
  </section>

  {/* Weekly Summary */}
  <section className="weekly-summary">
    <h2>📈 This Week</h2>
    <p>Avg Calories: {weeklySummary.avg_calories} kcal/day</p>
    <p>Training Days: {weeklySummary.training_days}/6</p>
    <p>Weight Change: {weeklySummary.weight_change} lbs</p>
  </section>
</div>
```

---

## Implementation Sequence

### Phase 1: Data Persistence (Backend)
1. ✅ Create database tables/collections
2. ✅ Implement `/api/user-profile` endpoints (POST, GET, PUT)
3. ✅ Implement `/api/workout-plan` endpoints (POST, GET, PUT)
4. ✅ Add user authentication/session management (if not exists)

### Phase 2: Calculator & Planner Integration (Frontend + Backend)
1. ✅ Update Energy Calculator to include macro outputs (user will add custom algorithm)
2. ✅ Add "Save & Continue" button to Energy Calculator
3. ✅ Implement save handler that POSTs to `/api/user-profile`
4. ✅ Add "Start This Plan" button to Workout Planner
5. ✅ Implement save handler that POSTs to `/api/workout-plan`
6. ✅ Add navigation flow: Calculator → Planner → Dashboard

### Phase 3: Tracking Dashboard (Frontend + Backend)
1. ✅ Create `/tracking/dashboard` page
2. ✅ Fetch and display user targets from profile
3. ✅ Fetch and display active workout plan
4. ✅ Implement today's progress view with progress bars
5. ✅ Add weekly summary display

### Phase 4: Logging Features (Full Stack)
1. ✅ Implement `/api/nutrition/logs` endpoints
2. ✅ Build nutrition logging form
3. ✅ Implement `/api/workout/logs` endpoints
4. ✅ Build workout logging form
5. ✅ Implement `/api/summary/daily` aggregation
6. ✅ Add real-time progress updates

### Phase 5: Historical Views (Full Stack)
1. ✅ Build `/tracking/nutrition` calendar view
2. ✅ Build `/tracking/workouts` calendar view
3. ✅ Build `/tracking/progress` charts page
4. ✅ Implement pagination and date range filtering
5. ✅ Add virtual scrolling for long lists

### Phase 6: AI Coach Agents (Future)
1. 🔮 Nutrition Coach Agent: Analyze progress, adjust macros
2. 🔮 Training Coach Agent: Analyze performance, adjust volume/intensity
3. 🔮 Weekly check-in system with AI recommendations

---

## Performance Considerations

### Query Optimization
- Index `user_id` and `date` columns in all logs tables
- Limit date range queries to max 31 days
- Use `daily_summaries` table for fast dashboard loads
- Pre-compute weekly/monthly aggregations

### Caching Strategy
```python
# Cache frequently accessed data
- User targets: Cache for 1 hour (rarely changes)
- Active workout plan: Cache for 1 hour (rarely changes)
- Today's summary: Cache for 5 minutes (updates frequently)
- This week's summary: Cache for 15 minutes
```

### Frontend Optimization
- Use React Query for data fetching and caching
- Implement virtual scrolling for long lists (react-window)
- Lazy load historical data
- Optimistic updates for logging actions

---

## User Experience Flow Diagram

```
┌─────────────────────────────────────────────────────┐
│                                                      │
│  User starts fitness journey                        │
│                                                      │
└──────────────────┬──────────────────────────────────┘
                   │
                   ▼
┌─────────────────────────────────────────────────────┐
│  Step 1: Energy Intake Calculator                   │
│  ├─ Input: weight, body fat %, activity level       │
│  ├─ Output: target calories & macros                │
│  └─ Action: "Save & Continue" → POST /user-profile  │
└──────────────────┬──────────────────────────────────┘
                   │
                   ▼
┌─────────────────────────────────────────────────────┐
│  Step 2: Workout Planner                            │
│  ├─ Input: training status, age, goals              │
│  ├─ Output: personalized workout program            │
│  └─ Action: "Start Plan" → POST /workout-plan       │
└──────────────────┬──────────────────────────────────┘
                   │
                   ▼
┌─────────────────────────────────────────────────────┐
│  Step 3: Tracking Dashboard (Ongoing)               │
│  ├─ Displays: targets, active plan, today's progress│
│  ├─ Actions: Log meals, log workouts, log weight    │
│  └─ Navigation: Dashboard, Nutrition, Workouts      │
└──────────────────┬──────────────────────────────────┘
                   │
                   ▼
┌─────────────────────────────────────────────────────┐
│  Future: AI Coach Agents                            │
│  ├─ Nutrition Agent: Weekly macro adjustments       │
│  ├─ Training Agent: Volume/intensity optimization   │
│  └─ Uses: Logged data + original algorithm logic    │
└─────────────────────────────────────────────────────┘
```

---

## Database Choice Recommendations

Given the current AWS infrastructure:

**Option 1: DynamoDB (Serverless, fits current architecture)**
- ✅ Fully managed, auto-scaling
- ✅ Already using AWS ecosystem
- ✅ Pay-per-request pricing
- ✅ Fast key-value queries
- ⚠️ Requires careful schema design for query patterns

**Option 2: Aurora Serverless PostgreSQL**
- ✅ Relational, easier for complex queries
- ✅ Serverless auto-scaling
- ✅ ACID compliance
- ✅ Familiar SQL interface
- ⚠️ Slightly higher cost for low usage

**Option 3: MongoDB Atlas (Serverless)**
- ✅ Flexible JSON documents (good for exercise/food items)
- ✅ Serverless tier available
- ✅ Easy to query and aggregate
- ⚠️ Outside AWS ecosystem

**Recommendation:** Start with **DynamoDB** to stay within AWS serverless architecture, then migrate to Aurora PostgreSQL if complex relational queries become necessary.

---

## Security Considerations

1. **User Authentication**
   - Implement user login/registration system (currently missing)
   - Use AWS Cognito for user management
   - Generate unique user_id for each account

2. **Data Privacy**
   - Encrypt sensitive data (body measurements, photos)
   - Implement row-level security (users can only access their own data)
   - HIPAA compliance considerations (if targeting US market)

3. **API Security**
   - Add JWT token validation to all endpoints
   - Rate limiting on write operations
   - Input validation and sanitization

---

## Success Metrics

**Technical:**
- Dashboard loads in < 1 second
- Single day summary loads in < 500ms
- API response times < 200ms
- Support 10,000+ log entries per user

**User Experience:**
- < 2 minutes to complete setup (Calculator + Planner)
- < 30 seconds to log a meal
- < 60 seconds to log a workout
- Clear visual feedback on progress vs. targets

---

**Document Version:** 1.0
**Created:** 2025-10-17
**Purpose:** Integration specification for connecting Energy Calculator, Workout Planner, and Tracking features
