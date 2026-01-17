"""
Deterministic Workout Planner

Pure algorithmic approach to workout plan generation.
Uses constraint satisfaction and optimization instead of LLM.

Benefits:
- Deterministic (same input = same output)
- Fast (<100ms vs several seconds)
- Free (no API costs)
- Guaranteed to meet constraints or fail with clear error
- Explainable (can show math behind decisions)
"""

from pydantic import BaseModel, Field
from typing import List, Dict, Literal, Optional, Tuple
import math
from copy import deepcopy

# Import shared models and data from existing workout planner
from workout_planner import (
    WorkoutPlannerInput,
    WorkoutPlanOutput,
    WorkoutDay,
    ExerciseSet,
    WeeklyVolumeSummary,
    EXERCISE_DATABASE,
    MUSCLE_GROUPS
)


class ExerciseCandidate:
    """Represents a candidate exercise with calculated efficiency metrics"""

    def __init__(self, name: str, exercise_data: dict):
        self.name = name
        self.type = exercise_data["type"]
        self.activation = exercise_data["activation"]
        self.efficiency_score = 0.0
        self.target_coverage = 0.0

    def calculate_efficiency(self, current_volumes: Dict[str, float], targets: Dict[str, float]) -> float:
        """
        Calculate how efficiently this exercise fills remaining volume gaps.

        Returns a score where higher = more efficient for current needs.
        """
        total_gap_filled = 0.0
        muscles_helped = 0

        for muscle, activation_value in self.activation.items():
            current = current_volumes.get(muscle, 0.0)
            target = targets.get(muscle, 0.0)
            gap = max(0, target - current)

            if gap > 0 and activation_value > 0:
                # How much this exercise helps fill the gap
                gap_filled = min(gap, activation_value)
                total_gap_filled += gap_filled
                muscles_helped += 1

        # Prefer exercises that help multiple muscles that need volume
        self.efficiency_score = total_gap_filled * (1 + muscles_helped * 0.1)
        self.target_coverage = muscles_helped

        return self.efficiency_score


