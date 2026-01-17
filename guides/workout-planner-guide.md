# Workout Planner - Complete Guide

## What Is It?

The Workout Planner is an intelligent training program generator that creates personalized workout plans based on your training level, recovery capacity, and goals. It's like having a personal trainer who designs your program using exercise science and optimization algorithms.

Think of it as a smart calculator that:
- Figures out how much training volume you need for each muscle group
- Selects the right exercises from a database
- Distributes them across your training days
- Sets appropriate intensity levels based on your experience

## Why Does It Exist?

Creating an effective workout plan is complex. You need to:
- Balance volume across all muscle groups
- Avoid overtraining or undertraining
- Choose the right exercises for your goals
- Organize workouts efficiently across the week
- Match intensity to your training level

The Workout Planner solves this by using:
1. **Evidence-based formulas** for volume calculation
2. **Exercise database** with muscle activation matrices
3. **Smart algorithms** (both AI and deterministic) for optimization
4. **Validation systems** to ensure safe, effective programs

## Two Methods Available

### Method 1: AI-Powered (LLM)
- Uses AWS Bedrock (Amazon Nova Lite) to generate plans
- Flexible and creative with exercise selection
- Takes 3-10 seconds
- Costs ~$0.01-0.05 per plan
- Best for varied, adaptive programs

### Method 2: Algorithm-Based (Deterministic)
- Pure mathematical optimization
- Fast (<100ms)
- Free (no API costs)
- Same input = same output
- Best for consistency and explainability

---

## Core Algorithms

### Step 1: Calculate Optimal Sets Per Muscle Group

This formula determines how many sets per week each muscle group needs:

```
Optimal Sets = ((Frequency Factor) * 5)
               * Recovery Factor
               * Energy Balance Factor
               * √(Training Status)
               * Age Factor
               + Sex Bonus
```

**Breaking it down**:

#### 1. Frequency Factor
```
If Training Frequency < 3: use Training Frequency
Otherwise: use 2.5
```

**Why**: Training frequency has diminishing returns above 2-3 days/week for beginners.

**Example**:
- 2 days/week → 2.0
- 3 days/week → 2.5 (capped)
- 6 days/week → 2.5 (capped)

#### 2. Base Volume (Frequency Factor × 5)
This gives us a baseline of 10-12.5 sets per muscle group per week.

**Example**:
- 2.5 × 5 = 12.5 sets

#### 3. Recovery Factor (0.5 - 1.2)
How well you recover from training.

**Factors that affect recovery**:
- Sleep quality
- Stress levels
- Nutrition
- Genetics
- Age

**Example values**:
- 0.5 = Poor recovery (high stress, poor sleep)
- 1.0 = Normal recovery
- 1.2 = Excellent recovery (young, low stress, great sleep)

#### 4. Energy Balance Factor
Same as in Energy Calculator - your calorie intake relative to maintenance.

**Why it matters for volume**:
- Surplus (1.2) = Can handle more volume, building muscle
- Maintenance (1.0) = Moderate volume
- Deficit (0.8) = Less volume, harder to recover on fewer calories

#### 5. Training Status Factor (√Status)
```
Novice = 1 → √1 = 1.0
Intermediate = 2 → √2 = 1.41
Advanced = 3 → √3 = 1.73
```

**Why square root**: Volume needs increase with training status, but not linearly. Square root gives a reasonable progression.

#### 6. Age Factor
```
Age Factor = 1 - ((MAX(Age - 50, 0)) / 10 * 0.12)
```

**What it does**:
- Under 50: No penalty (factor = 1.0)
- Age 60: Factor = 0.88 (12% reduction)
- Age 70: Factor = 0.76 (24% reduction)

**Why**: Recovery capacity declines after 50, so optimal volume decreases slightly.

#### 7. Sex Bonus
```
Male (0): +0 sets
Female (1): +3 sets
```

**Why**: Research shows females can typically handle slightly higher training volumes relative to their muscle mass.

### Complete Example Calculation

**Profile**:
- Training frequency: 4 days/week
- Recovery factor: 1.0 (normal)
- Energy balance: 1.1 (slight surplus)
- Training status: 2 (Intermediate)
- Age: 28
- Sex: Male (0)

