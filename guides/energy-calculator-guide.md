# Energy Intake Calculator - Complete Guide

## What Is It?

The Energy Intake Calculator is a personalized nutrition planning tool that calculates how many calories you should eat each day based on your body composition, activity level, and fitness goals. Think of it as a smart calculator that figures out your daily calorie and macro nutrient (protein, carbs, fats) targets.

## Why Does It Exist?

Instead of guessing how much you should eat, this calculator uses proven scientific formulas to give you accurate, personalized nutrition targets. It's especially useful for people who:
- Want to gain muscle (bulking)
- Want to lose fat (cutting)
- Want to maintain their current weight
- Train regularly and need precise nutrition guidance

## How Does It Work?

### The Process (Simple Version)

1. **You provide your information**: body weight, body fat percentage, activity level, training schedule
2. **The calculator does the math**: using scientific formulas to calculate your metabolism and energy needs
3. **You get your targets**: daily calorie goal and how much protein, carbs, and fats to eat

### The Algorithms (Technical Details)

The calculator uses a series of scientifically-validated formulas in a specific order:

#### Step 1: Calculate Fat-Free Mass
```
Fat-Free Mass = Bodyweight × (1 - Body Fat % / 100)
```

**What it means**: Your body has fat and everything else (muscle, bones, organs, water). This calculates the "everything else" part. For example, if you weigh 75kg with 15% body fat:
- Fat-Free Mass = 75 × (1 - 15/100) = 63.75 kg

**Why it matters**: Muscle burns more calories than fat, so this gives us a better estimate of your metabolism.

---

#### Step 2: Calculate Basal Metabolic Rate (BMR) Using Cunningham Formula
```
BMR = 370 + (21.6 × Fat-Free Mass in kg)
```

**What it means**: BMR is the number of calories your body burns just to stay alive - breathing, heart beating, brain working, etc. The Cunningham formula (from 1991 research) is specifically designed for people who exercise.

**Example**: With 63.75 kg fat-free mass:
- BMR = 370 + (21.6 × 63.75) = 1,747 calories/day

**Why it's used**: Unlike other formulas (like Harris-Benedict), Cunningham focuses on muscle mass, making it more accurate for people who train.

---

#### Step 3: Calculate Training Energy Expenditure
```
Training EE = 0.1 × Bodyweight (kg) × Training Duration (minutes)
```

**What it means**: This estimates how many calories you burn during a weight training session.

**Example**: 75 kg person training for 60 minutes:
- Training EE = 0.1 × 75 × 60 = 450 calories per session

---

#### Step 4: Calculate Rest Day Energy Expenditure
```
Rest Day EE = BMR × Physical Activity Factor × Thermic Effect of Food Factor
```

**What it means**: On days you don't train, you still burn calories through daily activities and digesting food.

**Factors explained**:
- **Physical Activity Factor** (1.0-1.5): How active you are outside the gym
  - 1.0 = Sedentary (desk job, minimal movement)
  - 1.2 = Moderately active (some walking, household chores)
  - 1.4 = Very active (active job, lots of movement)

- **Thermic Effect of Food** (1.0-1.25): Energy burned digesting food
  - 1.0 = Low protein diet
  - 1.15 = High protein diet
  - 1.25 = Very high protein diet

**Example**: BMR of 1,747 with moderate activity (1.2) and high protein (1.15):
- Rest Day EE = 1,747 × 1.2 × 1.15 = 2,411 calories

---

#### Step 5: Calculate Training Day Energy Expenditure
```
Training Day EE = (BMR × Physical Activity Factor + Training EE) × TEF Factor
```

**What it means**: On training days, you burn more calories because of your workout.

**Example**:
- Training Day EE = (1,747 × 1.2 + 450) × 1.15 = 2,928 calories

---

#### Step 6: Calculate Maintenance Energy Intake (Weekly Average)
```
Maintenance = (Training Days × Training Day EE + Rest Days × Rest Day EE) / 7
```

**What it means**: This averages your calorie burn across the week to find your maintenance calories - the amount you need to eat to stay the same weight.

**Example**: Training 4 days per week:
- Maintenance = (4 × 2,928 + 3 × 2,411) / 7 = 2,706 calories/day

---

#### Step 7: Apply Energy Balance Factor (Your Goal)
```
Target Calories = Maintenance × Energy Balance Factor
```

**What it means**: This adjusts your calories based on your goal:
- **0.8** = 20% calorie deficit (weight loss/cutting)
- **1.0** = Maintenance (stay the same weight)
- **1.1** = 10% calorie surplus (muscle gain/bulking)

**Example**: Want to gain muscle (1.1 factor):
- Target Calories = 2,706 × 1.1 = 2,977 calories/day

---

#### Step 8: Calculate Macro Nutrient Targets

Once we have your target calories, we split them into protein, fats, and carbs:

