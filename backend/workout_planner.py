from pydantic import BaseModel, Field
from typing import List, Dict, Literal, Optional
import math
import json
import boto3
from botocore.exceptions import ClientError


class WorkoutPlannerInput(BaseModel):
    """Input model for workout planner"""
    training_status: Literal[1, 2, 3] = Field(..., description="1=Novice, 2=Intermediate, 3=Advanced")
    sex: Literal[0, 1] = Field(..., description="0=Male, 1=Female")
    recovery_factor: float = Field(..., ge=0.5, le=1.2, description="Recovery factor between 0.5 and 1.2")
    energy_balance_factor: float = Field(..., description="Energy balance factor")
    age: int = Field(..., ge=10, le=100, description="Age in years")
    training_frequency: int = Field(..., ge=1, le=7, description="Training days per week")
    dedication_level: Literal["A", "B", "C"] = Field(..., description="A=Sustainability, B=Balanced, C=Maximum")


class ExerciseSet(BaseModel):
    """Single exercise in a workout"""
    exercise_name: str
    sets: int
    intensity: int
    muscle_activation: Dict[str, float]


class WorkoutDay(BaseModel):
    """Single training day"""
    day_name: str
    frequency_per_week: int
    exercises: List[ExerciseSet]


class WeeklyVolumeSummary(BaseModel):
    """Summary of weekly training volume per muscle"""
    muscle_group: str
    weekly_sets: float


class WorkoutPlanOutput(BaseModel):
    """Output model for generated workout plan"""
    estimated_optimal_sets: float
    target_volume_range: Dict[str, float]
    workout_days: List[WorkoutDay]
    weekly_volume_summary: List[WeeklyVolumeSummary]


