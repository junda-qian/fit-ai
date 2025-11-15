"""
Generate realistic 90-day test data for progress tracking

This creates a hypothetical user case with realistic variations:
- Weight loss progression (~0.5%/week)
- Daily fluctuations (water retention, digestion)
- Nutrition compliance (80-85%, higher calories on weekends)
- Weekly skinfold measurements (showing fat loss)
- Training 4x/week with occasional missed sessions
"""

import json
import random
from datetime import datetime, date, time, timedelta
from pathlib import Path
import uuid

# Test user ID
TEST_USER_ID = "test_user_90day"

# Starting metrics
START_WEIGHT = 85.0  # kg
START_BODY_FAT = 20.0  # %
TARGET_CALORIES = 2200
TARGET_PROTEIN = 170.0
TARGET_CARBS = 220.0
TARGET_FATS = 73.0

# Training schedule (4x/week: Mon, Tue, Thu, Fri)
TRAINING_DAYS = [0, 1, 3, 4]  # Monday=0, Sunday=6

# Weekly weight loss rate (0.5% per week is healthy)
WEEKLY_LOSS_RATE = 0.005

# Start date (90 days ago from today)
END_DATE = date.today()
START_DATE = END_DATE - timedelta(days=90)


def generate_weight_trajectory():
    """
    Generate realistic weight progression with:
    - Overall downward trend (fat loss)
    - Daily fluctuations (±0.3-0.8kg)
    - Water retention spikes after high-carb days
    - Occasional plateaus
    """
    weights = []
    current_weight = START_WEIGHT

    for day in range(91):
        # Weekly average loss
        weeks_elapsed = day / 7
        expected_weight = START_WEIGHT * (1 - WEEKLY_LOSS_RATE * weeks_elapsed)

        # Daily fluctuation (water, digestion, glycogen)
        daily_noise = random.uniform(-0.5, 0.5)

        # Weekend water retention (higher carbs)
        current_date = START_DATE + timedelta(days=day)
        if current_date.weekday() in [5, 6]:  # Saturday, Sunday
            daily_noise += random.uniform(0.2, 0.6)

        # Post-workout day (glycogen depletion)
        if current_date.weekday() in TRAINING_DAYS:
            daily_noise -= random.uniform(0.1, 0.3)

        # Occasional plateau (adaptive thermogenesis)
        if 35 <= day <= 42:  # Week 6 plateau
            expected_weight += 0.3

        current_weight = expected_weight + daily_noise
        weights.append(round(current_weight, 1))

    return weights


def generate_skinfold_trajectory():
    """
    Generate weekly skinfold measurements
    Shows fat loss progression (sum decreasing)
    """
    skinfolds = []

    # Starting skinfold sum: ~80mm (typical for 20% BF male)
    start_sum = 80.0

    for week in range(13):  # 90 days = ~13 weeks
        # Fat loss: ~2mm per week
        current_sum = start_sum - (week * 2.0)

        # Small weekly variation
        current_sum += random.uniform(-0.5, 0.5)

        # Individual site measurements (proportional distribution)
        # Common 7-site protocol
        skinfolds.append({
            'week': week,
            'sum': round(current_sum, 1),
            'tricep': round(current_sum * 0.12, 1),
            'abdomen': round(current_sum * 0.25, 1),
            'thigh': round(current_sum * 0.18, 1),
            'suprailiac': round(current_sum * 0.20, 1),
            'subscapular': round(current_sum * 0.15, 1),
            'chest': round(current_sum * 0.08, 1),
            'midaxillary': round(current_sum * 0.02, 1),
        })

    return skinfolds


def generate_daily_nutrition(day_index, is_weekend):
    """
    Generate realistic nutrition intake
    - 80-85% compliance overall
    - Weekend: higher calories (social eating)
    - Some days: no tracking
    """
    # 20% chance of no logging
    if random.random() < 0.20:
        return None

    if is_weekend:
        # Weekend: 10-20% over target
        calorie_multiplier = random.uniform(1.10, 1.20)
    else:
        # Weekday: 90-105% of target (good compliance)
        calorie_multiplier = random.uniform(0.90, 1.05)

    calories = TARGET_CALORIES * calorie_multiplier

    # Protein stays consistent (priority macro)
    protein = TARGET_PROTEIN * random.uniform(0.95, 1.05)

    # Fats relatively stable
    fats = TARGET_FATS * random.uniform(0.90, 1.10)

    # Carbs fill the rest
    remaining_cals = calories - (protein * 4) - (fats * 9)
    carbs = remaining_cals / 4

    return {
        'calories': round(calories),
        'protein': round(protein, 1),
        'carbs': round(carbs, 1),
        'fats': round(fats, 1)
    }


def generate_workout_status(current_date):
    """
    Generate workout completion
    - 4x/week on Mon, Tue, Thu, Fri
    - 10% chance of missed session
    """
    if current_date.weekday() in TRAINING_DAYS:
        # 90% adherence
        return 1 if random.random() > 0.10 else 0
    return 0


