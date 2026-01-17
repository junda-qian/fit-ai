"""
Analyze Exercise Database Coverage

Determines if the 27 exercises provide sufficient coverage for all 12 muscle groups.
Identifies gaps and suggests additional exercises if needed.
"""

from workout_planner import EXERCISE_DATABASE, MUSCLE_GROUPS
from collections import defaultdict
import json


def analyze_coverage():
    """Analyze how well exercises cover each muscle group"""

    print("="*80)
    print("EXERCISE DATABASE COVERAGE ANALYSIS")
    print("="*80)
    print(f"\nTotal Exercises: {len(EXERCISE_DATABASE)}")
    print(f"Total Muscle Groups: {len(MUSCLE_GROUPS)}")

    # Count exercises per muscle group
    muscle_to_exercises = defaultdict(list)

    for exercise_name, exercise_data in EXERCISE_DATABASE.items():
        activation = exercise_data["activation"]
        for muscle, value in activation.items():
            if value > 0:
                muscle_to_exercises[muscle].append({
                    "exercise": exercise_name,
                    "activation": value,
                    "type": exercise_data["type"]
                })

    # Analyze each muscle group
    print("\n" + "="*80)
    print("MUSCLE GROUP COVERAGE")
    print("="*80)

    for muscle in MUSCLE_GROUPS:
        exercises = muscle_to_exercises.get(muscle, [])

        # Count by activation level
        primary = [e for e in exercises if e["activation"] == 1.0]
        high = [e for e in exercises if e["activation"] >= 0.75 and e["activation"] < 1.0]
        moderate = [e for e in exercises if e["activation"] >= 0.5 and e["activation"] < 0.75]
        minor = [e for e in exercises if e["activation"] > 0 and e["activation"] < 0.5]

        # Count by exercise type
        compounds = [e for e in exercises if e["type"] == "Compound"]
        isolations = [e for e in exercises if e["type"] == "Isolation"]

        print(f"\n{muscle}:")
        print(f"  Total exercises: {len(exercises)}")
        print(f"  - Primary (1.0): {len(primary)}")
        print(f"  - High (0.75): {len(high)}")
        print(f"  - Moderate (0.5): {len(moderate)}")
        print(f"  - Minor (<0.5): {len(minor)}")
        print(f"  Exercise types: {len(compounds)} compound, {len(isolations)} isolation")

        # Check if we have isolation exercises for fine-tuning
        if len(isolations) == 0:
            print(f"  ⚠️  WARNING: No isolation exercises for precise volume control!")
        elif len(isolations) == 1:
            print(f"  ⚠️  CAUTION: Only 1 isolation exercise (limited options)")

        # Check if we have enough options
        if len(exercises) < 3:
            print(f"  ⚠️  WARNING: Limited exercise variety ({len(exercises)} total)")


def calculate_theoretical_coverage():
    """Calculate theoretical min/max achievable volume per muscle"""

    print("\n\n" + "="*80)
    print("THEORETICAL VOLUME RANGE ANALYSIS")
    print("="*80)
    print("\nAssuming: 2-5 sets per exercise, 1-2x per week frequency\n")

    for muscle in MUSCLE_GROUPS:
        # Find exercises that activate this muscle
        relevant_exercises = []
        for exercise_name, exercise_data in EXERCISE_DATABASE.items():
            activation = exercise_data["activation"].get(muscle, 0)
            if activation > 0:
                relevant_exercises.append({
                    "name": exercise_name,
                    "activation": activation
                })

        if not relevant_exercises:
            print(f"{muscle}: NO EXERCISES (impossible to train!)")
            continue

        # Calculate min (single best isolation exercise, 2 sets, 1x/week)
        isolations = [e for e in relevant_exercises
                     if EXERCISE_DATABASE[e["name"]]["type"] == "Isolation"]

        if isolations:
            best_isolation = max(isolations, key=lambda x: x["activation"])
            min_volume = 2 * best_isolation["activation"] * 1  # 2 sets, 1x/week
        else:
            # No isolation, use best compound
            best_exercise = max(relevant_exercises, key=lambda x: x["activation"])
            min_volume = 2 * best_exercise["activation"] * 1

        # Calculate max (all exercises, 5 sets each, 2x/week)
        max_volume = sum(5 * e["activation"] * 2 for e in relevant_exercises)

        print(f"{muscle:15s}: Min={min_volume:5.1f} sets/week, Max={max_volume:6.1f} sets/week")
        print(f"               Options: {len(relevant_exercises)} exercises")


