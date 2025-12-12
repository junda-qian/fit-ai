"""
Generate realistic 90-day demo data for test_user_90day

This script creates comprehensive fitness tracking data that mimics a real user:
- Progressive workout performance
- Realistic nutrition adherence patterns
- Gradual body composition changes
- Complete daily summaries

Run this script anytime to refresh demo data to the most recent 90 days.
"""

import sys
import os
import random
import uuid
from datetime import datetime, date, timedelta

# Add backend to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'backend'))

from database import JSONDatabase


class DemoDataGenerator:
    """Generate realistic 90-day fitness tracking data"""

    def __init__(self):
        self.db = JSONDatabase()
        self.user_id = "demo_user_90day"
        self.today = date.today()
        self.start_date = self.today - timedelta(days=89)  # 90 days total

        # User profile constants
        self.initial_weight = 85.0  # kg
        self.height = 178  # cm
        self.age = 28
        self.gender = "male"
        self.goal = "build_muscle"

        # Nutrition targets
        self.target_calories = 2200
        self.target_protein = 170
        self.target_carbs = 220
        self.target_fats = 73

    def generate_all(self):
        """Generate all demo data"""
        print(f"🚀 Generating 90-day demo data for {self.user_id}")
        print(f"   Date range: {self.start_date} to {self.today}\n")

        # Clear existing data
        self._clear_existing_data()

        # Generate fresh data
        self._create_user_profile()
        self._generate_body_logs()
        self._generate_workout_logs()
        self._generate_user_exercises()  # Must come after workout logs
        self._generate_nutrition_logs()
        self._generate_daily_summaries()

        print("\n" + "=" * 60)
        print("✅ Demo data generation complete!")
        print("=" * 60)
        print(f"\n90 days of realistic data from {self.start_date} to {self.today}")
        print("Ready for testing Coach Orchestrator and Progress tracking!")

    def _clear_existing_data(self):
        """Remove existing test_user_90day data"""
        print("1. Clearing existing data...")

        collections = ["user_profiles", "daily_summaries", "nutrition_logs",
                      "body_logs", "workout_logs", "user_exercises"]

        for collection in collections:
            count = self.db.delete(collection, {"user_id": self.user_id})
            if count > 0:
                print(f"   Removed {count} {collection}")

    def _create_user_profile(self):
        """Create user profile"""
        print("\n2. Creating user profile...")

        profile = {
            "id": str(uuid.uuid4()),
            "user_id": self.user_id,
            "age": self.age,
            "gender": self.gender,
            "height_cm": self.height,
            "weight_kg": self.initial_weight,
            "goal": self.goal,
            "activity_level": "moderate",
            "target_calories": self.target_calories,
            "target_protein": self.target_protein,
            "target_carbs": self.target_carbs,
            "target_fats": self.target_fats,
            "created_at": self.start_date.isoformat()
        }

        self.db.insert("user_profiles", profile)
        print(f"   ✅ Profile: {self.age}y {self.gender}, {self.initial_weight}kg, Goal: {self.goal}")

    def _generate_body_logs(self):
        """Generate daily body composition logs with gradual muscle gain"""
        print("\n3. Generating body logs...")

        body_logs = []

        # Daily weigh-ins (90 total)
        for day in range(90):
            log_date = self.start_date + timedelta(days=day)

            # Overall trend: +0.02kg per day (lean muscle gain = +1.8kg over 90 days)
            trend_weight = self.initial_weight + (day * 0.02)

            # Add realistic daily fluctuations (water retention, food volume, etc.)
            daily_variance = random.uniform(-0.2, 0.3)
            weight = trend_weight + daily_variance

            # Body fat slowly decreasing (body recomp)
            # Overall decrease: -1.2% over 90 days
            body_fat_pct = 20.0 - (day * 0.0133)

            # Skinfold sum decreasing (fat loss indicator)
            skinfold_sum = 120.0 - (day * 0.17)

            # Calculate individual skinfolds (decreasing over time)
            log = {
                "id": str(uuid.uuid4()),
                "user_id": self.user_id,
                "date": log_date.isoformat(),
                "weight": round(weight, 1),
                "body_fat_pct": round(body_fat_pct, 1),
                "skinfold_sum": round(skinfold_sum, 1),
                "skinfolds": {
                    "chest": round(15 - day * 0.03, 1),
                    "abdomen": round(25 - day * 0.04, 1),
                    "thigh": round(20 - day * 0.03, 1),
                    "tricep": round(12 - day * 0.02, 1),
                    "subscapular": round(18 - day * 0.03, 1),
                    "suprailiac": round(20 - day * 0.035, 1),
                    "midaxillary": round(15 - day * 0.03, 1)
                },
                "logged_at": f"{log_date}T07:00:00Z",
                "created_at": f"{log_date}T07:00:00Z"
            }

            body_logs.append(log)
            self.db.insert("body_logs", log)

        final_weight = round(self.initial_weight + (89 * 0.02), 1)
        final_body_fat = round(20.0 - (89 * 0.0133), 1)

        print(f"   ✅ Generated {len(body_logs)} daily body logs")
        print(f"      Weight: {self.initial_weight}kg → {final_weight}kg (+{round(final_weight - self.initial_weight, 1)}kg)")
        print(f"      Body fat: 20.0% → {final_body_fat}% (-{round(20.0 - final_body_fat, 1)}%)")

    def _generate_workout_logs(self):
        """Generate comprehensive workout logs (4-5x per week with progressive overload)"""
        print("\n4. Generating workout logs...")

        workout_logs = []

        # Workout schedule: Mon, Tue, Thu, Fri, Sat (4-5x per week)
        workout_days = [0, 1, 3, 4, 5]  # Monday = 0

        # Comprehensive exercise library with progressive overload
        # Main compound lifts
        main_lifts = {
            "Squat": {"start_weight": 80, "progression": 1.5, "type": "legs"},
            "Bench Press": {"start_weight": 70, "progression": 1.0, "type": "push"},
            "Deadlift": {"start_weight": 100, "progression": 2.0, "type": "pull"},
            "Overhead Press": {"start_weight": 45, "progression": 0.5, "type": "push"},
            "Barbell Row": {"start_weight": 65, "progression": 1.0, "type": "pull"},
            "Romanian Deadlift": {"start_weight": 70, "progression": 1.2, "type": "legs"},
        }

        # Accessory exercises
        accessories = {
            "Lat Pulldown": {"start_weight": 50, "progression": 0.8, "type": "pull"},
            "Dumbbell Press": {"start_weight": 25, "progression": 0.5, "type": "push"},
            "Leg Press": {"start_weight": 120, "progression": 2.5, "type": "legs"},
            "Cable Row": {"start_weight": 45, "progression": 0.7, "type": "pull"},
            "Dumbbell Curl": {"start_weight": 12, "progression": 0.3, "type": "pull"},
            "Tricep Extension": {"start_weight": 20, "progression": 0.4, "type": "push"},
            "Leg Curl": {"start_weight": 35, "progression": 0.6, "type": "legs"},
            "Lateral Raise": {"start_weight": 8, "progression": 0.2, "type": "push"},
        }

        # Training splits
        splits = {
            "push": ["Bench Press", "Overhead Press", "Dumbbell Press", "Tricep Extension", "Lateral Raise"],
            "pull": ["Deadlift", "Barbell Row", "Lat Pulldown", "Cable Row", "Dumbbell Curl"],
            "legs": ["Squat", "Romanian Deadlift", "Leg Press", "Leg Curl"],
        }

        current_date = self.start_date
        week = 0
        split_rotation = ["push", "pull", "legs", "push", "pull"]  # 5-day rotation

        while current_date <= self.today:
            # Rarely skip a week (1% chance - deload or vacation)
            if random.random() < 0.01:
                current_date += timedelta(days=7)
                week += 1
                continue

            # Workout 4-5x this week
            num_workouts = random.choice([4, 5, 5])  # weighted toward 5
            days_this_week = random.sample(workout_days, k=num_workouts)

            for workout_idx, day_offset in enumerate(sorted(days_this_week)):
                workout_date = current_date + timedelta(days=day_offset)

                if workout_date > self.today:
                    break

                # Determine split for this workout
                split_type = split_rotation[workout_idx % len(split_rotation)]
                available_exercises = splits[split_type]

                # Select 3-5 exercises from this split
                num_exercises = random.choice([3, 4, 4, 5])
                selected_exercises = random.sample(available_exercises, k=min(num_exercises, len(available_exercises)))

                workout_exercises = []
                for ex_name in selected_exercises:
                    # Get exercise data from main lifts or accessories
                    if ex_name in main_lifts:
                        base = main_lifts[ex_name]
                        is_main_lift = True
                    else:
                        base = accessories[ex_name]
                        is_main_lift = False

                    # Progressive overload: increase weight each week
                    current_weight = base["start_weight"] + (week * base["progression"])

                    # Main lifts: 4-5 sets, 5-8 reps (heavier)
                    # Accessories: 3-4 sets, 8-12 reps (lighter)
                    if is_main_lift:
                        num_sets = random.choice([4, 5])
                        rep_range = (5, 8)
                    else:
                        num_sets = random.choice([3, 4])
                        rep_range = (8, 12)

                    sets = []
                    for set_num in range(num_sets):
                        reps = random.randint(*rep_range)
                        # Fatigue: later sets might be slightly lighter
                        weight_reduction = set_num * random.choice([0, 2.5]) if is_main_lift else set_num * random.choice([0, 1.25])
                        weight = max(current_weight - weight_reduction, base["start_weight"] * 0.7)
                        sets.append({"reps": reps, "weight_kg": round(weight, 1)})

                    workout_exercises.append({
                        "name": ex_name,
                        "sets": sets
                    })

                log = {
                    "id": str(uuid.uuid4()),
                    "user_id": self.user_id,
                    "date": workout_date.isoformat(),
                    "workout_type": "strength",
                    "duration_minutes": random.randint(60, 90),
                    "exercises": workout_exercises,
                    "notes": f"{split_type.title()} day",
                    "timestamp": f"{workout_date}T18:00:00Z",
                    "created_at": f"{workout_date}T18:00:00Z"
                }

                workout_logs.append(log)
                self.db.insert("workout_logs", log)

            current_date += timedelta(days=7)
            week += 1

        # Calculate progression stats
        first_workout = workout_logs[0] if workout_logs else None
        last_workout = workout_logs[-1] if workout_logs else None

        print(f"   ✅ Generated {len(workout_logs)} workout logs (~{len(workout_logs)/13:.1f}x per week)")
        if first_workout and last_workout:
            print(f"      Date range: {first_workout['date']} to {last_workout['date']}")
            print(f"      Total exercises tracked: {sum(len(w['exercises']) for w in workout_logs)}")
            print(f"      Progressive overload applied across 14 exercises")

    def _generate_user_exercises(self):
        """Generate user exercise configurations based on workout logs"""
        print("\n5. Generating user exercise configurations...")

        # Get all workout logs for this user
        workout_logs = self.db.find("workout_logs", {"user_id": self.user_id})

        # Collect unique exercises
        unique_exercises = {}
        for log in workout_logs:
            for exercise in log.get("exercises", []):
                ex_name = exercise["name"]
                if ex_name not in unique_exercises:
                    # Analyze sets/reps from this exercise
                    sets = exercise.get("sets", [])
                    if sets:
                        avg_reps = sum(s["reps"] for s in sets) / len(sets)
                        num_sets = len(sets)
                        unique_exercises[ex_name] = {
                            "avg_reps": avg_reps,
                            "num_sets": num_sets
                        }

        # Main lifts use lower reps (strength), accessories use higher reps (hypertrophy)
        main_lifts = ["Squat", "Bench Press", "Deadlift", "Overhead Press", "Barbell Row", "Romanian Deadlift"]

        user_exercises = []
        for exercise_name, stats in unique_exercises.items():
            is_main_lift = exercise_name in main_lifts

            # Rep targets: main lifts 5-8, accessories 8-12
            rep_target = 6 if is_main_lift else 10

            config = {
                "id": str(uuid.uuid4()),
                "user_id": self.user_id,
                "exercise_name": exercise_name,
                "progression_model": "linear",
                "rep_target": rep_target,
                "num_sets": stats["num_sets"],
                "available_increments": [1.25, 2.5, 5.0],
                "selected_increment": 2.5 if is_main_lift else 1.25,
                "last_successful_weight": 0,
                "current_weight": 0,
                "created_at": self.start_date.isoformat(),
            }

            user_exercises.append(config)
            self.db.insert("user_exercises", config)

        print(f"   ✅ Generated {len(user_exercises)} exercise configurations")
        print(f"      Main lifts: {len([e for e in user_exercises if e['exercise_name'] in main_lifts])}")
        print(f"      Accessories: {len([e for e in user_exercises if e['exercise_name'] not in main_lifts])}")

    def _generate_nutrition_logs(self):
        """Generate realistic nutrition logs with high adherence"""
        print("\n6. Generating nutrition logs...")

        nutrition_logs = []

        meals = ["breakfast", "lunch", "dinner", "snack"]

        for day_offset in range(90):
            log_date = self.start_date + timedelta(days=day_offset)

            # 95% adherence: log almost all days
            if random.random() < 0.05:
                continue

            # Number of meals logged: 3-4 per day (more consistent)
            num_meals = random.choice([3, 3, 3, 4])  # heavily weighted toward 3-4

            daily_meals = random.sample(meals, k=num_meals)

            for meal_type in daily_meals:
                # Calories per meal vary but sum close to target
                base_cals = self.target_calories / 3.5

                # Weekend might have higher variance
                if log_date.weekday() >= 5:
                    variance = 0.3
                else:
                    variance = 0.15

                calories = int(base_cals * random.uniform(1 - variance, 1 + variance))

                # Macros roughly aligned with targets
                protein = int(calories * 0.30 / 4)  # 30% protein
                carbs = int(calories * 0.45 / 4)    # 45% carbs
                fats = int(calories * 0.25 / 9)     # 25% fats

                meal_times = {
                    "breakfast": "08:00:00",
                    "lunch": "12:30:00",
                    "dinner": "18:30:00",
                    "snack": "15:00:00"
                }

                log = {
                    "id": str(uuid.uuid4()),
                    "user_id": self.user_id,
                    "date": log_date.isoformat(),
                    "meal_type": meal_type,
                    "time": meal_times[meal_type],
                    "calories": calories,
                    "protein": protein,
                    "carbs": carbs,
                    "fats": fats,
                    "food_items": [{
                        "name": f"{meal_type.title()} foods",
                        "amount": "1 serving",
                        "calories": calories,
                        "protein": protein,
                        "carbs": carbs,
                        "fats": fats,
                        "fdc_id": None
                    }],
                    "notes": None,
                    "created_at": f"{log_date}T{meal_times[meal_type]}Z",
                    "logged_at": f"{log_date}T{meal_times[meal_type]}Z"
                }

                nutrition_logs.append(log)
                self.db.insert("nutrition_logs", log)

        print(f"   ✅ Generated {len(nutrition_logs)} nutrition logs (~95% adherence, 3-4 meals/day)")

    def _generate_daily_summaries(self):
        """Generate daily summaries aggregating nutrition and workouts"""
        print("\n7. Generating daily summaries...")

        summaries = []

        for day_offset in range(90):
            summary_date = self.start_date + timedelta(days=day_offset)

            # Get nutrition for this day
            day_nutrition = [
                log for log in self.db.find("nutrition_logs", {"user_id": self.user_id})
                if log.get("date") == summary_date.isoformat()
            ]

            total_calories = sum(log.get("calories", 0) for log in day_nutrition)
            total_protein = sum(log.get("protein", 0) for log in day_nutrition)
            total_carbs = sum(log.get("carbs", 0) for log in day_nutrition)
            total_fats = sum(log.get("fats", 0) for log in day_nutrition)

            # Get workouts for this day
            day_workouts = [
                log for log in self.db.find("workout_logs", {"user_id": self.user_id})
                if log.get("date") == summary_date.isoformat()
            ]

            workouts_completed = len(day_workouts)

            # Get nearest body weight (for reference)
            all_body_logs = sorted(
                [log for log in self.db.find("body_logs", {"user_id": self.user_id})
                 if datetime.fromisoformat(log["date"]).date() <= summary_date],
                key=lambda x: x["date"],
                reverse=True
            )

            weight = all_body_logs[0]["weight"] if all_body_logs else self.initial_weight

            summary = {
                "id": str(uuid.uuid4()),
                "user_id": self.user_id,
                "date": summary_date.isoformat(),
                "total_calories": total_calories,
                "total_protein": total_protein,
                "total_carbs": total_carbs,
                "total_fats": total_fats,
                "workouts_completed": workouts_completed,
                "weight": weight,
                "created_at": f"{summary_date}T23:59:59Z",
                "updated_at": f"{summary_date}T23:59:59Z"
            }

            summaries.append(summary)
            self.db.insert("daily_summaries", summary)

        print(f"   ✅ Generated {len(summaries)} daily summaries")


if __name__ == "__main__":
    generator = DemoDataGenerator()
    generator.generate_all()