**Calculation**:
```
Frequency Factor = 2.5 (capped at 3)
Base = 2.5 * 5 = 12.5

Optimal Sets = 12.5 * 1.0 * 1.1 * √2 * 1.0 + 0
             = 12.5 * 1.0 * 1.1 * 1.41 * 1.0
             = 19.4 sets per muscle per week
```

---

### Step 2: Apply Dedication Level

Your optimal sets get adjusted based on how hard you want to train:

```
Dedication A (Sustainability): 60-75% of optimal
Dedication B (Balanced): 75-90% of optimal
Dedication C (Maximum): 90-100% of optimal
```

**Deterministic algorithm uses slightly wider ranges**:
```
A: 55-80%
B: 70-95%
C: 85-105%
```

**Example** (Optimal = 19.4 sets):
- A: 11.6 - 14.6 sets/week per muscle
- B: 14.6 - 17.5 sets/week per muscle
- C: 17.5 - 19.4 sets/week per muscle

**Which to choose**:
- **A (Sustainability)**: Busy schedule, new to training, prioritize long-term adherence
- **B (Balanced)**: Most people - good results without burnout
- **C (Maximum)**: Experienced, good recovery, want fastest results

---

### Step 3: Set Training Intensity (% of 1RM)

Intensity is based on training status and exercise type:

| Training Status | Compound Exercises | Isolation Exercises |
|----------------|-------------------|-------------------|
| Novice         | 60%              | 60%               |
| Intermediate   | 80%              | 65%               |
| Advanced       | 85%              | 70%               |

**Why lower intensity for isolations**:
- Smaller muscles fatigue faster
- Lower injury risk
- Focus on muscle stimulation, not maximal load

**What this means for reps**:
- 60% = ~12-15 reps
- 65% = ~10-12 reps
- 70% = ~8-10 reps
- 80% = ~6-8 reps
- 85% = ~5-6 reps

---

### Step 4: Exercise Selection (The Hard Part)

This is where the two methods differ significantly.

## LLM Method (AI-Powered)

### How It Works

1. **Generate Detailed Prompt**
   - User profile and constraints
   - Exercise database with activation values
   - Target volume ranges for all 12 muscle groups
   - Example successful plans for reference

2. **LLM Generates Plan**
   - AWS Bedrock (Nova Lite) creates workout structure
   - Selects exercises from database
   - Distributes across training days
   - Assigns sets and intensities

3. **Validation Loop** (up to 5 attempts)
   - Check total training frequency ≤ user's max
   - Calculate actual weekly volumes for each muscle
   - Compare to targets with 30% tolerance
   - If invalid: provide detailed feedback and retry

4. **Accept or Reject**
   - If valid within 5 attempts: return plan
   - If still invalid after 5 attempts: accept with warning

### The LLM Prompt Strategy

The prompt is **massive** (~2000 words) and includes:

**Critical Constraints**:
```
1. VOLUME TARGET (HIGHEST PRIORITY):
   All 12 muscle groups must be within target range

2. FREQUENCY CONSTRAINT:
   Total training days ≤ user's max

3. Daily volume limit:
   Max 10 sets per muscle per day

4. Exercise database:
   Only use exercises from provided list
```

**Reference Example**:
The prompt includes a worked example showing:
- How compound exercises hit multiple muscles
- How to calculate weekly volumes
- How to add isolation exercises for lagging muscles

**Common Mistakes Section**:
Warns the LLM about typical errors:
- Forgetting lower body muscles
- Neglecting abs and calves
- Focusing too much on "push" exercises

**Feedback on Failure**:
If validation fails, the prompt gets augmented with:
```
🚫 VOLUME VALIDATION FAILED - Target range: 14.6-17.5 sets/week

WAY TOO LOW (must fix):
- Calves: 4.0 sets (needs 10.5 more sets)
- Abs: 6.0 sets (needs 8.5 more sets)

SPECIFIC FIXES NEEDED:
- Calves: Add Calf raises or Seated calf raises
- Abs: Add Ab crunches (you can do many sets of this)
```

### Exercise Database Format

