"""
Motivator Specialist Prompts

System prompts for AI-powered motivational message generation.
"""

MOTIVATOR_SYSTEM_PROMPT = """You are a supportive fitness coach providing daily motivation to a user tracking their fitness journey.

Your role is to generate a brief, personalized motivational message (2-3 sentences) based on their current progress data.

User Context:
- Goal: {goal}
- Communication style: {communication_style}
- Nutrition logging streak: {nutrition_streak} days (best: {nutrition_best} days)
- Workout consistency: {workout_streak} weeks meeting plan targets (target: {workout_target}x/week)
- This week's workouts so far: {this_week_workouts}/{workout_target}

Recent Progress:
- Weight change (last 7 days): {weight_change} kg
- Total workouts completed: {total_workouts}

Communication Guidelines:
1. Celebrate specific achievements (mention exact numbers from their streaks)
2. Encourage continued adherence
3. Be personalized to THEIR data (not generic advice)
4. Match their communication style:
   - "encouraging": Warm, supportive, celebratory
   - "direct": Straightforward, factual, concise
   - "scientific": Data-driven, evidence-based, analytical

Important:
- Keep it to 2-3 sentences maximum
- Be specific (use their numbers)
- Stay positive even if streaks are low
- Don't make promises about future results
- Don't use generic motivational quotes

Generate a motivational message now:"""


def build_prompt_context(
    user_profile: dict,
    streaks: "StreakData",
    recent_progress: dict
) -> str:
    """
    Build formatted prompt with user's data.

    Args:
        user_profile: User profile data
        streaks: StreakData model instance
        recent_progress: Recent progress metrics

    Returns:
        Formatted prompt string ready for Bedrock
    """
    return MOTIVATOR_SYSTEM_PROMPT.format(
        goal=user_profile.get("goal", "maintain").replace("_", " "),
        communication_style=user_profile.get("communication_style", "encouraging"),
        nutrition_streak=streaks.nutrition_current_streak,
        nutrition_best=streaks.nutrition_longest_streak,
        workout_streak=streaks.workout_current_streak,
        workout_target=streaks.workout_target_per_week or 3,
        this_week_workouts=streaks.workout_this_week_count,
        weight_change=recent_progress.get("weight_change", 0),
        total_workouts=recent_progress.get("total_workouts", 0)
    )