# Exercise Database with Muscle Activation Matrix
EXERCISE_DATABASE = {
    "Powerlifting deadlift": {
        "type": "Compound",
        "activation": {"Traps": 1, "Lats": 0.25, "Erector Spine": 1, "Quadriceps": 0.5, "Hamstrings": 0.75, "Glutes": 1, "Calves": 0.5, "Abs": 0.25}
    },
    "Romanian deadlifts": {
        "type": "Compound",
        "activation": {"Traps": 1, "Lats": 0.25, "Erector Spine": 1, "Hamstrings": 1, "Glutes": 1, "Abs": 0.25}
    },
    "Goodmornings": {
        "type": "Compound",
        "activation": {"Erector Spine": 1, "Hamstrings": 1, "Glutes": 1, "Abs": 0.25}
    },
    "Hip extensions & pull-throughs": {
        "type": "Compound",
        "activation": {"Erector Spine": 0.25, "Hamstrings": 1, "Glutes": 1}
    },
    "Back extensions": {
        "type": "Isolation",
        "activation": {"Erector Spine": 1, "Hamstrings": 1, "Glutes": 1}
    },
    "Leg curls": {
        "type": "Isolation",
        "activation": {"Hamstrings": 1, "Calves": 1}
    },
    "Barbell squats": {
        "type": "Compound",
        "activation": {"Erector Spine": 1, "Quadriceps": 1, "Glutes": 1, "Calves": 0.5, "Abs": 0.25}
    },
    "Leg presses, hack & belt squats": {
        "type": "Compound",
        "activation": {"Erector Spine": 0.25, "Quadriceps": 1, "Glutes": 1, "Calves": 0.5}
    },
    "Bulgarian split squats": {
        "type": "Compound",
        "activation": {"Erector Spine": 0.5, "Quadriceps": 1, "Glutes": 1, "Calves": 0.5, "Abs": 0.25}
    },
    "Lunges & step-ups": {
        "type": "Compound",
        "activation": {"Erector Spine": 0.5, "Quadriceps": 1, "Glutes": 1, "Calves": 0.5, "Abs": 0.25}
    },
    "Leg extensions": {
        "type": "Isolation",
        "activation": {"Quadriceps": 1}
    },
    "Hip thrusts & glute kickbacks": {
        "type": "Compound",
        "activation": {"Quadriceps": 0.5, "Glutes": 1}
    },
    "Hip abduction": {
        "type": "Isolation",
        "activation": {"Glutes": 1}
    },
    "Calf raises/jumps": {
        "type": "Isolation",
        "activation": {"Calves": 1}
    },
    "Seated calf raises": {
        "type": "Isolation",
        "activation": {"Calves": 1}
    },
    "Chin-ups & pulldowns": {
        "type": "Compound",
        "activation": {"Pecs": 0.25, "Delt": 1, "Traps": 1, "Lats": 1, "Biceps": 1}
    },
    "Pull-ups & wide pulldowns": {
        "type": "Compound",
        "activation": {"Pecs": 0.5, "Delt": 0.25, "Traps": 1, "Lats": 1, "Biceps": 1}
    },
    "Cable rows with spinal flexion": {
        "type": "Compound",
        "activation": {"Delt": 1, "Traps": 1, "Lats": 1, "Biceps": 0.5, "Triceps": 0.25, "Erector Spine": 0.5, "Hamstrings": 0.25, "Glutes": 0.25}
    },
    "Pull-overs & lat prayers": {
        "type": "Compound",
        "activation": {"Pecs": 0.5, "Delt": 1, "Lats": 1, "Triceps": 1}
    },
    "High rows & rear delt flys": {
        "type": "Compound",
        "activation": {"Delt": 1, "Traps": 1}
    },
    "Barbell bench press": {
        "type": "Compound",
        "activation": {"Pecs": 1, "Delt": 1, "Triceps": 1}
    },
    "Dumbbell bench press": {
        "type": "Compound",
        "activation": {"Pecs": 1, "Delt": 1, "Triceps": 0.5}
    },
    "Chest flys": {
        "type": "Isolation",
        "activation": {"Pecs": 1, "Delt": 1}
    },
    "Barbell overhead press": {
        "type": "Compound",
        "activation": {"Pecs": 0.25, "Delt": 1, "Traps": 0.25, "Triceps": 1, "Abs": 0.25}
    },
    "Dumbbell overhead press": {
        "type": "Compound",
        "activation": {"Pecs": 0.25, "Delt": 1, "Traps": 0.25, "Triceps": 0.5, "Abs": 0.25}
    },
    "Lateral raises": {
        "type": "Isolation",
        "activation": {"Pecs": 0.25, "Delt": 1, "Traps": 0.25}
    },
    "Shrugs": {
        "type": "Isolation",
        "activation": {"Traps": 1}
    },
    "Triceps extensions": {
        "type": "Isolation",
        "activation": {"Triceps": 1}
    },
    "Biceps curls": {
        "type": "Isolation",
        "activation": {"Biceps": 1}
    },
    "Ab crunches": {
        "type": "Isolation",
        "activation": {"Abs": 1}
    },
}

MUSCLE_GROUPS = ["Pecs", "Delt", "Traps", "Lats", "Biceps", "Triceps", "Erector Spine", "Quadriceps", "Hamstrings", "Glutes", "Calves", "Abs"]