```json
{
  "Barbell bench press": {
    "type": "Compound",
    "activation": {
      "Pecs": 1,
      "Delt": 1,
      "Triceps": 1
    }
  },
  "Biceps curls": {
    "type": "Isolation",
    "activation": {
      "Biceps": 1
    }
  }
}
```

**Activation values**:
- **1.0** = Primary target muscle (full activation)
- **0.75** = Strong secondary muscle
- **0.5** = Moderate involvement
- **0.25** = Minor involvement

**Example**: 4 sets of Barbell bench press done 2x/week:
- Pecs: 4 sets × 1.0 activation × 2 days = 8 weekly sets
- Delts: 4 sets × 1.0 activation × 2 days = 8 weekly sets
- Triceps: 4 sets × 1.0 activation × 2 days = 8 weekly sets

---

## Deterministic Method (Algorithm-Based)

### How It Works

1. **Calculate Targets** (same formula as LLM)
2. **Greedy Exercise Selection**
   - Loop through all exercises
   - Score each based on how well it fills volume gaps
   - Add the best exercise
   - Repeat until all muscles reach minimum target
3. **Distribute Across Days**
   - Auto-select split pattern based on frequency
   - Balance exercises per day
4. **Validate**
   - Must pass all constraints or throw error

### Greedy Algorithm Explained

**Scoring System**:

For each exercise, calculate:
```
Score = 0

For each muscle group:
  Current = current weekly volume
  Target = target midpoint
  Gap = max(0, Target - Current)

  If Gap > 0 and exercise activates this muscle:
    Contribution = min(Gap, activation_value)
    Score += Contribution × 5.0  (HIGH priority for under-target muscles)
    Muscles_Helped += 1

  If Current >= Target × 1.2:
    Score -= weekly_contribution × 3.0  (STRONG penalty for over-training)

Score += Muscles_Helped × 1.0  (bonus for multi-muscle exercises)

If exercise already used:
  Score -= 2.0  (penalty for repetition, but allowed)
```

**Why this works**:
- Prioritizes exercises that fill gaps in under-trained muscles
- Penalizes exercises that would cause overtraining
- Rewards compound movements (they help multiple muscles)
- Allows exercise repetition when needed

**Example Iteration**:

Current state:
- Pecs: 0 sets (target: 15)
- Triceps: 0 sets (target: 15)
- Delts: 0 sets (target: 15)
- All others: 0 sets

Best exercise: **Barbell bench press** (hits Pecs, Delts, Triceps)
- Each muscle needs 15 sets
- This exercise fills gap for 3 muscles
- Very high score!

After adding 4 sets × 2x/week:
- Pecs: 8 sets (need 7 more)
- Delts: 8 sets (need 7 more)
- Triceps: 8 sets (need 7 more)

Next best: Another pressing exercise or targeted isolation

### Set Optimization

For each selected exercise, algorithm determines optimal sets (2-5):

```python
def optimize_sets(exercise, current_volumes, targets):
    max_sets_needed = 0

    for muscle in exercise.activation:
        gap = target - current_volume
        if gap > 0:
            sets_for_gap = ceil(gap / activation_value)
            max_sets_needed = max(max_sets_needed, sets_for_gap)

    return clamp(max_sets_needed, min=2, max=5)
```

**Why 2-5 sets**:
- 1 set: Not enough stimulus
- 2-3 sets: Good for beginners or accessory work
- 4-5 sets: Good for main lifts
- 6+ sets: Usually too much per session (fatigue)

### Split Pattern Selection

Based on training frequency:

**2-3 days**: Full Body
```
All exercises done each session
Frequency: 2-3x per week
```

**4-5 days**: Upper/Lower
```
Upper Body Day (frequency: 2-3x/week)
  - All push exercises (chest, shoulders, triceps)
  - All pull exercises (back, biceps)

Lower Body Day (frequency: 2x/week)
  - All leg exercises (quads, hams, glutes, calves)
```

**6-7 days**: Push/Pull/Legs
```
Push Day (2x/week): Pecs, Delts, Triceps
Pull Day (2x/week): Lats, Traps, Biceps
Leg Day (2x/week): Quads, Hams, Glutes, Calves
```

