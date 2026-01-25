"""
Insert 90 days of realistic sample data into deployed DynamoDB tables

This creates a test user with realistic tracking data:
- Weight loss progression (~0.5%/week)
- Daily nutrition logs with 80-85% compliance
- Weekly skinfold measurements
- Training 4x/week with occasional missed sessions
- Daily summaries and body logs

Usage:
    python insert_sample_data_to_dynamodb.py
"""

import boto3
import json
import random
from datetime import datetime, date, time, timedelta
from decimal import Decimal
import uuid

# AWS Configuration
REGION = "us-east-1"
TABLE_PREFIX = "health-chatbot-dev"

# Test user ID
TEST_USER_ID = "demo_user_90day"

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


def decimal_default(obj):
    """JSON serializer for objects not serializable by default json code"""
    if isinstance(obj, Decimal):
        return float(obj)
    raise TypeError


def python_to_dynamodb(obj):
    """Convert Python objects to DynamoDB format"""
    if obj is None:
        return None
    elif isinstance(obj, bool):
        return obj
    elif isinstance(obj, (int, float)):
        return Decimal(str(obj))
    elif isinstance(obj, str):
        return obj
    elif isinstance(obj, (datetime, date, time)):
        return obj.isoformat()
    elif isinstance(obj, dict):
        return {k: python_to_dynamodb(v) for k, v in obj.items() if v is not None}
    elif isinstance(obj, list):
        return [python_to_dynamodb(item) for item in obj]
    else:
        return obj


def generate_weight_trajectory():
    """Generate realistic weight progression"""
    weights = []
    current_weight = START_WEIGHT

    for day in range(91):
        weeks_elapsed = day / 7
        expected_weight = START_WEIGHT * (1 - WEEKLY_LOSS_RATE * weeks_elapsed)

        daily_noise = random.uniform(-0.5, 0.5)

        current_date = START_DATE + timedelta(days=day)
        if current_date.weekday() in [5, 6]:
            daily_noise += random.uniform(0.2, 0.6)

        if current_date.weekday() in TRAINING_DAYS:
            daily_noise -= random.uniform(0.1, 0.3)

        if 35 <= day <= 42:
            expected_weight += 0.3

        current_weight = expected_weight + daily_noise
        weights.append(round(current_weight, 1))

    return weights


def generate_skinfold_trajectory():
    """Generate weekly skinfold measurements"""
    skinfolds = []
    start_sum = 80.0

    for week in range(13):
        current_sum = start_sum - (week * 2.0)
        current_sum += random.uniform(-0.5, 0.5)

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
    """Generate realistic nutrition intake"""
    if random.random() < 0.20:
        return None

    if is_weekend:
        calorie_multiplier = random.uniform(1.10, 1.20)
    else:
        calorie_multiplier = random.uniform(0.90, 1.05)

    calories = TARGET_CALORIES * calorie_multiplier
    protein = TARGET_PROTEIN * random.uniform(0.95, 1.05)
    fats = TARGET_FATS * random.uniform(0.90, 1.10)

    remaining_cals = calories - (protein * 4) - (fats * 9)
    carbs = remaining_cals / 4

    return {
        'calories': round(calories),
        'protein': round(protein, 1),
        'carbs': round(carbs, 1),
        'fats': round(fats, 1)
    }


def generate_workout_log(current_date, workout_number):
    """Generate a realistic workout log"""
    workout_names = ["Upper Body A", "Lower Body A", "Upper Body B", "Lower Body B"]
    workout_name = workout_names[workout_number % 4]

    # Upper body exercises
    upper_exercises = [
        {"name": "Bench Press", "muscle_group": "chest"},
        {"name": "Bent Over Row", "muscle_group": "back"},
        {"name": "Overhead Press", "muscle_group": "shoulders"},
        {"name": "Pull-ups", "muscle_group": "back"},
        {"name": "Dips", "muscle_group": "triceps"}
    ]

    # Lower body exercises
    lower_exercises = [
        {"name": "Squat", "muscle_group": "legs"},
        {"name": "Romanian Deadlift", "muscle_group": "hamstrings"},
        {"name": "Leg Press", "muscle_group": "legs"},
        {"name": "Leg Curl", "muscle_group": "hamstrings"},
        {"name": "Calf Raises", "muscle_group": "calves"}
    ]

    if "Upper" in workout_name:
        exercises = random.sample(upper_exercises, 4)
    else:
        exercises = random.sample(lower_exercises, 4)

    workout_exercises = []
    for exercise in exercises:
        num_sets = random.randint(3, 4)
        sets = []

        base_weight = random.uniform(60, 120)
        for set_num in range(num_sets):
            sets.append({
                "reps": random.randint(6, 12),
                "weight": round(base_weight + random.uniform(-5, 5), 1),
                "rpe": round(random.uniform(6.5, 9.0), 1)
            })

        workout_exercises.append({
            "name": exercise["name"],
            "sets": sets
        })

    return {
        "id": str(uuid.uuid4()),
        "user_id": TEST_USER_ID,
        "date": current_date.isoformat(),
        "workout_name": workout_name,
        "exercises": workout_exercises,
        "duration_minutes": random.randint(45, 75),
        "notes": None,
        "completed": True,
        "created_at": datetime.now().isoformat()
    }