class WorkoutPlanner:
    """Main workout planner class using LLM for plan generation"""

    def __init__(self, bedrock_client, model_id: str = "amazon.nova-lite-v1:0"):
        self.bedrock_client = bedrock_client
        self.model_id = model_id

    @staticmethod
    def calculate_optimal_sets(input_data: WorkoutPlannerInput) -> float:
        """
        Calculate estimated optimal sets per week per muscle group

        Formula:
        = ((IF(Training Frequency < 3, Training Frequency, 2.5)) * 5) * Recovery Factor
          * Energy Balance Factor
          * SQRT(Training Status)
          * (1 - ((MAX(Age - 50, 0)) / 10 * 0.12))
          + Sex * 3
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
            "A": (0.60, 0.75),  # Sustainability
            "B": (0.75, 0.90),  # Balanced
            "C": (0.90, 1.00),  # Maximum
        }

        min_pct, max_pct = ranges[dedication_level]
        return {
            "min": round(optimal_sets * min_pct, 1),
            "max": round(optimal_sets * max_pct, 1)
        }

    @staticmethod
    def get_training_status_label(status: int) -> str:
        """Convert training status number to label"""
        labels = {1: "Novice", 2: "Intermediate", 3: "Advanced"}
        return labels[status]

    @staticmethod
    def get_dedication_level_description(level: str) -> str:
        """Get dedication level description"""
        descriptions = {
            "A": "Sustainability Focus (60-75% of optimal volume)",
            "B": "Balanced Approach (75-90% of optimal volume)",
            "C": "Maximum Results (90-100% of optimal volume)"
        }
        return descriptions[level]

    def generate_workout_prompt(self, input_data: WorkoutPlannerInput, optimal_sets: float, target_range: Dict[str, float]) -> str:
        """Generate the prompt for LLM to create workout plan"""

        training_status_label = self.get_training_status_label(input_data.training_status)
        dedication_desc = self.get_dedication_level_description(input_data.dedication_level)

        # Training intensity guidelines
        intensity_guidelines = {
            "Novice": {"Compound": 60, "Isolation": 60},
            "Intermediate": {"Compound": 80, "Isolation": 65},
            "Advanced": {"Compound": 85, "Isolation": 70}
        }

        intensities = intensity_guidelines[training_status_label]

        prompt = f"""You are an expert fitness coach creating a personalized workout plan. Generate a workout plan based on the following constraints:

## User Profile
- Training Status: {training_status_label}
- Sex: {"Female" if input_data.sex == 1 else "Male"}
- Age: {input_data.age}
- Training Frequency: {input_data.training_frequency} days per week
- Dedication Level: {input_data.dedication_level} - {dedication_desc}
- Recovery Factor: {input_data.recovery_factor}
- Energy Balance Factor: {input_data.energy_balance_factor}

## Calculated Target Volumes
- Estimated Optimal Sets Per Muscle Group: {optimal_sets}
- Target Volume Range: {target_range['min']} - {target_range['max']} sets per week per muscle group

## Training Intensity Guidelines (% of 1RM)
- Compound Exercises: {intensities['Compound']}%
- Isolation Exercises: {intensities['Isolation']}%

## CRITICAL CONSTRAINTS (MUST FOLLOW)
1. VOLUME TARGET (HIGHEST PRIORITY): Weekly sets for EACH of the 12 muscle groups should be close to {target_range['min']} - {target_range['max']} sets
   - Target range: {target_range['min']:.1f} - {target_range['max']:.1f} sets/week per muscle
   - Acceptable range (with ±20% tolerance): {target_range['min']*0.8:.1f} - {target_range['max']*1.2:.1f} sets/week
   - ALL 12 muscle groups: Pecs, Delt, Traps, Lats, Biceps, Triceps, Erector Spine, Quadriceps, Hamstrings, Glutes, Calves, Abs
   - Calculate weekly volume as: (sets per exercise) × (muscle activation value) × (frequency per week)
   - Example: 4 sets of Barbell bench press done 2x/week = 4 × 1.0 × 2 = 8 weekly sets for Pecs
   - Aim for the target range, but being slightly outside (within tolerance) is acceptable
   - Being WAY outside tolerance will result in REJECTION

2. FREQUENCY CONSTRAINT: The sum of ALL frequency_per_week values MUST NOT EXCEED {input_data.training_frequency}
   - User's max training frequency: {input_data.training_frequency} days/week
   - Your plan can use FEWER days but NEVER MORE
   - Example for 6 days max: 3 days×2x/week=6, or 2 days×2x/week + 2 days×1x/week=6

3. Training volume per muscle per day MUST NOT exceed 10 sets

4. You MUST ONLY use exercises from the Exercise Database below

5. Use the exact intensity percentages specified above based on exercise type

## Exercise Database with Muscle Activation
{json.dumps(EXERCISE_DATABASE, indent=2)}