**Auto-adjustment**: If not enough exercises for balanced days, algorithm automatically reduces to simpler split.

Example: User wants 6-day PPL, but algorithm only selected 6 total exercises
- Can't make 3 balanced days with only 2 exercises each
- Automatically switches to Upper/Lower (2 days, 3 exercises each)

---

## Exercise Database

The system includes 49 exercises across all major muscle groups:

### The 12 Muscle Groups

1. **Pecs** (Chest)
2. **Delt** (Shoulders)
3. **Triceps**
4. **Lats** (Upper back)
5. **Traps** (Upper traps)
6. **Biceps**
7. **Erector Spine** (Lower back)
8. **Abs** (Core)
9. **Quadriceps** (Front thighs)
10. **Hamstrings** (Back thighs)
11. **Glutes**
12. **Calves**

### Exercise Categories

**Compound Exercises** (30 exercises)
Multi-joint movements that hit multiple muscles:
- Powerlifting deadlift
- Barbell squats
- Barbell bench press
- Pull-ups & wide pulldowns
- Barbell overhead press
- Romanian deadlifts
- etc.

**Isolation Exercises** (19 exercises)
Single-joint movements for specific muscles:
- Biceps curls
- Triceps extensions
- Leg curls
- Leg extensions
- Calf raises
- Ab crunches
- Lateral raises
- etc.

### Example: Complex Exercise Activation

**Cable rows with spinal flexion**:
```json
{
  "activation": {
    "Delt": 1,
    "Traps": 1,
    "Lats": 1,
    "Biceps": 0.5,
    "Triceps": 0.25,
    "Erector Spine": 0.5,
    "Hamstrings": 0.25,
    "Glutes": 0.25
  }
}
```

This exercise:
- Heavily works: Delts, Traps, Lats (1.0)
- Moderately works: Biceps, Erector Spine (0.5)
- Lightly works: Triceps, Hamstrings, Glutes (0.25)

---

## How the Backend Works

### Technology Stack
- **Language**: Python 3.12
- **Framework**: FastAPI
- **AI Service**: AWS Bedrock (Amazon Nova Lite)
- **Validation**: Pydantic models

### File Structure

```
backend/
├── workout_planner.py             # LLM-based planner
├── workout_planner_deterministic.py  # Algorithm-based planner
└── server.py                      # API endpoint
```

### API Endpoint

```
POST /generate-workout-plan?method=<llm|deterministic>

Request Body:
{
  "training_status": 1-3,
  "sex": 0-1,
  "recovery_factor": 0.5-1.2,
  "energy_balance_factor": 0.8-1.2,
  "age": 10-100,
  "training_frequency": 1-7,
  "dedication_level": "A|B|C"
}

Response:
{
  "estimated_optimal_sets": 19.4,
  "target_volume_range": {
    "min": 14.6,
    "max": 17.5
  },
  "workout_days": [
    {
      "day_name": "Upper Body",
      "frequency_per_week": 2,
      "exercises": [
        {
          "exercise_name": "Barbell bench press",
          "sets": 4,
          "intensity": 80,
          "muscle_activation": {"Pecs": 1, "Delt": 1, "Triceps": 1}
        }
      ]
    }
  ],
  "weekly_volume_summary": [
    {"muscle_group": "Pecs", "weekly_sets": 16.0},
    {"muscle_group": "Delt", "weekly_sets": 15.5},
    ...
  ]
}
```

### Backend Flow (LLM Method)

```
1. Receive request
   ↓
2. Calculate optimal sets
   ↓
3. Generate LLM prompt
   ↓
4. Call AWS Bedrock (Loop up to 5x)
   ↓
5. Parse JSON response
   ↓
6. Validate frequency constraint
   ↓
7. Validate volume targets
   ↓
8. If invalid: Add feedback to prompt, retry
   ↓
9. If valid or max attempts: Return plan
```

### Backend Flow (Deterministic Method)

```
1. Receive request
   ↓
2. Calculate optimal sets and targets
   ↓
3. Run greedy algorithm to select exercises
   ↓
4. Distribute exercises across days
   ↓
5. Validate all constraints
   ↓
6. If invalid: Throw exception with details
   ↓
7. If valid: Return plan
```

