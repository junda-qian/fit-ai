"""
Motivator Specialist Message Generator

AI-powered motivational message generation using Bedrock Claude.
"""

from datetime import datetime
import sys
import os

# Add parent directory to path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

from ai_agents.shared.models import MotivationalMessage, StreakData
from .prompts import build_prompt_context


async def generate_motivational_message(
    bedrock_client,
    user_id: str,
    streaks: StreakData,
    user_profile: dict,
    recent_progress: dict,
    model_id: str = "anthropic.claude-3-5-sonnet-20241022-v2:0"
) -> MotivationalMessage:
    """
    Generate personalized motivational message using Bedrock Claude.

    Args:
        bedrock_client: Boto3 Bedrock runtime client
        user_id: User identifier
        streaks: StreakData model instance
        user_profile: User profile data (goal, communication_style)
        recent_progress: Recent progress metrics (weight_change, total_workouts)
        model_id: Bedrock model ID to use

    Returns:
        MotivationalMessage with AI-generated content
    """
    # Build prompt with user's specific data
    prompt = build_prompt_context(user_profile, streaks, recent_progress)

    # Determine tone from user profile
    tone = user_profile.get("communication_style", "encouraging")

    try:
        # Call Bedrock Claude
        response = bedrock_client.converse(
            modelId=model_id,
            messages=[
                {
                    "role": "user",
                    "content": [{"text": prompt}]
                }
            ],
            inferenceConfig={
                "maxTokens": 300,
                "temperature": 0.7  # Slightly creative for natural language
            }
        )

        # Extract generated message
        message_text = response["output"]["message"]["content"][0]["text"]

        # Extract highlights (achievements mentioned)
        highlights = []
        if streaks.nutrition_current_streak >= 7:
            highlights.append(f"{streaks.nutrition_current_streak}-day nutrition streak")
        if streaks.workout_current_streak >= 2:
            highlights.append(f"{streaks.workout_current_streak}-week workout consistency")

        return MotivationalMessage(
            message=message_text.strip(),
            tone=tone,
            highlights=highlights,
            generated_at=datetime.utcnow().isoformat(),
            model_used=model_id
        )

    except Exception as e:
        # Fallback message if AI generation fails
        print(f"Error generating motivational message: {e}")

        fallback_message = "Keep up the great work! Every day of tracking builds better habits."

        return MotivationalMessage(
            message=fallback_message,
            tone=tone,
            highlights=[],
            generated_at=datetime.utcnow().isoformat(),
            model_used="fallback"
        )
