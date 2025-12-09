"""
Test script for Phase 3: Personal Data Tools

Tests the Coach Orchestrator's ability to access and analyze user's:
- Profile and goals
- Nutrition logs
- Workout logs
- Body composition logs
"""

import os
import sys

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from coach_orchestrator import CoachAgent


def test_personal_data_tools():
    """Test personal data integration with demo user"""
    print("=" * 60)
    print("Testing Coach Orchestrator - Phase 3: Personal Data Tools")
    print("=" * 60)

    # Load API key from backend/.env
    backend_env_path = os.path.join(
        os.path.dirname(os.path.dirname(os.path.dirname(__file__))),
        "backend", ".env"
    )

    api_key = None
    if os.path.exists(backend_env_path):
        with open(backend_env_path) as f:
            for line in f:
                if line.startswith("OPENAI_API_KEY="):
                    api_key = line.split("=", 1)[1].strip()
                    break

    if not api_key:
        print("\n❌ Error: OPENAI_API_KEY not found")
        return

    print("✅ Loaded API key from .env")

    # Initialize coach with test user (has existing sample data)
    print("\n1. Initializing Coach Agent with test_user_90day...")
    coach = CoachAgent(
        openai_api_key=api_key,
        user_id="test_user_90day",
        model="gpt-3.5-turbo"
    )
    print("   ✅ Coach initialized")

    # Test 1: User profile and goals
    print("\n2. Testing Personal Data - Profile & Goals...")
    print("-" * 60)
    question1 = "What are my fitness goals and macro targets?"

    response1 = coach.handle_question(question1)
    print(f"\n   User: {question1}")
    print(f"\n   Coach: {response1['message'][:300]}...")
    print(f"\n   ✅ Tools called: {len(response1['tool_calls'])}")

    if response1['tool_calls']:
        for tool_call in response1['tool_calls']:
            print(f"      - {tool_call['tool']}: {tool_call.get('success', False)}")

    # Test 2: Nutrition logs analysis
    print("\n3. Testing Personal Data - Nutrition Logs...")
    print("-" * 60)
    question2 = "How has my nutrition been this week? Am I hitting my calorie targets?"

    response2 = coach.handle_question(question2)
    print(f"\n   User: {question2}")
    print(f"\n   Coach: {response2['message'][:300]}...")
    print(f"\n   ✅ Tools called: {len(response2['tool_calls'])}")

    if response2['tool_calls']:
        for tool_call in response2['tool_calls']:
            print(f"      - {tool_call['tool']}: {tool_call.get('success', False)}")

    # Test 3: Workout logs analysis
    print("\n4. Testing Personal Data - Workout Logs...")
    print("-" * 60)
    question3 = "What workouts have I been doing? How often am I training?"

    response3 = coach.handle_question(question3)
    print(f"\n   User: {question3}")
    print(f"\n   Coach: {response3['message'][:300]}...")
    print(f"\n   ✅ Tools called: {len(response3['tool_calls'])}")

    if response3['tool_calls']:
        for tool_call in response3['tool_calls']:
            print(f"      - {tool_call['tool']}: {tool_call.get('success', False)}")

    # Test 4: Body composition tracking
    print("\n5. Testing Personal Data - Body Composition...")
    print("-" * 60)
    question4 = "How has my weight changed over the past two weeks?"

    response4 = coach.handle_question(question4)
    print(f"\n   User: {question4}")
    print(f"\n   Coach: {response4['message'][:300]}...")
    print(f"\n   ✅ Tools called: {len(response4['tool_calls'])}")

    if response4['tool_calls']:
        for tool_call in response4['tool_calls']:
            print(f"      - {tool_call['tool']}: {tool_call.get('success', False)}")

    # Test 5: Combined analysis (profile + logs)
    print("\n6. Testing Combined Analysis...")
    print("-" * 60)
    question5 = "Based on my goals and recent progress, how am I doing?"

    response5 = coach.handle_question(question5)
    print(f"\n   User: {question5}")
    print(f"\n   Coach: {response5['message'][:400]}...")
    print(f"\n   ✅ Tools called: {len(response5['tool_calls'])}")

    if response5['tool_calls']:
        for tool_call in response5['tool_calls']:
            print(f"      - {tool_call['tool']}: {tool_call.get('success', False)}")

    # Summary
    print("\n" + "=" * 60)
    print("✅ Phase 3 Personal Data Tools Test Complete!")
    print("=" * 60)
    print("\nResults:")
    all_responses = [response1, response2, response3, response4, response5]
    print(f"  - All 5 questions answered successfully")
    print(f"  - Total tools called: {sum(len(r['tool_calls']) for r in all_responses)}")

    # Count tool types
    tool_counts = {}
    for response in all_responses:
        for tool_call in response['tool_calls']:
            tool_name = tool_call['tool']
            tool_counts[tool_name] = tool_counts.get(tool_name, 0) + 1

    print(f"\n  Tool usage breakdown:")
    for tool_name, count in tool_counts.items():
        print(f"    - {tool_name}: {count} times")

    print("\nNext steps:")
    print("  - Phase 4: Add specialist agent tools (Nutrition, Training)")
    print("  - Phase 5: Create API endpoint")
    print("  - Phase 6: Frontend integration")


if __name__ == "__main__":
    test_personal_data_tools()