---

## How the Frontend Works

### Technology Stack
- **Framework**: Next.js 14 (React)
- **Language**: TypeScript
- **Styling**: Tailwind CSS

### User Interface

**Input Form**:
- Training Status (dropdown)
- Sex (dropdown)
- Age (number)
- Recovery Factor (number, 0.5-1.2)
- Energy Balance Factor (number)
- Training Frequency (dropdown, 1-7 days)
- Dedication Level (dropdown, A/B/C)
- Method Selection (dropdown, LLM/Deterministic)

**Results Display**:
1. **Summary Cards**: Optimal sets, target range, training days
2. **Workout Days**: Each day with exercises, sets, and intensity
3. **Weekly Volume Summary**: Color-coded muscle groups
   - Green: Within target range
   - Yellow: Close (within 50% tolerance)
   - Red: Outlier (way off target)

### Data Flow

```
1. User fills form
   ↓
2. Click "Generate Workout Plan"
   ↓
3. Frontend sends to API with ?method=llm or ?method=deterministic
   ↓
4. Backend processes (3-10s for LLM, <100ms for deterministic)
   ↓
5. Frontend receives plan
   ↓
6. Display workout days and volume summary
   ↓
7. User clicks "Start Plan"
   ↓
8. Plan saved to database
   ↓
9. Redirect to tracking dashboard
```

### Code Location
- **Component**: `frontend/components/workout-planner.tsx`
- **Page**: `frontend/app/workout-planner/page.tsx`

---

## Step-by-Step User Journey

### Step 1: Complete Energy Calculator First
You need a user profile with body metrics before creating a workout plan.

### Step 2: Navigate to Workout Planner
Go to `/workout-planner` in the app.

### Step 3: Enter Training Profile

**Training Status**:
- **Novice**: < 6 months consistent training
- **Intermediate**: 6 months - 2 years
- **Advanced**: 2+ years

**Recovery Factor**:
- **0.5-0.7**: Poor recovery (high stress, poor sleep, older)
- **0.8-1.0**: Normal recovery
- **1.1-1.2**: Excellent recovery (young, low stress, great sleep)

**Energy Balance Factor**:
- Should match your Energy Calculator setting
- **0.8**: Cutting (calorie deficit)
- **1.0**: Maintaining
- **1.1-1.2**: Bulking (calorie surplus)

**Training Frequency**:
- How many days per week you can train
- Be realistic - consistency matters more than frequency

**Dedication Level**:
- **A**: Sustainability - you want steady progress without burnout
- **B**: Balanced - most people choose this
- **C**: Maximum - experienced lifters wanting fastest results

**Method**:
- **LLM**: More creative, flexible plans (costs pennies, takes a few seconds)
- **Deterministic**: Fast, free, consistent (same input = same output)

### Step 4: Generate Plan
Click "Generate Workout Plan" and wait:
- LLM: 3-10 seconds
- Deterministic: <1 second

### Step 5: Review Your Plan

**Check the summary**:
- Optimal sets: Target volume per muscle
- Target range: Acceptable volume range
- Number of training days

**Review each workout day**:
- Day name and frequency (how many times per week)
- Exercises with sets and intensity
- Muscle activation for each exercise

**Check weekly volume summary**:
- All 12 muscle groups with color coding
- Green = perfect, yellow = close, red = outlier

### Step 6: Start Your Plan
Click "Start Plan" to:
- Save plan to your profile
- Activate it for tracking
- Redirect to tracking dashboard

---

## Comparison: LLM vs Deterministic

| Feature | LLM Method | Deterministic Method |
|---------|-----------|---------------------|
| **Speed** | 3-10 seconds | <100ms |
| **Cost** | $0.01-0.05 per plan | $0.00 |
| **Consistency** | Varies slightly each time | Identical for same input |
| **Creativity** | More varied exercise selection | Follows algorithm strictly |
| **Validation** | Soft validation (30% tolerance) | Hard validation (must pass or fail) |
| **Failure Handling** | Accepts after 5 attempts | Throws error immediately |
| **Exercise Distribution** | More flexible splits | Fixed split patterns |
| **Best For** | Users who want variety | Users who want consistency |

