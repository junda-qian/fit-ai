"""
Test script for Coach Orchestrator Agent

Run this to test basic functionality locally.
"""

import os
import sys

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from coach_orchestrator import CoachAgent


def test_basic_chat():
    """Test basic chat without function calling"""
    print("=" * 60)
    print("Testing Coach Orchestrator - Phase 1")
    print("=" * 60)

    # Load .env from backend directory
    backend_env_path = os.path.join(
        os.path.dirname(os.path.dirname(os.path.dirname(__file__))),
        "backend", ".env"
    )

    # Read API key from .env file
    api_key = None
    if os.path.exists(backend_env_path):
        with open(backend_env_path) as f:
            for line in f:
                if line.startswith("OPENAI_API_KEY="):
                    api_key = line.split("=", 1)[1].strip()
                    break

    # Also check environment variable
    if not api_key:
        api_key = os.getenv("OPENAI_API_KEY")

    if not api_key:
        print("\n❌ Error: OPENAI_API_KEY not found")
        print(f"   Looked in: {backend_env_path}")
        print("Please add it to backend/.env file:")
        print('OPENAI_API_KEY=sk-...')
        return

    print(f"✅ Loaded API key from .env")

    # Initialize coach
    print("\n1. Initializing Coach Agent...")
    try:
        coach = CoachAgent(
            openai_api_key=api_key,
            user_id="test_user",
            model="gpt-3.5-turbo"  # Use cheaper model for testing
        )
        print("    Coach initialized successfully")
    except Exception as e:
        print(f"   L Failed to initialize: {e}")
        return

    # Test simple question (no tools needed)
    print("\n2. Testing simple question...")
    question = "Hello! Can you introduce yourself as my fitness coach?"

    try:
        response = coach.handle_question(question)
        print(f"\n   User: {question}")
        print(f"\n   Coach: {response['message']}")
        print(f"\n    Response received successfully")
        print(f"   Tools called: {len(response['tool_calls'])}")
    except Exception as e:
        print(f"   L Failed to get response: {e}")
        import traceback
        traceback.print_exc()
        return

    # Test another question
    print("\n3. Testing fitness knowledge question...")
    question2 = "What are the main principles of progressive overload?"

    try:
        response2 = coach.handle_question(question2)
        print(f"\n   User: {question2}")
        print(f"\n   Coach: {response2['message'][:200]}...")  # First 200 chars
        print(f"\n    Response received successfully")
    except Exception as e:
        print(f"   L Failed to get response: {e}")
        return

    print("\n" + "=" * 60)
    print(" Phase 1 Test Complete!")
    print("=" * 60)
    print("\nNext steps:")
    print("- Phase 2: Implement RAG integration")
    print("- Phase 3: Add personal data tools")
    print("- Phase 4: Add specialist agent tools")


if __name__ == "__main__":
    test_basic_chat()