## Required Output Format
Generate a workout plan in the following JSON structure:

{{
  "workout_days": [
    {{
      "day_name": "Day A - [descriptive name]",
      "frequency_per_week": [number],
      "exercises": [
        {{
          "exercise_name": "[exact name from database]",
          "sets": [number],
          "intensity": [percentage],
          "muscle_activation": {{...from database...}}
        }}
      ]
    }}
  ]
}}

## Important Notes:
- You can design ANY split pattern (full-body, upper/lower, push/pull/legs, etc.) that fits the constraints
- BEFORE submitting, manually calculate weekly volume for each of the 12 muscle groups to verify ALL are within {target_range['min']}-{target_range['max']} sets
- If a muscle group is under target, add exercises or sets that activate it
- Compound exercises efficiently hit multiple muscle groups (e.g., Barbell bench press hits Pecs, Delt, Triceps)
- Use isolation exercises to fine-tune individual muscle groups that are below target
- Each training day should group exercises logically (e.g., push muscles together, pull muscles together)

## Strategy to Hit All Volume Targets:
1. Start with big compound movements (squats, deadlifts, bench press, rows, overhead press) - these cover most muscle groups
2. Check which muscle groups need more volume
3. Add targeted exercises for lagging muscle groups (e.g., Biceps curls for biceps, Calf raises for calves, Ab crunches for abs)
4. Verify all 12 muscle groups are within range

## REFERENCE EXAMPLE - Study This Carefully:
Here's a successful plan for target range 8.4-10.5 sets/week (6 days training, 3 unique days × 2x/week):

Day A (2x/week):
- Barbell bench press: 4 sets → Pecs(8), Delt(8), Triceps(8)
- Ab crunches: 3 sets → Abs(6)
- Biceps curls: 2 sets → Biceps(4)

Day B (2x/week):
- Pull-ups: 3 sets → Pecs(3), Delt(1.5), Traps(6), Lats(6), Biceps(6)
- Romanian deadlifts: 2 sets → Traps(4), Lats(1), Erector Spine(4), Hamstrings(4), Glutes(4), Abs(1)

Day C (2x/week):
- Barbell squats: 4 sets → Erector Spine(8), Quadriceps(8), Glutes(8), Calves(4), Abs(2)
- Leg curls: 4 sets → Hamstrings(8), Calves(8)
- Calf raises: 3 sets → Calves(6)

Final volumes: Pecs(11), Delt(9.5), Traps(10), Lats(7), Biceps(10), Triceps(8), Erector Spine(12), Quadriceps(8), Hamstrings(12), Glutes(12), Calves(18), Abs(9)
→ Notice how compound exercises are strategically selected to hit multiple muscle groups efficiently!

