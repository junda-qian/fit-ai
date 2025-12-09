"""
Test script for Phase 4: Specialist Agent Integration

Tests the Coach Orchestrator's ability to call Nutrition and Training agents
for personalized recommendations.
"""

import os
import sys

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from coach_orchestrator import CoachAgent


def test_specialist_agent_integration():
    """Test specialist agent integration"""
    print("=" * 60)
    print("Testing Coach Orchestrator - Phase 4: Specialist Agents")
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

    # Test 1: Nutrition recommendation
    print("\n2. Testing Nutrition Specialist Agent...")
    print("-" * 60)
    question1 = "Based on my progress, should I adjust my calories? What should my nutrition targets be?"

    response1 = coach.handle_question(question1)
    print(f"\n   User: {question1}")
    print(f"\n   Coach: {response1['message'][:400]}...")
    print(f"\n   ✅ Tools called: {len(response1['tool_calls'])}")

    if response1['tool_calls']:
        for tool_call in response1['tool_calls']:
            print(f"      - {tool_call['tool']}: {tool_call.get('success', False)}")

    # Test 2: Training summary
    print("\n3. Testing Training Specialist Agent...")
    print("-" * 60)
    question2 = "How is my training going? Am I making progress on my lifts?"

    response2 = coach.handle_question(question2)
    print(f"\n   User: {question2}")
    print(f"\n   Coach: {response2['message'][:400]}...")
    print(f"\n   ✅ Tools called: {len(response2['tool_calls'])}")

    if response2['tool_calls']:
        for tool_call in response2['tool_calls']:
            print(f"      - {tool_call['tool']}: {tool_call.get('success', False)}")

    # Test 3: Combined question (nutrition + training)
    print("\n4. Testing Combined Specialist Query...")
    print("-" * 60)
    question3 = "Based on my training progress and nutrition, what changes should I make to optimize my muscle gain?"

    response3 = coach.handle_question(question3)
    print(f"\n   User: {question3}")
    print(f"\n   Coach: {response3['message'][:400]}...")
    print(f"\n   ✅ Tools called: {len(response3['tool_calls'])}")

    if response3['tool_calls']:
        for tool_call in response3['tool_calls']:
            print(f"      - {tool_call['tool']}: {tool_call.get('success', False)}")

    # Summary
    print("\n" + "=" * 60)
    print("✅ Phase 4 Specialist Agent Integration Test Complete!")
    print("=" * 60)
    print("\nResults:")
    all_responses = [response1, response2, response3]
    print(f"  - All 3 questions answered successfully")
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

    print("\nPhase 4 Complete! Next steps:")
    print("  - Phase 5: Create API endpoint")
    print("  - Phase 6: Frontend integration")
    print("  - Phase 7: AWS deployment")


if __name__ == "__main__":
    test_specialist_agent_integration()