class DeterministicWorkoutPlanner:
    """
    Algorithmic workout planner using constraint satisfaction.

    Algorithm:
    1. Calculate volume targets for each muscle group
    2. Select foundation compound exercises (always include key movements)
    3. Greedily add exercises to fill volume gaps
    4. Distribute exercises across training days
    5. Validate all constraints
    """

    def __init__(self):
        pass

    @staticmethod
    def calculate_optimal_sets(input_data: WorkoutPlannerInput) -> float:
        """
        Calculate estimated optimal sets per week per muscle group.
        (Same formula as LLM version for consistency)
        """
        freq = input_data.training_frequency if input_data.training_frequency < 3 else 2.5

        optimal_sets = (
            (freq * 5) * input_data.recovery_factor
            * input_data.energy_balance_factor
            * math.sqrt(input_data.training_status)
            * (1 - ((max(input_data.age - 50, 0)) / 10 * 0.12))
            + (input_data.sex * 3)
        )

        return round(optimal_sets, 1)

    @staticmethod
    def get_target_volume_range(optimal_sets: float, dedication_level: str) -> Dict[str, float]:
        """Get target volume range based on dedication level"""
        ranges = {
            "A": (0.55, 0.80),  # Sustainability (widened from 0.60-0.75)
            "B": (0.70, 0.95),  # Balanced (widened from 0.75-0.90)
            "C": (0.85, 1.05),  # Maximum (widened from 0.90-1.00)
        }

        min_pct, max_pct = ranges[dedication_level]
        return {
            "min": round(optimal_sets * min_pct, 1),
            "max": round(optimal_sets * max_pct, 1)
        }

    @staticmethod
    def get_intensity_for_exercise(exercise_name: str, training_status: int) -> int:
        """Get recommended intensity % for exercise based on type and training status"""
        exercise_type = EXERCISE_DATABASE[exercise_name]["type"]

        intensity_guidelines = {
            1: {"Compound": 60, "Isolation": 60},      # Novice
            2: {"Compound": 80, "Isolation": 65},      # Intermediate
            3: {"Compound": 85, "Isolation": 70}       # Advanced
        }

        return intensity_guidelines[training_status][exercise_type]

    def calculate_volume_targets(self, input_data: WorkoutPlannerInput) -> Dict[str, Tuple[float, float]]:
        """
        Calculate target volume ranges for each muscle group.

        Returns dict: {muscle_name: (min_sets, max_sets)}
        """
        optimal_sets = self.calculate_optimal_sets(input_data)
        target_range = self.get_target_volume_range(optimal_sets, input_data.dedication_level)

        # All muscle groups have same target
        targets = {}
        for muscle in MUSCLE_GROUPS:
            targets[muscle] = (target_range["min"], target_range["max"])

        return targets

    def select_foundation_exercises(self, training_status: int) -> List[Tuple[str, int, int]]:
        """
        Select foundation compound exercises that should always be included.

        Returns list of (exercise_name, sets, intensity)
        """
        foundation = []

        # Key compound movements based on training status
        if training_status == 1:  # Novice
            # Simpler movements, fewer sets
            foundation = [
                ("Barbell squats", 3, 60),
                ("Barbell bench press", 3, 60),
                ("Romanian deadlifts", 2, 60),
                ("Pull-ups & wide pulldowns", 3, 60),
            ]
        elif training_status == 2:  # Intermediate
            # More variety, moderate volume
            foundation = [
                ("Barbell squats", 4, 80),
                ("Powerlifting deadlift", 3, 80),
                ("Barbell bench press", 4, 80),
                ("Pull-ups & wide pulldowns", 3, 80),
                ("Barbell overhead press", 3, 80),
            ]
        else:  # Advanced
            # Full compound movements, higher volume
            foundation = [
                ("Barbell squats", 5, 85),
                ("Powerlifting deadlift", 4, 85),
                ("Barbell bench press", 5, 85),
                ("Pull-ups & wide pulldowns", 4, 85),
                ("Barbell overhead press", 4, 85),
                ("Romanian deadlifts", 3, 85),
            ]

        return foundation

    def calculate_current_volumes(
        self,
        exercises: List[Tuple[str, int, int]],
        frequency_per_exercise: Optional[Dict[str, int]] = None
    ) -> Dict[str, float]:
        """
        Calculate current weekly volume for each muscle from exercise list.

        Args:
            exercises: List of (exercise_name, sets, intensity)
            frequency_per_exercise: Optional dict mapping exercise names to their weekly frequency
                                  If None, assumes all exercises done together

        Returns:
            Dict of {muscle_name: weekly_sets}
        """
        volumes = {muscle: 0.0 for muscle in MUSCLE_GROUPS}

        for exercise_name, sets, _ in exercises:
            activation = EXERCISE_DATABASE[exercise_name]["activation"]
            freq = frequency_per_exercise.get(exercise_name, 1) if frequency_per_exercise else 1

            for muscle, activation_value in activation.items():
                volumes[muscle] += sets * activation_value * freq

        return volumes

    def find_best_exercise_for_gaps(
        self,
        current_volumes: Dict[str, float],
        targets: Dict[str, Tuple[float, float]],
        excluded_exercises: set
    ) -> Optional[str]:
        """
        Find the most efficient exercise to fill remaining volume gaps.

        Returns exercise name or None if all targets met.
        """
        # Calculate target midpoints
        target_midpoints = {
            muscle: (min_vol + max_vol) / 2
            for muscle, (min_vol, max_vol) in targets.items()
        }

        # Find best candidate
        best_exercise = None
        best_score = 0.0

        for exercise_name, exercise_data in EXERCISE_DATABASE.items():
            if exercise_name in excluded_exercises:
                continue

            candidate = ExerciseCandidate(exercise_name, exercise_data)
            score = candidate.calculate_efficiency(current_volumes, target_midpoints)

            if score > best_score:
                best_score = score
                best_exercise = exercise_name

        return best_exercise if best_score > 0 else None

    def optimize_sets_for_exercise(
        self,
        exercise_name: str,
        current_volumes: Dict[str, float],
        targets: Dict[str, Tuple[float, float]]
    ) -> int:
        """
        Determine optimal number of sets for an exercise.

        Returns number of sets (2-5)
        """
        activation = EXERCISE_DATABASE[exercise_name]["activation"]

        # Calculate how many sets would be needed to fill largest gap
        max_sets_needed = 0

        for muscle, activation_value in activation.items():
            if activation_value > 0:
                current = current_volumes.get(muscle, 0.0)
                target_mid = (targets[muscle][0] + targets[muscle][1]) / 2
                gap = target_mid - current

                if gap > 0:
                    # How many sets of this exercise to fill the gap?
                    sets_for_gap = math.ceil(gap / activation_value)
                    max_sets_needed = max(max_sets_needed, sets_for_gap)

        # Constrain to reasonable range (2-5 sets)
        return min(5, max(2, max_sets_needed))

    def build_exercise_plan(
        self,
        targets: Dict[str, Tuple[float, float]],
        training_status: int,
        training_frequency: int
    ) -> List[Tuple[str, int]]:
        """
        Build complete exercise plan using greedy algorithm.

        Returns list of (exercise_name, sets_per_session)
        """
        # Target weekly volumes (use midpoint of range)
        target_weekly = {
            muscle: (min_vol + max_vol) / 2
            for muscle, (min_vol, max_vol) in targets.items()
        }

        # Current weekly volumes
        current_weekly = {muscle: 0.0 for muscle in MUSCLE_GROUPS}

        # Selected exercises
        selected_exercises = []
        used_exercises = set()

        # Determine how many times each exercise will be performed per week
        # For simplicity, assume all exercises done 2x/week for higher frequencies,
        # 1x/week for lower frequencies
        default_frequency = 2 if training_frequency >= 4 else 1

        # Greedy selection loop
        max_exercises = 25  # Increased safety limit
        for iteration in range(max_exercises):
            # Check if all muscles have reached minimum target
            all_satisfied = all(
                current_weekly[muscle] >= targets[muscle][0]
                for muscle in MUSCLE_GROUPS
            )

            if all_satisfied:
                break

            # Find best exercise to add
            best_exercise = None
            best_sets = 0
            best_score = -999999.0

            for exercise_name, exercise_data in EXERCISE_DATABASE.items():
                # Allow reusing exercises if needed (remove exclusion check)
                # This allows adding same exercise multiple times

                # Try different set counts (2-5)
                for sets in range(2, 6):
                    # Calculate how much this would help
                    score = 0.0
                    muscles_helped = 0
                    would_overtrain = False

                    for muscle, activation_value in exercise_data["activation"].items():
                        weekly_contribution = sets * activation_value * default_frequency
                        current = current_weekly.get(muscle, 0.0)
                        target_min, target_max = targets[muscle]

                        # Score based on how well it fills gaps
                        if current < target_min:
                            # Muscle needs volume - HIGH priority
                            gap = target_min - current
                            contribution = min(weekly_contribution, gap)
                            score += contribution * 5.0  # Much higher priority
                            if contribution > 0:
                                muscles_helped += 1
                        elif current >= target_max * 1.2:
                            # Way over max - strong penalty
                            score -= weekly_contribution * 3.0
                        elif current >= target_max:
                            # Slightly over max - medium penalty
                            score -= weekly_contribution * 1.5
                        else:
                            # In range - small bonus
                            score += weekly_contribution * 0.05

                    # Bonus for exercises that help multiple under-target muscles
                    score += muscles_helped * 1.0

                    # Check if this would cause severe overtraining
                    for muscle, activation_value in exercise_data["activation"].items():
                        current = current_weekly.get(muscle, 0.0)
                        weekly_contribution = sets * activation_value * default_frequency
                        if current + weekly_contribution > targets[muscle][1] * 1.5:  # 50% over max (more lenient)
                            would_overtrain = True
                            break

                    if would_overtrain:
                        continue

                    # Penalize reusing same exercise
                    if exercise_name in used_exercises:
                        score -= 2.0

                    if score > best_score:
                        best_score = score
                        best_exercise = exercise_name
                        best_sets = sets

            if not best_exercise or best_score <= -100:
                # Can't improve further without major overtraining
                break

            # Add the exercise
            selected_exercises.append((best_exercise, best_sets))
            used_exercises.add(best_exercise)

            # Update current volumes
            activation = EXERCISE_DATABASE[best_exercise]["activation"]
            for muscle, activation_value in activation.items():
                current_weekly[muscle] += best_sets * activation_value * default_frequency

        return selected_exercises

    def _balance_exercises_across_days(self, workout_days: List[WorkoutDay]) -> List[WorkoutDay]:
        """
        Balance exercises across days to ensure each day has 3-6 exercises.

        Prevents days with only 1-2 exercises (too light) or 7+ exercises (too heavy).
        """
        MIN_EXERCISES = 3
        MAX_EXERCISES = 6

        # Count exercises per day
        day_counts = [(i, len(day.exercises)) for i, day in enumerate(workout_days)]

        # Find underloaded and overloaded days
        underloaded = [(i, count) for i, count in day_counts if count < MIN_EXERCISES]
        overloaded = [(i, count) for i, count in day_counts if count > MAX_EXERCISES]

        # If we have underloaded days, try to redistribute
        if underloaded and len(workout_days) > 1:
            # Collect all exercises into a pool
            all_exercises = []
            for day in workout_days:
                all_exercises.extend(day.exercises)

            # Redistribute evenly
            target_per_day = len(all_exercises) // len(workout_days)
            target_per_day = max(MIN_EXERCISES, min(target_per_day, MAX_EXERCISES))

            # Clear existing exercises and redistribute
            new_days = []
            exercise_idx = 0

            for day_idx, day in enumerate(workout_days):
                day_exercises = []
                # Assign target number of exercises to each day
                exercises_for_this_day = min(target_per_day, len(all_exercises) - exercise_idx)

                for _ in range(exercises_for_this_day):
                    if exercise_idx < len(all_exercises):
                        day_exercises.append(all_exercises[exercise_idx])
                        exercise_idx += 1

                # Ensure at least MIN_EXERCISES per day (if possible)
                while len(day_exercises) < MIN_EXERCISES and exercise_idx < len(all_exercises):
                    day_exercises.append(all_exercises[exercise_idx])
                    exercise_idx += 1

                new_days.append(WorkoutDay(
                    day_name=day.day_name,
                    frequency_per_week=day.frequency_per_week,
                    exercises=day_exercises
                ))

            return new_days

        return workout_days

    def distribute_across_days(
        self,
        exercises: List[Tuple[str, int, int]],
        training_frequency: int
    ) -> List[WorkoutDay]:
        """
        Distribute exercises across training days using split patterns.

        Strategy based on frequency:
        - 2-3 days: Full body split
        - 4-5 days: Upper/Lower split
        - 6-7 days: Push/Pull/Legs split

        Automatically reduces frequency if not enough exercises for balanced days.
        """
        MIN_EXERCISES_PER_DAY = 3
        total_exercises = len(exercises)

        # Determine optimal frequency based on exercise count
        # We want at least 3 exercises per unique workout day
        if training_frequency >= 6:
            # PPL = 3 unique days, need at least 9 exercises
            if total_exercises < 9:
                # Not enough exercises for 3-day split, use upper/lower instead
                training_frequency = 4  # 2 unique days (upper/lower)

        if training_frequency >= 4:
            # Upper/Lower = 2 unique days, need at least 6 exercises
            if total_exercises < 6:
                # Not enough exercises for 2-day split, use full body instead
                training_frequency = 3  # 1 unique day (full body)

        if training_frequency <= 3:
            workout_days = self._create_fullbody_split(exercises, training_frequency)
        elif training_frequency <= 5:
            workout_days = self._create_upper_lower_split(exercises, training_frequency)
        else:
            workout_days = self._create_push_pull_legs_split(exercises, training_frequency)

        # Balance exercises across days to prevent days with only 1-2 exercises
        return self._balance_exercises_across_days(workout_days)

    def _categorize_exercise(self, exercise_name: str) -> str:
        """Categorize exercise as push/pull/legs/core"""
        activation = EXERCISE_DATABASE[exercise_name]["activation"]

        # Check dominant muscle groups
        push_muscles = ["Pecs", "Delt", "Triceps"]
        pull_muscles = ["Lats", "Traps", "Biceps"]
        leg_muscles = ["Quadriceps", "Hamstrings", "Glutes", "Calves"]

        push_score = sum(activation.get(m, 0) for m in push_muscles)
        pull_score = sum(activation.get(m, 0) for m in pull_muscles)
        leg_score = sum(activation.get(m, 0) for m in leg_muscles)

        if leg_score > push_score and leg_score > pull_score:
            return "legs"
        elif push_score > pull_score:
            return "push"
        elif pull_score > 0:
            return "pull"
        else:
            return "core"

    def _create_fullbody_split(
        self,
        exercises: List[Tuple[str, int, int]],
        frequency: int
    ) -> List[WorkoutDay]:
        """Create full-body split (all exercises each session)"""
        # Merge duplicate exercises by summing sets
        exercise_map = {}
        for exercise_name, sets, intensity in exercises:
            if exercise_name in exercise_map:
                # Merge: add sets together
                exercise_map[exercise_name] = (exercise_map[exercise_name][0] + sets, intensity)
            else:
                exercise_map[exercise_name] = (sets, intensity)

        # Convert to ExerciseSet objects
        # Cap at 6 sets per exercise per day (realistic training limit)
        workout_exercises = []
        for exercise_name, (sets, intensity) in exercise_map.items():
            # Cap at 6 sets per exercise per session
            capped_sets = min(sets, 6)
            activation = EXERCISE_DATABASE[exercise_name]["activation"]
            workout_exercises.append(ExerciseSet(
                exercise_name=exercise_name,
                sets=capped_sets,
                intensity=intensity,
                muscle_activation=activation
            ))

        return [
            WorkoutDay(
                day_name="Full Body Workout",
                frequency_per_week=frequency,
                exercises=workout_exercises
            )
        ]

    def _create_upper_lower_split(
        self,
        exercises: List[Tuple[str, int, int]],
        frequency: int
    ) -> List[WorkoutDay]:
        """Create upper/lower split"""
        # Merge duplicate exercises by category
        upper_map = {}
        lower_map = {}

        for exercise_name, sets, intensity in exercises:
            category = self._categorize_exercise(exercise_name)

            if category == "legs":
                if exercise_name in lower_map:
                    lower_map[exercise_name] = (lower_map[exercise_name][0] + sets, intensity)
                else:
                    lower_map[exercise_name] = (sets, intensity)
            else:
                if exercise_name in upper_map:
                    upper_map[exercise_name] = (upper_map[exercise_name][0] + sets, intensity)
                else:
                    upper_map[exercise_name] = (sets, intensity)

        # Convert to ExerciseSet objects
        # Cap at 6 sets per exercise per day (realistic training limit)
        upper_exercises = []
        for exercise_name, (sets, intensity) in upper_map.items():
            capped_sets = min(sets, 6)
            activation = EXERCISE_DATABASE[exercise_name]["activation"]
            upper_exercises.append(ExerciseSet(
                exercise_name=exercise_name,
                sets=capped_sets,
                intensity=intensity,
                muscle_activation=activation
            ))

        lower_exercises = []
        for exercise_name, (sets, intensity) in lower_map.items():
            capped_sets = min(sets, 6)
            activation = EXERCISE_DATABASE[exercise_name]["activation"]
            lower_exercises.append(ExerciseSet(
                exercise_name=exercise_name,
                sets=capped_sets,
                intensity=intensity,
                muscle_activation=activation
            ))

        # Distribute frequency (e.g., 4 days = 2 upper + 2 lower)
        upper_freq = (frequency + 1) // 2
        lower_freq = frequency // 2

        return [
            WorkoutDay(
                day_name="Upper Body",
                frequency_per_week=upper_freq,
                exercises=upper_exercises
            ),
            WorkoutDay(
                day_name="Lower Body",
                frequency_per_week=lower_freq,
                exercises=lower_exercises
            )
        ]

    def _create_push_pull_legs_split(
        self,
        exercises: List[Tuple[str, int, int]],
        frequency: int
    ) -> List[WorkoutDay]:
        """Create push/pull/legs split"""
        # Merge duplicate exercises by category
        push_map = {}
        pull_map = {}
        leg_map = {}

        for exercise_name, sets, intensity in exercises:
            category = self._categorize_exercise(exercise_name)

            if category == "push":
                if exercise_name in push_map:
                    push_map[exercise_name] = (push_map[exercise_name][0] + sets, intensity)
                else:
                    push_map[exercise_name] = (sets, intensity)
            elif category == "pull":
                if exercise_name in pull_map:
                    pull_map[exercise_name] = (pull_map[exercise_name][0] + sets, intensity)
                else:
                    pull_map[exercise_name] = (sets, intensity)
            else:  # legs or core
                if exercise_name in leg_map:
                    leg_map[exercise_name] = (leg_map[exercise_name][0] + sets, intensity)
                else:
                    leg_map[exercise_name] = (sets, intensity)

        # Convert to ExerciseSet objects
        # Cap at 6 sets per exercise per day (realistic training limit)
        push_exercises = []
        for exercise_name, (sets, intensity) in push_map.items():
            capped_sets = min(sets, 6)
            activation = EXERCISE_DATABASE[exercise_name]["activation"]
            push_exercises.append(ExerciseSet(
                exercise_name=exercise_name,
                sets=capped_sets,
                intensity=intensity,
                muscle_activation=activation
            ))

        pull_exercises = []
        for exercise_name, (sets, intensity) in pull_map.items():
            capped_sets = min(sets, 6)
            activation = EXERCISE_DATABASE[exercise_name]["activation"]
            pull_exercises.append(ExerciseSet(
                exercise_name=exercise_name,
                sets=capped_sets,
                intensity=intensity,
                muscle_activation=activation
            ))

        leg_exercises = []
        for exercise_name, (sets, intensity) in leg_map.items():
            capped_sets = min(sets, 6)
            activation = EXERCISE_DATABASE[exercise_name]["activation"]
            leg_exercises.append(ExerciseSet(
                exercise_name=exercise_name,
                sets=capped_sets,
                intensity=intensity,
                muscle_activation=activation
            ))

        # Distribute frequency (e.g., 6 days = 2 push + 2 pull + 2 legs)
        push_freq = (frequency + 2) // 3
        pull_freq = (frequency + 1) // 3
        legs_freq = frequency // 3

        return [
            WorkoutDay(
                day_name="Push Day (Chest, Shoulders, Triceps)",
                frequency_per_week=push_freq,
                exercises=push_exercises
            ),
            WorkoutDay(
                day_name="Pull Day (Back, Biceps)",
                frequency_per_week=pull_freq,
                exercises=pull_exercises
            ),
            WorkoutDay(
                day_name="Leg Day (Quads, Hams, Glutes, Calves)",
                frequency_per_week=legs_freq,
                exercises=leg_exercises
            )
        ]

    def validate_plan(
        self,
        workout_days: List[WorkoutDay],
        targets: Dict[str, Tuple[float, float]],
        training_frequency: int,
        training_status: int = 1
    ) -> Tuple[bool, str]:
        """
        Validate that plan meets all constraints.

        Returns (is_valid, error_message)
        """
        # 1. Check frequency constraint
        total_frequency = sum(day.frequency_per_week for day in workout_days)
        if total_frequency > training_frequency:
            return False, f"Plan requires {total_frequency} days/week but max is {training_frequency}"

        # 2. Check volume targets
        weekly_volumes = {muscle: 0.0 for muscle in MUSCLE_GROUPS}

        for workout_day in workout_days:
            frequency = workout_day.frequency_per_week
            for exercise in workout_day.exercises:
                for muscle, activation_value in exercise.muscle_activation.items():
                    weekly_volumes[muscle] += exercise.sets * activation_value * frequency

        # Check each muscle
        errors = []
        for muscle, (min_vol, max_vol) in targets.items():
            actual = weekly_volumes[muscle]
            if actual < min_vol * 0.85:  # 15% under tolerance (relaxed from 10%)
                errors.append(f"{muscle}: {actual:.1f} sets (need {min_vol:.1f}-{max_vol:.1f})")

        if errors:
            return False, "Volume targets not met:\n" + "\n".join(errors)

        # 3. Check daily volume constraint (training status dependent)
        # Advanced lifters can handle more volume per day
        daily_limit_per_muscle = {
            1: 10,  # Novice: 10 sets/muscle/day
            2: 15,  # Intermediate: 15 sets/muscle/day
            3: 20   # Advanced: 20 sets/muscle/day
        }
        max_daily_volume = daily_limit_per_muscle.get(training_status, 10)

        for workout_day in workout_days:
            daily_volumes = {muscle: 0.0 for muscle in MUSCLE_GROUPS}
            for exercise in workout_day.exercises:
                for muscle, activation_value in exercise.muscle_activation.items():
                    daily_volumes[muscle] += exercise.sets * activation_value

            for muscle, volume in daily_volumes.items():
                if volume > max_daily_volume:
                    return False, f"{workout_day.day_name}: {muscle} has {volume:.1f} sets (max {max_daily_volume} per day for training status {training_status})"

        return True, "All constraints satisfied"

    def generate_workout_plan(self, input_data: WorkoutPlannerInput) -> WorkoutPlanOutput:
        """
        Generate workout plan using deterministic algorithm.

        Guaranteed to meet constraints or raise exception.
        """
        # Step 1: Calculate targets
        optimal_sets = self.calculate_optimal_sets(input_data)
        target_range = self.get_target_volume_range(optimal_sets, input_data.dedication_level)
        targets = self.calculate_volume_targets(input_data)

        # Step 2: Build complete exercise list using greedy algorithm
        exercises_with_sets = self.build_exercise_plan(
            targets,
            input_data.training_status,
            input_data.training_frequency
        )

        # Step 3: Add intensity to exercises
        exercises_complete = [
            (name, sets, self.get_intensity_for_exercise(name, input_data.training_status))
            for name, sets in exercises_with_sets
        ]

        # Step 4: Distribute across training days
        workout_days = self.distribute_across_days(
            exercises_complete,
            input_data.training_frequency
        )

        # Step 5: Validate plan
        is_valid, message = self.validate_plan(
            workout_days,
            targets,
            input_data.training_frequency,
            input_data.training_status
        )

        if not is_valid:
            raise Exception(f"Generated plan failed validation: {message}")

        # Step 6: Calculate weekly volume summary
        weekly_volumes = {muscle: 0.0 for muscle in MUSCLE_GROUPS}
        for workout_day in workout_days:
            frequency = workout_day.frequency_per_week
            for exercise in workout_day.exercises:
                for muscle, activation_value in exercise.muscle_activation.items():
                    weekly_volumes[muscle] += exercise.sets * activation_value * frequency

        volume_summary = [
            WeeklyVolumeSummary(muscle_group=muscle, weekly_sets=round(volume, 1))
            for muscle, volume in weekly_volumes.items()
        ]

        return WorkoutPlanOutput(
            estimated_optimal_sets=optimal_sets,
            target_volume_range=target_range,
            workout_days=workout_days,
            weekly_volume_summary=volume_summary
        )