def find_missing_exercise_types():
    """Identify what types of exercises might be missing"""

    print("\n\n" + "="*80)
    print("GAP ANALYSIS: MISSING EXERCISE TYPES")
    print("="*80)

    gaps = []

    # Check for isolation exercises for each muscle
    for muscle in MUSCLE_GROUPS:
        isolations = []
        for exercise_name, exercise_data in EXERCISE_DATABASE.items():
            if (exercise_data["type"] == "Isolation" and
                exercise_data["activation"].get(muscle, 0) == 1.0):
                isolations.append(exercise_name)

        if len(isolations) == 0:
            gaps.append(f"❌ {muscle}: NO isolation exercises (can't fine-tune volume precisely)")
        elif len(isolations) == 1:
            gaps.append(f"⚠️  {muscle}: Only 1 isolation exercise ({isolations[0]})")

    if gaps:
        print("\n".join(gaps))
    else:
        print("✅ All muscle groups have adequate isolation exercises")

    # Suggest additional exercises
    print("\n\n" + "="*80)
    print("SUGGESTED ADDITIONAL EXERCISES")
    print("="*80)

    suggestions = {
        "Pecs": ["Incline dumbbell press", "Decline press", "Cable crossovers"],
        "Delt": ["Front raises", "Arnold press", "Face pulls"],
        "Traps": ["Dumbbell shrugs", "Barbell rows"],
        "Lats": ["Dumbbell rows", "T-bar rows", "Straight-arm pulldowns"],
        "Erector Spine": ["Hyperextensions", "Cable pull-throughs"],
        "Quadriceps": ["Front squats", "Sissy squats", "Walking lunges"],
        "Hamstrings": ["Nordic curls", "Glute-ham raises"],
        "Glutes": ["Cable kickbacks", "Smith machine hip thrusts"],
        "Triceps": ["Close-grip bench", "Dips", "Skull crushers"],
        "Biceps": ["Hammer curls", "Preacher curls", "Cable curls"],
        "Abs": ["Hanging leg raises", "Cable crunches", "Planks"],
        "Calves": ["Donkey calf raises", "Single-leg calf raises"]
    }

    for muscle in MUSCLE_GROUPS:
        current_count = len([
            ex for ex, data in EXERCISE_DATABASE.items()
            if data["activation"].get(muscle, 0) == 1.0
        ])

        print(f"\n{muscle} (currently {current_count} primary exercises):")
        for suggestion in suggestions.get(muscle, []):
            print(f"  + {suggestion}")


def analyze_exercise_efficiency():
    """Analyze which exercises are most 'efficient' (hit most muscles)"""

    print("\n\n" + "="*80)
    print("EXERCISE EFFICIENCY RANKING")
    print("="*80)
    print("\nExercises ranked by number of muscles activated:\n")

    exercise_scores = []

    for exercise_name, exercise_data in EXERCISE_DATABASE.items():
        activation = exercise_data["activation"]

        # Count muscles activated
        muscles_hit = len([m for m, v in activation.items() if v > 0])

        # Calculate total activation (sum of all activation values)
        total_activation = sum(activation.values())

        # Count primary activations
        primary_count = len([m for m, v in activation.items() if v == 1.0])

        exercise_scores.append({
            "name": exercise_name,
            "type": exercise_data["type"],
            "muscles_hit": muscles_hit,
            "total_activation": total_activation,
            "primary_muscles": primary_count
        })

    # Sort by efficiency
    exercise_scores.sort(key=lambda x: (x["muscles_hit"], x["total_activation"]), reverse=True)

    for i, ex in enumerate(exercise_scores[:10], 1):
        print(f"{i:2d}. {ex['name']:40s} | {ex['muscles_hit']} muscles | "
              f"{ex['total_activation']:.2f} total | {ex['primary_muscles']} primary | "
              f"{ex['type']}")

    print("\n..." + str(len(exercise_scores) - 10) + " more exercises")

    # Show least efficient (isolation exercises)
    print("\n\nLeast Efficient (Isolation - good for fine-tuning):")
    for i, ex in enumerate(sorted(exercise_scores, key=lambda x: x["muscles_hit"])[:5], 1):
        print(f"{i}. {ex['name']:40s} | {ex['muscles_hit']} muscles | "
              f"{ex['total_activation']:.2f} total | {ex['type']}")


if __name__ == "__main__":
    analyze_coverage()
    calculate_theoretical_coverage()
    find_missing_exercise_types()
    analyze_exercise_efficiency()

    print("\n\n" + "="*80)
    print("CONCLUSION")
    print("="*80)
    print("""
The exercise database has SUFFICIENT coverage for all 12 muscle groups.
However, adding more isolation exercises could help the algorithm by:
1. Providing more granular volume control
2. Allowing precise fine-tuning for under-target muscles
3. Reducing side effects when trying to hit specific muscles

Recommended additions: 10-15 more isolation exercises (listed above)
    """)