def main():
    print("🏋️ Inserting 90-day sample data into DynamoDB...")
    print(f"User: {TEST_USER_ID}")
    print(f"Period: {START_DATE} to {END_DATE}")
    print(f"Region: {REGION}\n")

    # Initialize DynamoDB client
    dynamodb = boto3.resource('dynamodb', region_name=REGION)

    # Get table references
    tables = {
        'user_profiles': dynamodb.Table(f"{TABLE_PREFIX}-user_profiles"),
        'body_logs': dynamodb.Table(f"{TABLE_PREFIX}-body_logs"),
        'nutrition_logs': dynamodb.Table(f"{TABLE_PREFIX}-nutrition_logs"),
        'workout_logs': dynamodb.Table(f"{TABLE_PREFIX}-workout_logs"),
        'daily_summaries': dynamodb.Table(f"{TABLE_PREFIX}-daily_summaries"),
        'user_exercises': dynamodb.Table(f"{TABLE_PREFIX}-user_exercises"),
    }

    # Generate trajectories
    print("📊 Generating data trajectories...")
    weights = generate_weight_trajectory()
    skinfolds = generate_skinfold_trajectory()

    # 1. Insert User Profile
    print("\n👤 Inserting user profile...")
    user_profile = python_to_dynamodb({
        "user_id": TEST_USER_ID,
        "name": "Demo User",
        "age": 30,
        "sex": "male",
        "height_cm": 180,
        "body_weight_kg": START_WEIGHT,
        "body_fat_pct": START_BODY_FAT,
        "goal": "lose_weight",
        "training_status": "intermediate",
        "target_calories": TARGET_CALORIES,
        "target_protein": TARGET_PROTEIN,
        "target_carbs": TARGET_CARBS,
        "target_fats": TARGET_FATS,
        "bmr": 1850.0,
        "tdee": 2640.0,
        "activity_level": 1.4,
        "is_active": True,
        "communication_style": "encouraging",
        "language": "en",
        "timezone": "UTC",
        "created_at": START_DATE.isoformat(),
        "updated_at": datetime.now().isoformat()
    })

    tables['user_profiles'].put_item(Item=user_profile)
    print("  ✅ User profile inserted")

    # 2. Insert Exercise Configurations
    print("\n🏋️ Inserting exercise configurations...")

    exercise_configs = [
        # Main Compound Lifts - Linear Progressive
        {"exercise_name": "Bench Press", "progression_model": "linear", "rep_target": 8, "num_sets": 4,
         "available_increments": [1.25, 2.5, 5.0], "selected_increment": 2.5,
         "current_weight": 80.0, "last_successful_weight": 77.5, "exercise_type": "compound"},

        {"exercise_name": "Squat", "progression_model": "linear", "rep_target": 8, "num_sets": 4,
         "available_increments": [2.5, 5.0], "selected_increment": 5.0,
         "current_weight": 100.0, "last_successful_weight": 95.0, "exercise_type": "compound"},

        {"exercise_name": "Romanian Deadlift", "progression_model": "rep_range", "rep_target": 10, "num_sets": 3,
         "available_increments": [2.5, 5.0], "selected_increment": 5.0,
         "current_weight": 90.0, "last_successful_weight": 85.0, "exercise_type": "compound"},

        {"exercise_name": "Overhead Press", "progression_model": "rep_range", "rep_target": 8, "num_sets": 3,
         "available_increments": [1.25, 2.5], "selected_increment": 1.25,
         "current_weight": 50.0, "last_successful_weight": 48.75, "exercise_type": "compound"},

        # Accessory Exercises - Rep Range
        {"exercise_name": "Bent Over Row", "progression_model": "rep_range", "rep_target": 10, "num_sets": 3,
         "available_increments": [2.5, 5.0], "selected_increment": 2.5,
         "current_weight": 70.0, "last_successful_weight": 67.5, "exercise_type": "compound"},

        {"exercise_name": "Pull-ups", "progression_model": "rep_range", "rep_target": 12, "num_sets": 3,
         "available_increments": [0, 2.5, 5.0], "selected_increment": 2.5,
         "current_weight": 0.0, "last_successful_weight": 0.0, "exercise_type": "compound"},

        {"exercise_name": "Dips", "progression_model": "rep_range", "rep_target": 12, "num_sets": 3,
         "available_increments": [0, 2.5, 5.0], "selected_increment": 2.5,
         "current_weight": 0.0, "last_successful_weight": 0.0, "exercise_type": "compound"},

        {"exercise_name": "Leg Press", "progression_model": "rep_range", "rep_target": 12, "num_sets": 3,
         "available_increments": [5.0, 10.0], "selected_increment": 10.0,
         "current_weight": 150.0, "last_successful_weight": 140.0, "exercise_type": "compound"},

        {"exercise_name": "Leg Curl", "progression_model": "rep_range", "rep_target": 12, "num_sets": 3,
         "available_increments": [2.5, 5.0], "selected_increment": 2.5,
         "current_weight": 45.0, "last_successful_weight": 42.5, "exercise_type": "isolation"},

        {"exercise_name": "Calf Raises", "progression_model": "rep_range", "rep_target": 15, "num_sets": 3,
         "available_increments": [5.0, 10.0], "selected_increment": 5.0,
         "current_weight": 80.0, "last_successful_weight": 75.0, "exercise_type": "isolation"},
    ]

    for config in exercise_configs:
        next_session = {
            "weight": config['current_weight'],
            "target_reps": config['rep_target'],
            "action": "baseline",
            "message": f"Start with {config['current_weight']}kg x {config['rep_target']} reps",
            "reasoning": "Initial session - establishing baseline"
        }

        exercise_data = python_to_dynamodb({
            "id": str(uuid.uuid4()),
            "user_id": TEST_USER_ID,
            "exercise_name": config['exercise_name'],
            "progression_model": config['progression_model'],
            "rep_target": config['rep_target'],
            "num_sets": config['num_sets'],
            "available_increments": config['available_increments'],
            "selected_increment": config['selected_increment'],
            "current_weight": config['current_weight'],
            "last_successful_weight": config['last_successful_weight'],
            "plateau_count": 0,
            "next_session": next_session,
            "exercise_type": config['exercise_type'],
            "created_at": datetime.now().isoformat(),
            "updated_at": datetime.now().isoformat()
        })

        tables['user_exercises'].put_item(Item=exercise_data)

    print(f"  ✅ {len(exercise_configs)} exercises configured")

    # Counters
    body_logs_count = 0
    nutrition_logs_count = 0
    workout_logs_count = 0
    daily_summaries_count = 0
    workout_number = 0

    # 2. Insert daily data
    print("\n📅 Inserting daily logs (this may take a minute)...")

    for day in range(91):
        current_date = START_DATE + timedelta(days=day)
        is_weekend = current_date.weekday() in [5, 6]
        week_index = day // 7

        # Progress indicator
        if day % 10 == 0:
            print(f"  Processing day {day + 1}/91...")

        # Body log (daily weight)
        body_log = {
            "id": str(uuid.uuid4()),
            "user_id": TEST_USER_ID,
            "date": current_date.isoformat(),
            "weight": weights[day],
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

        body_log["created_at"] = datetime.now().isoformat()
        tables['body_logs'].put_item(Item=python_to_dynamodb(body_log))
        body_logs_count += 1

        # Nutrition logs
        nutrition = generate_daily_nutrition(day, is_weekend)
        day_nutrition_total = {'calories': 0, 'protein': 0, 'carbs': 0, 'fats': 0}

        if nutrition:
            num_meals = random.randint(2, 3)

            for meal_idx in range(num_meals):
                meal_types = ['breakfast', 'lunch', 'dinner', 'snack']
                meal_type = meal_types[min(meal_idx, 2)]

                if num_meals == 2:
                    pct = 0.5
                else:
                    pct = [0.25, 0.35, 0.40][meal_idx]

                meal_cals = nutrition['calories'] * pct
                meal_protein = nutrition['protein'] * pct
                meal_carbs = nutrition['carbs'] * pct
                meal_fats = nutrition['fats'] * pct

                meal_times = [time(8, 0), time(12, 30), time(18, 30)]
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
                            "name": f"{meal_type.capitalize()} meal",
                            "amount": "1 serving",
                            "calories": round(meal_cals),
                            "protein": round(meal_protein, 1),
                            "carbs": round(meal_carbs, 1),
                            "fats": round(meal_fats, 1)
                        }
                    ],
                    "created_at": datetime.now().isoformat()
                }

                tables['nutrition_logs'].put_item(Item=python_to_dynamodb(nutrition_log))
                nutrition_logs_count += 1

                day_nutrition_total['calories'] += meal_cals
                day_nutrition_total['protein'] += meal_protein
                day_nutrition_total['carbs'] += meal_carbs
                day_nutrition_total['fats'] += meal_fats

        # Workout log
        workout_completed = 0
        if current_date.weekday() in TRAINING_DAYS and random.random() > 0.10:
            workout_log = generate_workout_log(current_date, workout_number)
            tables['workout_logs'].put_item(Item=python_to_dynamodb(workout_log))
            workout_logs_count += 1
            workout_completed = 1
            workout_number += 1

        # Daily summary
        daily_summary = {
            "id": str(uuid.uuid4()),
            "user_id": TEST_USER_ID,
            "date": current_date.isoformat(),
            "total_calories": round(day_nutrition_total['calories']),
            "total_protein": round(day_nutrition_total['protein'], 1),
            "total_carbs": round(day_nutrition_total['carbs'], 1),
            "total_fats": round(day_nutrition_total['fats'], 1),
            "workouts_completed": workout_completed,
            "weight": weights[day],
            "created_at": datetime.now().isoformat(),
            "updated_at": datetime.now().isoformat()
        }

        tables['daily_summaries'].put_item(Item=python_to_dynamodb(daily_summary))
        daily_summaries_count += 1

    # Generate training progress summary (so chatbot can answer training questions)
    print("\n📈 Generating training progress summary...")
    training_summary = {
        "id": str(uuid.uuid4()),
        "user_id": TEST_USER_ID,
        "week": f"{END_DATE.year}-W{END_DATE.isocalendar()[1]:02d}",
        "published_by": "training_agent",
        "published_at": datetime.now().isoformat(),
        "overall_strength_trend": "stable",
        "exercises_analyzed": len(exercise_configs),
        "exercises_progressing": 2,
        "exercises_plateaued": len(exercise_configs) - 2,
        "exercises_regressing": 0,
        "avg_weekly_volume_kg": 85000.0,
        "trend_confidence": 1.0,
        "days_of_data": 14,
        "workouts_completed": 7,
        "data_quality": "good"
    }
    tables['training_progress_summaries'].put_item(Item=python_to_dynamodb(training_summary))
    print("  ✅ Training progress summary generated")

    # Final stats
    final_weight = weights[-1]
    weight_loss = START_WEIGHT - final_weight

    print("\n✅ Sample data inserted successfully!\n")
    print("📊 Summary:")
    print(f"  • User profile: 1")
    print(f"  • Exercise configurations: {len(exercise_configs)}")
    print(f"  • Body logs: {body_logs_count}")
    print(f"  • Nutrition logs: {nutrition_logs_count}")
    print(f"  • Workout logs: {workout_logs_count}")
    print(f"  • Daily summaries: {daily_summaries_count}")
    print(f"  • Training progress summaries: 1")
    print(f"\n  • Starting weight: {START_WEIGHT}kg")
    print(f"  • Final weight: {final_weight}kg")
    print(f"  • Total loss: {weight_loss:.1f}kg ({(weight_loss/START_WEIGHT)*100:.1f}%)\n")
    print(f"🔑 Test User ID: {TEST_USER_ID}")
    print(f"🌐 CloudFront URL: https://d18dmr2jorio01.cloudfront.net")
    print(f"\n🚀 Next steps:")
    print(f"  1. Visit your app at the CloudFront URL")
    print(f"  2. Set localStorage: localStorage.setItem('fit_tracker_user_id', '{TEST_USER_ID}')")
    print(f"  3. Test the nutrition and training analyzers with 90 days of data!")
    print(f"  4. Training analyzer now has exercise configs for proper analysis!")


if __name__ == "__main__":
    main()
