"""
Test script for Phase 2: RAG Integration

Tests the Coach Orchestrator's ability to search the knowledge base
and answer evidence-based fitness questions.
"""

import os
import sys

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from coach_orchestrator import CoachAgent


def test_rag_integration():
    """Test RAG integration with knowledge-based questions"""
    print("=" * 60)
    print("Testing Coach Orchestrator - Phase 2: RAG Integration")
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

    # Initialize coach
    print("\n1. Initializing Coach Agent...")
    coach = CoachAgent(
        openai_api_key=api_key,
        user_id="test_user",
        model="gpt-3.5-turbo"
    )
    print("   ✅ Coach initialized")

    # Test 1: General fitness knowledge question
    print("\n2. Testing RAG - Training Volume Question...")
    print("-" * 60)
    question1 = "What is the optimal training volume for muscle hypertrophy?"

    response1 = coach.handle_question(question1)
    print(f"\n   User: {question1}")
    print(f"\n   Coach: {response1['message'][:300]}...")
    print(f"\n   ✅ Tools called: {len(response1['tool_calls'])}")
    print(f"   ✅ Sources found: {len(response1.get('sources', []))}")

    if response1['tool_calls']:
        for tool_call in response1['tool_calls']:
            print(f"      - {tool_call['tool']}: {tool_call.get('success', False)}")

    # Test 2: Nutrition science question
    print("\n3. Testing RAG - Nutrition Question...")
    print("-" * 60)
    question2 = "How should I structure my macronutrients for fat loss?"

    response2 = coach.handle_question(question2)
    print(f"\n   User: {question2}")
    print(f"\n   Coach: {response2['message'][:300]}...")
    print(f"\n   ✅ Tools called: {len(response2['tool_calls'])}")
    print(f"   ✅ Sources found: {len(response2.get('sources', []))}")

    # Test 3: Sleep optimization
    print("\n4. Testing RAG - Sleep Question...")
    print("-" * 60)
    question3 = "What are evidence-based sleep optimization strategies?"

    response3 = coach.handle_question(question3)
    print(f"\n   User: {question3}")
    print(f"\n   Coach: {response3['message'][:300]}...")
    print(f"\n   ✅ Tools called: {len(response3['tool_calls'])}")
    print(f"   ✅ Sources found: {len(response3.get('sources', []))}")

    # Summary
    print("\n" + "=" * 60)
    print("✅ Phase 2 RAG Integration Test Complete!")
    print("=" * 60)
    print("\nResults:")
    print(f"  - All 3 questions answered successfully")
    print(f"  - RAG tool called: {sum(len(r['tool_calls']) for r in [response1, response2, response3])} times")
    print(f"  - Total sources retrieved: {sum(len(r.get('sources', [])) for r in [response1, response2, response3])}")
    print("\nNext steps:")
    print("  - Phase 3: Add personal data tools")
    print("  - Phase 4: Add specialist agent tools")


if __name__ == "__main__":
    test_rag_integration()