### When to Use LLM

✅ You want creative, varied programs
✅ You don't mind waiting a few seconds
✅ You want the AI to "think" about your plan
✅ You're okay with slight variations on regeneration

### When to Use Deterministic

✅ You want instant results
✅ You want to understand exactly how it works
✅ You want the same plan for same inputs
✅ You're testing or comparing plans
✅ You want to avoid API costs

---

## Common Questions

### Q: What if my plan has red (outlier) muscles?

**A**: This can happen for a few reasons:

1. **Very low frequency** (1-2 days/week): Hard to hit all 12 muscles adequately
   - Solution: Increase training frequency

2. **Low dedication level** (A): Lower volume makes it harder to balance
   - Solution: Try dedication level B or C

3. **LLM made a mistake**: Rare, but possible
   - Solution: Regenerate or try deterministic method

4. **Deterministic validation failed**: Plan should have been rejected
   - Should not happen - report as bug if it does

### Q: Can I modify the generated plan?

**A**: Currently the app doesn't have a plan editor, but you can:
1. Save the plan
2. Manually adjust during workout logging
3. Regenerate with different parameters

Future versions may include plan customization.

### Q: Which exercises should I do first?

**A**: General rule of thumb:
1. Compound exercises first (when energy is highest)
2. Isolation exercises last (when energy is lower)

Example order for Upper Body:
1. Barbell bench press (compound)
2. Pull-ups (compound)
3. Barbell overhead press (compound)
4. Biceps curls (isolation)
5. Triceps extensions (isolation)

### Q: What if I can't do an exercise?

**A**: You can:
1. Substitute with a similar exercise
2. Regenerate the plan (might get different exercises)
3. Skip it and do extra sets of similar exercises

Example substitutions:
- Can't do Pull-ups → Lat pulldowns
- Can't do Barbell squats → Leg press
- Can't do Barbell bench → Dumbbell bench

### Q: How long should I follow this plan?

**A**: Typically 6-12 weeks:
- **6-8 weeks**: Minimum for adaptation
- **8-12 weeks**: Optimal for most people
- **12+ weeks**: Diminishing returns, time for variation

After this period, regenerate with updated parameters (likely higher training status).

### Q: What's the difference between intensity and RPE?

**A**:
- **Intensity**: % of 1RM (one-rep max) - how heavy the weight is
  - 80% intensity = you could do 1 more rep with 80% of your max

- **RPE** (Rate of Perceived Exertion): How hard a set feels (0-10 scale)
  - RPE 8 = could do 2 more reps
  - RPE 9 = could do 1 more rep
  - RPE 10 = absolute maximum

The frontend converts intensity to RPE for easier tracking during workouts.

### Q: Why does the algorithm sometimes suggest the same exercise multiple times?

**A**: This is intentional! Research shows:
- Exercise repetition is fine (even beneficial for skill development)
- Total weekly volume matters more than exercise variety
- Some muscles (abs, calves) benefit from frequent stimulation

Example: Doing Ab crunches on all 3 training days is perfectly valid.

### Q: What if I want to train more than 7 days per week?

**A**: Don't! Your body needs rest days to:
- Repair muscle tissue
- Replenish energy stores
- Prevent burnout and injury

Even elite athletes rarely train more than 6-7 days/week, and they split body parts extensively.

---

## Technical Notes for Developers

### Adding New Exercises

To add exercises to the database:

```python
EXERCISE_DATABASE = {
    "Your new exercise": {
        "type": "Compound" or "Isolation",
        "activation": {
            "Muscle1": 1.0,    # Primary
            "Muscle2": 0.5,    # Secondary
            "Muscle3": 0.25    # Minimal
        }
    }
}
```

**Guidelines**:
- Use standard exercise names
- Activation values: 0.25, 0.5, 0.75, or 1.0
- Include all significantly activated muscles
- Categorize correctly (Compound = multi-joint, Isolation = single-joint)

### Modifying Volume Formula

Current formula in both planners (lines 85-99):