**Protein** (Priority #1):
```
Protein = 1.6g per kg bodyweight
Protein Calories = Protein (g) × 4 calories per gram
```
- Example: 75kg person needs 120g protein = 480 calories

**Fat** (Priority #2):
```
Fat Calories = Target Calories × 0.3 (30% of total)
Fat (g) = Fat Calories / 9 calories per gram
```
- Example: 2,977 × 0.3 = 893 calories = 99g fat

**Carbs** (Fills the rest):
```
Carbs Calories = Target Calories - Protein Calories - Fat Calories
Carbs (g) = Carbs Calories / 4 calories per gram
```
- Example: 2,977 - 480 - 893 = 1,604 calories = 401g carbs

---

## How the Backend Works

### Technology Stack
- **Language**: Python
- **Framework**: FastAPI (for the web API)
- **Validation**: Pydantic (ensures data is correct)

### Architecture

```
User Input → FastAPI Endpoint → EnergyCalculator Class → Results
```

### Backend Components

**1. Input Model (EnergyCalculatorInput)**
- Validates all user inputs
- Ensures values are in correct ranges (e.g., body fat between 0-100%)
- Located in: `backend/energy_calculator.py` (lines 12-21)

**2. Calculator Class (EnergyCalculator)**
- Contains all the calculation methods
- Each formula has its own method (easy to test and maintain)
- All methods are static (don't need an instance)
- Located in: `backend/energy_calculator.py` (lines 48-265)

**3. API Endpoint**
- URL: `POST /calculate-energy`
- Accepts JSON input with your data
- Returns JSON with all calculated results
- Located in: `backend/server.py` (lines 133-147)

**Example API Request**:
```json
{
  "bodyweight_kg": 75,
  "body_fat_percentage": 15,
  "physical_activity_factor": 1.2,
  "thermic_effect_food_factor": 1.15,
  "training_duration_min": 60,
  "energy_balance_factor": 1.1,
  "training_days_per_week": 4
}
```

**Example API Response**:
```json
{
  "fat_free_mass_kg": 63.75,
  "cunningham_bmr": 1747.0,
  "training_energy_expenditure": 450.0,
  "rest_day_energy_expenditure": 2411.0,
  "training_day_energy_expenditure": 2928.0,
  "maintenance_energy_intake": 2706.0,
  "average_target_energy_intake": 2977.0,
  "macro_targets": {
    "protein_grams": 120.0,
    "protein_calories": 480.0,
    "fat_grams": 99.0,
    "fat_calories": 893.0,
    "carbs_grams": 401.0,
    "carbs_calories": 1604.0,
    "protein_percentage": 16.1,
    "fat_percentage": 30.0,
    "carbs_percentage": 53.9
  }
}
```

---

## How the Frontend Works

### Technology Stack
- **Framework**: Next.js 14 (React)
- **Language**: TypeScript
- **Styling**: Tailwind CSS

### User Interface Components

**1. Input Form** (Left Side)
The form is organized into sections:
- **Body Composition**: Weight and body fat %
- **Activity Factors**: Daily activity and diet type
- **Training Schedule**: Session duration and frequency
- **Energy Goal**: Surplus, maintenance, or deficit

**2. Results Display** (Right Side)
Shows your results in colorful cards:
- Fat-Free Mass (blue)
- BMR (purple)
- Training Energy Expenditure (orange)
- Rest/Training Day Expenditure (green/teal)
- Maintenance Calories (indigo)
- Target Calories (gradient - the big goal)
- Macro Targets (red/yellow/green with pie chart)

**3. Save & Continue**
After calculating, you can save your targets to your profile and continue to the Workout Planner.

### Data Flow

```
1. User fills form
   ↓
2. Click "Calculate"
   ↓
3. Frontend sends data to backend API
   ↓
4. Backend processes with formulas
   ↓
5. Frontend receives results
   ↓
6. Results displayed in cards
   ↓
7. User clicks "Save & Continue"
   ↓
8. Profile saved to database
   ↓
9. Redirect to Workout Planner
```

### Code Location
- **Component**: `frontend/components/energy-calculator.tsx`
- **Page**: `frontend/app/calculator/page.tsx`

---

## Step-by-Step User Journey

### Step 1: Navigate to Calculator
Go to `/calculator` page in the app

### Step 2: Enter Body Information
- **Bodyweight**: Your current weight in kilograms
- **Body Fat %**: Estimate using online calculators or get measured professionally

### Step 3: Set Activity Factors
- **Physical Activity Factor**:
  - Choose 1.0 if you sit most of the day
  - Choose 1.2 if you walk around regularly
  - Choose 1.4+ if you have an active job

- **Thermic Effect of Food**:
  - Choose 1.0 for low protein diet (< 1g per kg bodyweight)
  - Choose 1.15 for high protein (1.6g+ per kg bodyweight)

### Step 4: Define Training Schedule
- **Training Duration**: How long each workout session lasts (in minutes)
- **Training Days**: How many days per week you train (0-7)

### Step 5: Set Your Goal
- **Energy Balance Factor**:
  - 0.8 = Aggressive cut (20% deficit)
  - 0.9 = Moderate cut (10% deficit)
  - 1.0 = Maintenance (stay same weight)
  - 1.05-1.1 = Lean bulk (5-10% surplus)
  - 1.2+ = Aggressive bulk (20% surplus)

### Step 6: Calculate
Click the "Calculate Energy Metrics" button. The backend processes your data and returns your personalized results.

### Step 7: Review Results
Check all the metrics:
- Your BMR (baseline metabolism)
- Energy expenditure on training vs rest days
- Target daily calories
- Macro breakdown (protein, fats, carbs)

### Step 8: Save Your Targets
Click "Save & Continue to Workout Planner"
- Your targets are saved to your user profile
- The dashboard will use these targets to track your progress
- You're redirected to create a workout plan

---

## The Science Behind It

### Why Cunningham BMR?

The Cunningham formula is preferred over older formulas (Harris-Benedict, Mifflin-St Jeor) because:
1. **Muscle-focused**: Uses fat-free mass instead of total body weight
2. **More accurate for athletes**: Designed for people who train regularly
3. **Simpler**: Doesn't need age/sex inputs (which add noise)

**Citation**: Cunningham JJ. Body composition as a determinant of energy expenditure: a synthetic review and a proposed general prediction equation. Am J Clin Nutr. 1991;54(6):963-9.

### Why 1.6g Protein per kg?

Research shows that for people doing resistance training:
- **Minimum**: 1.2g/kg to maintain muscle
- **Optimal**: 1.6g/kg to maximize muscle growth
- **Maximum benefit**: Around 2.2g/kg (more doesn't help)

1.6g/kg is the sweet spot for most people.

### Why 30% Fat?

Dietary fat is essential for:
- Hormone production (especially testosterone)
- Vitamin absorption (A, D, E, K)
- Brain function
- Joint health

30% of calories from fat ensures adequate intake without going too high.

### Why Carbs Fill the Rest?

Carbs are:
- Your body's preferred fuel for intense training
- Protein-sparing (prevents muscle breakdown)
- Important for recovery and performance

By setting protein and fat first (essential nutrients), carbs naturally fill the remaining calories.

---

## Common Questions

### Q: What if I don't know my body fat percentage?
**A**: Use online visual estimation guides or get a professional measurement (DEXA scan, caliper test). For a rough estimate:
- Men: 10-15% = visible abs, 15-20% = fit, 20-25% = average
- Women: 18-25% = fit, 25-30% = average, 30-35% = above average

### Q: Can I change my macro percentages?
**A**: The current system uses a fixed approach (1.6g/kg protein, 30% fat, rest carbs). This is evidence-based and works for most people. Custom macro ratios may be added in future versions.

### Q: How accurate is the training energy expenditure?
**A**: The 0.1 × bodyweight × duration formula is a general estimate. Actual burn varies by:
- Exercise intensity
- Rest periods
- Exercise selection
- Individual metabolism

It's accurate enough for planning, but individual results may vary ±20%.

### Q: Should I eat the same calories every day?
**A**: The calculator gives you an average daily target. Some people prefer:
- **Calorie cycling**: More on training days, less on rest days
- **Flat intake**: Same calories every day (easier to track)

Both approaches work if weekly average matches your goal.

### Q: What if I'm not losing/gaining weight as expected?
**A**: The calculator provides a starting point. After 2-3 weeks:
- If not losing weight: Reduce by 5-10%
- If not gaining weight: Increase by 5-10%
- If losing/gaining too fast: Adjust accordingly

Track your actual results and adjust!

---

## Technical Notes for Developers

### File Structure
```
backend/
  ├── energy_calculator.py      # Core calculation logic
  └── server.py                 # FastAPI endpoints

frontend/
  ├── components/
  │   └── energy-calculator.tsx # Main calculator component
  └── app/
      └── calculator/
          └── page.tsx          # Calculator page
```

### Key Design Decisions

1. **Separation of Concerns**: Calculator logic is separate from API logic
2. **Type Safety**: Pydantic models ensure data validation
3. **Stateless**: Each calculation is independent (no stored state)
4. **Testable**: Each formula is a separate method (easy unit testing)

### Testing the API

Using `curl`:
```bash
curl -X POST http://localhost:8000/calculate-energy \
  -H "Content-Type: application/json" \
  -d '{
    "bodyweight_kg": 75,
    "body_fat_percentage": 15,
    "physical_activity_factor": 1.2,
    "thermic_effect_food_factor": 1.15,
    "training_duration_min": 60,
    "energy_balance_factor": 1.1,
    "training_days_per_week": 4
  }'
```

### Extending the Calculator

To add new features:
1. Add new input fields to `EnergyCalculatorInput` model
2. Add calculation method to `EnergyCalculator` class
3. Update `calculate_all()` method to call new calculation
4. Add result field to `EnergyCalculatorOutput` model
5. Update frontend to display new results

---

## Conclusion

The Energy Intake Calculator is a science-backed tool that takes the guesswork out of nutrition planning. By combining proven formulas (Cunningham BMR) with your personal data, it provides accurate calorie and macro targets tailored to your goals.

**Remember**:
- These are starting targets - adjust based on real-world results
- Consistency matters more than perfection
- Track your progress and adapt as needed

Good luck with your fitness journey!