## Your Task:
Follow this same approach for your target of {target_range['min']:.1f}-{target_range['max']:.1f} sets/week:
1. Start with 2-3 compound movements that cover most muscle groups
2. Calculate volumes for ALL 12 muscles after adding those compounds
3. Identify which muscles are still below {target_range['min']:.1f} sets
4. Add isolation exercises specifically for those lagging muscles (e.g., Leg curls for Hamstrings, Calf raises for Calves, Ab crunches for Abs, Leg extensions for Quadriceps)
5. Fine-tune by adjusting the number of sets (you can use 2, 3, 4, or 5 sets per exercise - don't default to 3-4 always!)
6. Verify EVERY SINGLE muscle group is within range before submitting

⚠️ COMMON MISTAKES TO AVOID:
- Don't focus only on upper body - lower body muscles (Quadriceps, Hamstrings, Glutes, Calves) need volume too!
- Don't forget Abs and Calves - they often need dedicated isolation exercises
- If a muscle has less than {target_range['min']:.1f} sets, you MUST add exercises for it
- You CAN repeat the same exercise across multiple workout days (e.g., Ab crunches on Day A, Day B, and Day C)
- You DON'T need to follow rigid splits (Push/Pull/Legs) - hitting volume targets is MORE IMPORTANT than categorization
- It's OKAY to do Biceps curls 3 times per week, Ab crunches 4 times per week, Calf raises every day, etc.
- Focus on TOTAL WEEKLY VOLUME per muscle, not on keeping each day "unique"
- You can use 2 sets per exercise for fine-tuning - don't always default to 3-4 sets
- Example: If Abs needs 15 sets total and you have 3 workout days, you could do "Ab crunches: 2 sets" on Day A, "Ab crunches: 3 sets" on Day B, "Ab crunches: 2 sets" on Day C = 14 sets total

Generate the workout plan now in valid JSON format:"""

        return prompt

    def call_bedrock_for_workout(self, prompt: str, max_retries: int = 3) -> Optional[Dict]:
        """Call AWS Bedrock to generate workout plan"""

        for attempt in range(max_retries):
            try:
                response = self.bedrock_client.converse(
                    modelId=self.model_id,
                    messages=[
                        {
                            "role": "user",
                            "content": [{"text": prompt}]
                        }
                    ],
                    inferenceConfig={
                        "maxTokens": 4000,
                        "temperature": 0.3,  # Lower temperature for more precise constraint following
                        "topP": 0.9
                    }
                )

                # Extract response text
                response_text = response["output"]["message"]["content"][0]["text"]

                # Try to extract JSON from the response
                # Sometimes LLM wraps JSON in markdown code blocks
                response_text = response_text.strip()
                if response_text.startswith("```json"):
                    response_text = response_text[7:]
                if response_text.startswith("```"):
                    response_text = response_text[3:]
                if response_text.endswith("```"):
                    response_text = response_text[:-3]

                response_text = response_text.strip()

                # Parse JSON
                workout_data = json.loads(response_text)
                return workout_data

            except json.JSONDecodeError as e:
                print(f"Attempt {attempt + 1}: Failed to parse JSON from LLM response: {e}")
                if attempt < max_retries - 1:
                    prompt += "\n\nIMPORTANT: Your previous response was not valid JSON. Please provide ONLY valid JSON with no additional text or markdown formatting."
                    continue
                else:
                    raise Exception("Failed to get valid JSON response from LLM after retries")

            except ClientError as e:
                print(f"Bedrock error: {e}")
                raise Exception(f"Bedrock API error: {str(e)}")
            except Exception as e:
                print(f"Unexpected error: {e}")
                raise Exception(f"Error generating workout plan: {str(e)}")

        return None

    def validate_and_calculate_volumes(self, workout_data: Dict) -> List[WeeklyVolumeSummary]:
        """Validate the workout plan and calculate actual weekly volumes"""
        weekly_volumes = {muscle: 0.0 for muscle in MUSCLE_GROUPS}

        for workout_day in workout_data.get("workout_days", []):
            frequency = workout_day.get("frequency_per_week", 1)

            for exercise in workout_day.get("exercises", []):
                exercise_name = exercise.get("exercise_name")
                sets = exercise.get("sets", 0)

                # Get muscle activation from database
                if exercise_name in EXERCISE_DATABASE:
                    activation = EXERCISE_DATABASE[exercise_name]["activation"]
                    for muscle, activation_value in activation.items():
                        weekly_volumes[muscle] += sets * activation_value * frequency

        volume_summary = [
            WeeklyVolumeSummary(muscle_group=muscle, weekly_sets=round(volume, 1))
            for muscle, volume in weekly_volumes.items()
        ]

        return volume_summary

    def validate_volume_targets(self, workout_data: Dict, target_range: Dict[str, float]) -> tuple[bool, str]:
        """
        Validate if generated workout plan meets volume targets for all muscle groups.
        Returns (is_valid, feedback_message)

        Uses tolerance bands:
        - Within range: acceptable
        - Slightly off (within 20% tolerance): acceptable
        - Way off (beyond 20% tolerance): needs improvement
        """
        weekly_volumes = {muscle: 0.0 for muscle in MUSCLE_GROUPS}

        # Calculate volumes
        for workout_day in workout_data.get("workout_days", []):
            frequency = workout_day.get("frequency_per_week", 1)
            for exercise in workout_day.get("exercises", []):
                exercise_name = exercise.get("exercise_name")
                sets = exercise.get("sets", 0)
                if exercise_name in EXERCISE_DATABASE:
                    activation = EXERCISE_DATABASE[exercise_name]["activation"]
                    for muscle, activation_value in activation.items():
                        weekly_volumes[muscle] += sets * activation_value * frequency

        # Allow 30% tolerance beyond the target range for more flexibility
        # But still catch egregious errors like 4 sets when target is 17.5-21
        tolerance = 0.30
        min_with_tolerance = target_range['min'] * (1 - tolerance)
        max_with_tolerance = target_range['max'] * (1 + tolerance)

        # Check which muscle groups are significantly out of range
        way_too_high = []
        way_too_low = []
        slightly_off = []

        for muscle, volume in weekly_volumes.items():
            if volume < min_with_tolerance:
                deficit = target_range['min'] - volume
                way_too_low.append(f"{muscle}: {volume:.1f} sets (needs {deficit:.1f} more sets)")
            elif volume > max_with_tolerance:
                excess = volume - target_range['max']
                way_too_high.append(f"{muscle}: {volume:.1f} sets ({excess:.1f} sets too many)")
            elif volume < target_range['min'] or volume > target_range['max']:
                slightly_off.append(f"{muscle}: {volume:.1f} sets (target: {target_range['min']:.1f}-{target_range['max']:.1f})")

        # Only reject if muscles are WAY off (beyond tolerance)
        if way_too_low or way_too_high:
            feedback = f"VOLUME VALIDATION FAILED - Target range: {target_range['min']:.1f}-{target_range['max']:.1f} sets/week (accepting up to ±20% tolerance)\n\n"

            if way_too_low:
                feedback += "WAY TOO LOW (must fix):\n" + "\n".join(way_too_low) + "\n\n"
                feedback += "SPECIFIC FIXES NEEDED:\n"

                # Give specific exercise suggestions for each low muscle
                exercise_suggestions = {
                    "Quadriceps": "Add Leg extensions or Barbell squats or Leg presses",
                    "Hamstrings": "Add Leg curls or Romanian deadlifts",
                    "Glutes": "Add Hip thrusts or Barbell squats or Romanian deadlifts",
                    "Calves": "Add Calf raises or Seated calf raises",
                    "Abs": "Add Ab crunches (you can do many sets of this)",
                    "Biceps": "Add Biceps curls",
                    "Triceps": "Add Triceps extensions",
                    "Pecs": "Add Barbell bench press or Dumbbell bench press or Chest flys",
                    "Delt": "Add Barbell overhead press or Lateral raises",
                    "Traps": "Add Shrugs or Romanian deadlifts",
                    "Lats": "Add Pull-ups or Chin-ups",
                    "Erector Spine": "Add Romanian deadlifts or Barbell squats"
                }

                for muscle, volume in weekly_volumes.items():
                    if volume < min_with_tolerance and muscle in exercise_suggestions:
                        feedback += f"  - {muscle}: {exercise_suggestions[muscle]}\n"
                feedback += "\n"

            if way_too_high:
                feedback += "WAY TOO HIGH (must fix):\n" + "\n".join(way_too_high) + "\n\n"
                feedback += "Suggestions: Reduce sets or remove some exercises for these muscle groups.\n\n"

            if slightly_off:
                feedback += "Slightly off but acceptable:\n" + "\n".join(slightly_off) + "\n\n"

            feedback += f"IMPORTANT: Focus on fixing the muscles that are WAY off. Regenerate the plan with better balance."
            return False, feedback

        # Plan is acceptable (all within tolerance)
        if slightly_off:
            return True, f"Plan acceptable - some muscles slightly off target but within ±20% tolerance:\n" + "\n".join(slightly_off)

        return True, "All muscle groups within target range"

    def generate_workout_plan(self, input_data: WorkoutPlannerInput) -> WorkoutPlanOutput:
        """
        Generate a complete workout plan using LLM with volume validation
        """
        # Calculate optimal sets and target range
        optimal_sets = self.calculate_optimal_sets(input_data)
        target_range = self.get_target_volume_range(optimal_sets, input_data.dedication_level)

        # Generate base prompt for LLM
        base_prompt = self.generate_workout_prompt(input_data, optimal_sets, target_range)

        # Try up to 5 times to get a valid plan
        max_attempts = 5
        workout_data = None

        for attempt in range(max_attempts):
            print(f"\nAttempt {attempt + 1}/{max_attempts} to generate workout plan...")

            # Build prompt with feedback from previous attempts
            current_prompt = base_prompt
            if attempt > 0:
                current_prompt += f"\n\n{'='*50}\nATTEMPT {attempt + 1} - Your previous plan was REJECTED.\n{'='*50}\n"

            # Call LLM to generate workout plan
            workout_data = self.call_bedrock_for_workout(current_prompt)

            if not workout_data:
                raise Exception("Failed to generate workout plan")

            # Validate total training frequency
            total_frequency = sum(
                day.get("frequency_per_week", 0)
                for day in workout_data.get("workout_days", [])
            )

            if total_frequency > input_data.training_frequency:
                if attempt < max_attempts - 1:
                    base_prompt += f"\n\n🚫 FREQUENCY ERROR: Your plan has {total_frequency} total days/week which EXCEEDS the max of {input_data.training_frequency}. You MUST regenerate with total frequency ≤ {input_data.training_frequency}."
                    print(f"  ❌ Frequency validation failed: {total_frequency} > {input_data.training_frequency}")
                    continue
                else:
                    raise Exception(
                        f"Generated plan exceeds maximum training frequency: "
                        f"plan requires {total_frequency} days/week but user maximum is {input_data.training_frequency} days/week."
                    )

            # Validate volume targets
            is_valid, feedback = self.validate_volume_targets(workout_data, target_range)
            if not is_valid:
                if attempt < max_attempts - 1:
                    base_prompt += f"\n\n🚫 {feedback}"
                    print(f"  ❌ Volume validation failed - retrying...")
                    continue
                else:
                    # Accept the plan after max attempts but log warning
                    print(f"⚠️  Warning: Accepting plan after {max_attempts} attempts even though volumes are outside target range.")
                    print(f"    User can manually adjust the plan.\n{feedback}")
                    break

            # Plan is valid
            print(f"  ✓ Plan validated successfully!")
            break

        # Parse and validate workout days
        workout_days = []
        for day_data in workout_data.get("workout_days", []):
            exercises = []
            for ex_data in day_data.get("exercises", []):
                exercise_name = ex_data.get("exercise_name")

                # Ensure exercise exists in database and has activation data
                if exercise_name in EXERCISE_DATABASE:
                    activation = EXERCISE_DATABASE[exercise_name]["activation"]
                else:
                    # Skip invalid exercises
                    print(f"Warning: Exercise '{exercise_name}' not found in database, skipping")
                    continue

                exercises.append(ExerciseSet(
                    exercise_name=exercise_name,
                    sets=ex_data.get("sets", 0),
                    intensity=ex_data.get("intensity", 60),
                    muscle_activation=activation
                ))

            workout_days.append(WorkoutDay(
                day_name=day_data.get("day_name", "Workout Day"),
                frequency_per_week=day_data.get("frequency_per_week", 1),
                exercises=exercises
            ))

        # Calculate actual weekly volumes
        volume_summary = self.validate_and_calculate_volumes(workout_data)

        return WorkoutPlanOutput(
            estimated_optimal_sets=optimal_sets,
            target_volume_range=target_range,
            workout_days=workout_days,
            weekly_volume_summary=volume_summary
        )