```python
@staticmethod
def calculate_optimal_sets(input_data: WorkoutPlannerInput) -> float:
    freq = input_data.training_frequency if input_data.training_frequency < 3 else 2.5

    optimal_sets = (
        (freq * 5) * input_data.recovery_factor
        * input_data.energy_balance_factor
        * math.sqrt(input_data.training_status)
        * (1 - ((max(input_data.age - 50, 0)) / 10 * 0.12))
        + (input_data.sex * 3)
    )

    return round(optimal_sets, 1)
```

To modify:
1. Update both `workout_planner.py` and `workout_planner_deterministic.py`
2. Test with various inputs
3. Verify results are in reasonable range (8-25 sets/muscle/week)

### Adjusting Tolerance

**LLM validation** (`workout_planner.py`, line 556):
```python
tolerance = 0.30  # 30% beyond target range
```

**Deterministic validation** (`workout_planner_deterministic.py`, line 734):
```python
if actual < min_vol * 0.85:  # 15% under tolerance
```

Increase tolerance = more lenient (plans pass easier)
Decrease tolerance = stricter (plans fail more often)

### Testing the API

**Test LLM method**:
```bash
curl -X POST "http://localhost:8000/generate-workout-plan?method=llm" \
  -H "Content-Type: application/json" \
  -d '{
    "training_status": 2,
    "sex": 0,
    "recovery_factor": 1.0,
    "energy_balance_factor": 1.1,
    "age": 28,
    "training_frequency": 4,
    "dedication_level": "B"
  }'
```

**Test deterministic method**:
```bash
curl -X POST "http://localhost:8000/generate-workout-plan?method=deterministic" \
  -H "Content-Type: application/json" \
  -d '{
    "training_status": 2,
    "sex": 0,
    "recovery_factor": 1.0,
    "energy_balance_factor": 1.1,
    "age": 28,
    "training_frequency": 4,
    "dedication_level": "B"
  }'
```

---

## The Science Behind It

### Volume Landmarks (Israetel, 2017)

Modern exercise science recognizes volume landmarks:

1. **MV** (Maintenance Volume): Minimum to maintain muscle
   - ~4-6 sets/muscle/week

2. **MEV** (Minimum Effective Volume): Minimum to grow
   - ~8-10 sets/muscle/week

3. **MAV** (Maximum Adaptive Volume): Optimal growth
   - ~12-20 sets/muscle/week (varies by muscle and individual)

4. **MRV** (Maximum Recoverable Volume): Beyond this = overtraining
   - ~20-25+ sets/muscle/week (highly individual)

Our calculator targets **MAV** range, adjusted for individual factors.

### Why Compound Exercises First?

Research shows:
1. **Neurological efficiency**: Multi-joint movements require more coordination
2. **Energy demands**: Compounds burn more calories, need more ATP
3. **Injury prevention**: Proper form requires fresh nervous system
4. **Strength gains**: Heavy compounds build most strength

### Progressive Overload

The workout planner sets a baseline, but you need progressive overload:

**Ways to progress**:
1. **Weight**: Increase load (most common)
2. **Reps**: More reps at same weight
3. **Sets**: Additional sets (within reason)
4. **Frequency**: Train muscle more often
5. **Range of Motion**: Deeper squats, fuller stretch
6. **Tempo**: Slower eccentric (lowering) phase

The tracking dashboard will help you implement progressive overload over time.

### Frequency vs Volume

Classic bodybuilding: Train each muscle 1x/week (bro split)
Modern research: 2-3x/week is often superior

**Why**:
- Protein synthesis elevated ~48 hours post-training
- Multiple smaller sessions > one giant session
- Better recovery between sessions
- More motor learning opportunities

Our planner automatically distributes volume across frequency for optimal results.

---

## Conclusion

The Workout Planner combines exercise science, optimization algorithms, and AI to create personalized training programs. Whether you choose the flexible LLM method or the fast deterministic method, you get:

- **Evidence-based volume targets** specific to your recovery and goals
- **Balanced muscle development** across all 12 muscle groups
- **Appropriate intensity** for your training level
- **Organized split** matching your training frequency
- **Validated safety** to prevent overtraining

**Remember**:
- The plan is a starting point - adjust based on your response
- Consistency matters more than perfection
- Progressive overload is key to continued gains
- Listen to your body and adjust recovery factors as needed

Now get to training!