def main():
    print("🏋️ Generating 90-day test data for hypothetical user...")
    print(f"User: {TEST_USER_ID}")
    print(f"Period: {START_DATE} to {END_DATE}")
    print(f"Starting weight: {START_WEIGHT}kg")
    print(f"Target: {TARGET_CALORIES} cal/day\n")

    # Generate trajectories
    weights = generate_weight_trajectory()
    skinfolds = generate_skinfold_trajectory()

    # Initialize data structures
    user_profile = None
    body_logs = []
    nutrition_logs = []
    workout_logs = []
    daily_summaries = []

    # Generate user profile (updated for Nutrition Agent)
    user_profile = {
        "id": str(uuid.uuid4()),
        "user_id": TEST_USER_ID,

        # Personal info (NEW - required for Nutrition Agent)
        "name": "Alex",
        "age": 30,
        "sex": "male",  # Required for Table 1 (optimal deficit)
        "height_cm": 180,

        # Current metrics
        "body_weight_kg": START_WEIGHT,
        "body_fat_pct": START_BODY_FAT,

        # Fitness goals (UPDATED - new terminology)
        "goal": "lose_weight",  # Changed from "cut"
        "training_status": "intermediate",  # NEW - for Table 3 (bulking)

        # Nutrition targets
        "target_calories": TARGET_CALORIES,
        "target_protein": TARGET_PROTEIN,
        "target_carbs": TARGET_CARBS,
        "target_fats": TARGET_FATS,

        # Energy calculations
        "bmr": 1850.0,
        "tdee": 2640.0,
        "activity_level": 1.4,

        # Account status (NEW)
        "is_active": True,  # For weekly analysis filtering

        # Communication preferences (NEW)
        "communication_style": "encouraging",
        "language": "en",
        "timezone": "UTC",

        # Timestamps
        "created_at": START_DATE.isoformat(),
        "updated_at": datetime.now().isoformat()
    }

    # Generate daily data
    for day in range(91):
        current_date = START_DATE + timedelta(days=day)
        is_weekend = current_date.weekday() in [5, 6]
        week_index = day // 7

        # Body log (daily weight)
        body_log = {
            "id": str(uuid.uuid4()),
            "user_id": TEST_USER_ID,
            "date": current_date.isoformat(),
            "weight": weights[day],
            "body_fat_pct": None,
            "body_fat_method": None,
            "waist_cm": None,
            "hips_cm": None,
            "neck_cm": None,
            "chest_cm": None,
            "bicep_cm": None,
            "thigh_cm": None,
            "skinfolds": None,
            "skinfold_sum": None,
            "photo_front": None,
            "photo_side": None,
            "photo_back": None,
            "measurements": None,
            "notes": None,
            "created_at": datetime.now().isoformat()
        }

        # Add skinfold measurements weekly (every Monday)
        if current_date.weekday() == 0 and week_index < len(skinfolds):
            sf = skinfolds[week_index]
            body_log["skinfolds"] = {
                "tricep": sf['tricep'],
                "abdomen": sf['abdomen'],
                "thigh": sf['thigh'],
                "suprailiac": sf['suprailiac'],
                "subscapular": sf['subscapular'],
                "chest": sf['chest'],
                "midaxillary": sf['midaxillary']
            }
            body_log["skinfold_sum"] = sf['sum']

        body_logs.append(body_log)

        # Nutrition log (if tracked that day)
        nutrition = generate_daily_nutrition(day, is_weekend)
        if nutrition:
            # Create 2-3 meals per day
            num_meals = random.randint(2, 3)
            meals_per_day = []

            for meal_idx in range(num_meals):
                meal_types = ['breakfast', 'lunch', 'dinner', 'snack']
                meal_type = meal_types[min(meal_idx, 2)]

                # Distribute calories across meals
                if num_meals == 2:
                    meal_cals = nutrition['calories'] / 2
                    meal_protein = nutrition['protein'] / 2
                    meal_carbs = nutrition['carbs'] / 2
                    meal_fats = nutrition['fats'] / 2
                else:
                    if meal_idx == 0:  # Breakfast
                        pct = 0.25
                    elif meal_idx == 1:  # Lunch
                        pct = 0.35
                    else:  # Dinner
                        pct = 0.40

                    meal_cals = nutrition['calories'] * pct
                    meal_protein = nutrition['protein'] * pct
                    meal_carbs = nutrition['carbs'] * pct
                    meal_fats = nutrition['fats'] * pct

                # Create meal time
                meal_times = [
                    time(8, 0),   # Breakfast
                    time(12, 30), # Lunch
                    time(18, 30), # Dinner
                ]
                meal_time = meal_times[meal_idx]

                nutrition_log = {
                    "id": str(uuid.uuid4()),
                    "user_id": TEST_USER_ID,
                    "date": current_date.isoformat(),
                    "meal_type": meal_type,
                    "time": meal_time.isoformat(),
                    "calories": round(meal_cals),
                    "protein": round(meal_protein, 1),
                    "carbs": round(meal_carbs, 1),
                    "fats": round(meal_fats, 1),
                    "food_items": [
                        {
                            "name": f"{meal_type.capitalize()} foods",
                            "amount": "1 serving",
                            "calories": round(meal_cals),
                            "protein": round(meal_protein, 1),
                            "carbs": round(meal_carbs, 1),
                            "fats": round(meal_fats, 1),
                            "fdc_id": None
                        }
                    ],
                    "notes": None,
                    "created_at": datetime.now().isoformat()
                }

                nutrition_logs.append(nutrition_log)
                meals_per_day.append(nutrition_log)

        # Workout log
        workout_completed = generate_workout_status(current_date)

        # Daily summary
        day_nutrition_total = {
            'calories': 0,
            'protein': 0,
            'carbs': 0,
            'fats': 0
        }

        # Sum up all meals for this day
        day_meals = [n for n in nutrition_logs if n['date'] == current_date.isoformat()]
        for meal in day_meals:
            day_nutrition_total['calories'] += meal['calories']
            day_nutrition_total['protein'] += meal['protein']
            day_nutrition_total['carbs'] += meal['carbs']
            day_nutrition_total['fats'] += meal['fats']

        daily_summary = {
            "id": str(uuid.uuid4()),
            "user_id": TEST_USER_ID,
            "date": current_date.isoformat(),
            "total_calories": day_nutrition_total['calories'],
            "total_protein": round(day_nutrition_total['protein'], 1),
            "total_carbs": round(day_nutrition_total['carbs'], 1),
            "total_fats": round(day_nutrition_total['fats'], 1),
            "workouts_completed": workout_completed,
            "weight": weights[day],
            "created_at": datetime.now().isoformat(),
            "updated_at": datetime.now().isoformat()
        }

        daily_summaries.append(daily_summary)

    # Save to JSON files
    data_dir = Path("data/tracking")
    data_dir.mkdir(parents=True, exist_ok=True)

    # Load existing data
    def load_existing(filename):
        file_path = data_dir / filename
        if file_path.exists():
            with open(file_path, 'r') as f:
                return json.load(f)
        return []

    # Remove any existing test data
    def remove_test_user(data):
        return [item for item in data if item.get('user_id') != TEST_USER_ID]

    # User profiles
    existing_profiles = remove_test_user(load_existing("user_profiles.json"))
    existing_profiles.append(user_profile)
    with open(data_dir / "user_profiles.json", 'w') as f:
        json.dump(existing_profiles, f, indent=2, default=str)

    # Body logs
    existing_body = remove_test_user(load_existing("body_logs.json"))
    existing_body.extend(body_logs)
    with open(data_dir / "body_logs.json", 'w') as f:
        json.dump(existing_body, f, indent=2, default=str)

    # Nutrition logs
    existing_nutrition = remove_test_user(load_existing("nutrition_logs.json"))
    existing_nutrition.extend(nutrition_logs)
    with open(data_dir / "nutrition_logs.json", 'w') as f:
        json.dump(existing_nutrition, f, indent=2, default=str)

    # Daily summaries
    existing_summaries = remove_test_user(load_existing("daily_summaries.json"))
    existing_summaries.extend(daily_summaries)
    with open(data_dir / "daily_summaries.json", 'w') as f:
        json.dump(existing_summaries, f, indent=2, default=str)

    # Stats
    final_weight = weights[-1]
    weight_loss = START_WEIGHT - final_weight
    total_workouts = sum(1 for s in daily_summaries if s['workouts_completed'] > 0)
    nutrition_logged_days = len(set(n['date'] for n in nutrition_logs))

    print("✅ Test data generated successfully!\n")
    print("📊 Summary:")
    print(f"  • Starting weight: {START_WEIGHT}kg")
    print(f"  • Final weight: {final_weight}kg")
    print(f"  • Total loss: {weight_loss:.1f}kg ({(weight_loss/START_WEIGHT)*100:.1f}%)")
    print(f"  • Workouts logged: {total_workouts}/91 days")
    print(f"  • Nutrition logged: {nutrition_logged_days}/91 days")
    print(f"  • Body logs: {len(body_logs)} (daily weight + weekly skinfolds)")
    print(f"  • Nutrition logs: {len(nutrition_logs)} meals")
    print(f"  • Daily summaries: {len(daily_summaries)} days\n")
    print(f"🔑 Test User ID: {TEST_USER_ID}")
    print(f"💾 Data saved to: {data_dir}\n")
    print("🚀 Next steps:")
    print("  1. Restart backend: cd backend && uv run uvicorn server:app --reload")
    print("  2. In browser localStorage, set: fit_tracker_user_id = 'test_user_90day'")
    print("  3. Visit: http://localhost:3000/tracking/progress")


if __name__ == "__main__":
    main()
