# Coach Orchestrator Implementation Plan
## Unified Personal + Evidence-Based AI Coach

---

## Overview

This plan outlines how to implement the Coach Orchestrator agent that combines:
1. **Personal coaching** - Analyzes user's workout/nutrition data
2. **Evidence-based knowledge** - Uses existing RAG system for general fitness questions
3. **Unified experience** - Single chatbot interface for both

---

## Current State

### ✅ Already Implemented

**RAG System (`backend/`):**
- `vector_store.py` - FAISS/OpenSearch vector storage
- `embeddings.py` - Bedrock Titan embeddings
- `retrieval.py` - HealthRAG class with `retrieve_context()`
- `upload_to_opensearch.py` - Vector store migration script

**Existing Chatbot (`frontend/`):**
- `app/chatbot/page.tsx` - Chat interface
- `components/health-chat.tsx` - Chat UI component
- API endpoint: `POST /chat` (currently not implemented in backend)

**Agent Infrastructure:**
- `ai_agents/nutrition_specialist/` - Nutrition analysis algorithms
- `ai_agents/training_specialist/` - Training analysis algorithms
- `backend/server.py` - FastAPI backend with `/api/nutrition/analyze` and `/api/training/weekly-summary` endpoints

### ❌ Missing for Coach Orchestrator

1. **OpenAI SDK integration** - No OpenAI client setup yet
2. **Function calling architecture** - No tool definitions or execution logic
3. **Coach agent module** - No `ai_agents/coach_orchestrator/` directory
4. **Unified API endpoint** - Need to replace/enhance existing `/chat` endpoint
5. **Tool implementations** - Functions to fetch user data and call specialist agents

---

## Implementation Phases

### Phase 1: Setup OpenAI SDK & Basic Structure
**Goal:** Get basic chat working with OpenAI SDK

**Tasks:**
1. Install OpenAI Python SDK
   ```bash
   cd backend
   pip install openai
   # Add to requirements.txt and requirements-lambda.txt
   ```

2. Add OpenAI API key to environment
   ```bash
   # .env
   OPENAI_API_KEY=sk-...
   ```

3. Create coach orchestrator module structure
   ```
   ai_agents/coach_orchestrator/
   ├── __init__.py
   ├── agent.py          # CoachAgent class with OpenAI SDK
   ├── tools.py          # Function tool definitions
   ├── prompts.py        # System prompts
   └── test_coach.py     # Unit tests
   ```

**Deliverable:** Basic chat that responds using OpenAI (no function calling yet)

---

### Phase 2: Implement Knowledge Base Tool (RAG Integration)
**Goal:** Coach can answer evidence-based questions using existing RAG

**Tasks:**
1. Create `search_knowledge_base` tool in `tools.py`
   ```python
   def search_knowledge_base(query: str, top_k: int = 5) -> dict:
       """Search fitness knowledge base using RAG"""
       from backend.retrieval import HealthRAG

       rag = HealthRAG(use_opensearch=True)  # or False for local dev
       context, sources = rag.retrieve_context(query, top_k)

       return {
           "context": context,
           "sources": sources
       }
   ```

2. Add RAG tool to OpenAI function definitions
   ```python
   {
       "type": "function",
       "function": {
           "name": "search_knowledge_base",
           "description": "Search evidence-based fitness/health knowledge...",
           "parameters": {
               "type": "object",
               "properties": {
                   "query": {"type": "string"},
                   "top_k": {"type": "integer", "default": 5}
               }
           }
       }
   }
   ```

3. Update system prompt to know when to use RAG
   ```python
   # prompts.py
   system_prompt = """...
   When users ask general fitness questions (not about their personal data):
   - Use search_knowledge_base() to find scientific research
   - Cite sources in your response
   - Provide evidence-based answers
   ...
   """
   ```

**Deliverable:** Coach can answer questions like "What's the optimal training volume?" using RAG

---

### Phase 3: Implement Personal Data Tools
**Goal:** Coach can access user's workout/nutrition data

**Tasks:**
1. Create data retrieval tools in `tools.py`
   ```python
   def get_user_profile(user_id: str) -> dict:
       """Get user profile from DynamoDB"""
       # Use existing database client
       from backend.database import DynamoDBClient
       db = DynamoDBClient()
       return db.get_user_profile(user_id)

   def get_nutrition_logs(user_id: str, days: int = 7) -> list:
       """Get recent nutrition logs"""
       # Query nutrition_logs table
       ...

   def get_workout_logs(user_id: str, days: int = 14) -> list:
       """Get recent workout logs"""
       # Query workout_logs table
       ...

   def get_body_logs(user_id: str, days: int = 14) -> list:
       """Get body composition logs"""
       # Query body_logs table
       ...
   ```

2. Add these tools to function definitions for OpenAI

3. Update system prompt to use personal data when relevant
   ```python
   system_prompt = """...
   When users ask about THEIR progress or data:
   - Use get_user_profile(), get_nutrition_logs(), etc.
   - Reference specific numbers from their logs
   - Provide personalized analysis
   ...
   """
   ```

**Deliverable:** Coach can answer "What's my average calorie intake this week?"

---

### Phase 4: Implement Specialist Agent Tools
**Goal:** Coach can call Nutrition/Training agents for analysis

**Tasks:**
1. Create specialist agent tools in `tools.py`
   ```python
   def get_nutrition_recommendation(user_id: str) -> dict:
       """Call Nutrition Specialist agent"""
       from ai_agents.nutrition_specialist.algorithm import apply_nutrition_algorithm
       from ai_agents.nutrition_specialist.trend_analysis import (
           analyze_weight_trend,
           analyze_body_composition_trend
       )

       # Gather data
       # Call algorithm
       # Return recommendation
       ...

   def get_training_status(user_id: str, exercise: str = None) -> dict:
       """Call Training Specialist agent"""
       from ai_agents.training_specialist.weekly_summary import publish_weekly_strength_summary

       # Get training data
       # Analyze progression
       # Return status
       ...
   ```

2. Add to function definitions

3. Update system prompt
   ```python
   system_prompt = """...
   When users ask "should I change my calories?" or "is my training working?":
   - Call the specialist agents (get_nutrition_recommendation, get_training_status)
   - Explain their recommendations in simple terms
   - You DON'T make these decisions - you explain what the specialists decided
   ...
   """
   ```

**Deliverable:** Coach can answer "Should I decrease my calories?" by calling Nutrition Agent

---

### Phase 5: Create Unified API Endpoint
**Goal:** Single `/api/coach/ask` endpoint that handles all questions

**Tasks:**
1. Implement in `backend/server.py`
   ```python
   from ai_agents.coach_orchestrator.agent import CoachAgent

   @app.post("/api/coach/ask")
   async def ask_coach(request: CoachRequest):
       """
       Unified coach endpoint - handles both personal and general questions

       Request:
           {
               "user_id": "user_123",
               "question": "Why did my calories change?",
               "thread_id": "thread_abc"  # optional
           }

       Response:
           {
               "response": "Your calories changed because...",
               "thread_id": "thread_abc",
               "sources": [...]  # if RAG was used
           }
       """
       coach = CoachAgent(
           openai_api_key=os.getenv('OPENAI_API_KEY'),
           user_id=request.user_id
       )

       result = coach.handle_question(
           question=request.question,
           thread_id=request.thread_id
       )

       return result
   ```

2. Handle backward compatibility
   - Keep existing `/chat` endpoint for now (or migrate it)
   - Or update frontend to use `/api/coach/ask` instead

**Deliverable:** Working API endpoint that routes between personal/general questions

---

### Phase 6: Update Frontend
**Goal:** Update chat UI to use new endpoint

**Tasks:**
1. Update `frontend/components/health-chat.tsx`
   ```typescript
   // Change from:
   const response = await fetch(`${API_URL}/chat`, ...);

   // To:
   const response = await fetch(`${API_URL}/api/coach/ask`, {
       method: 'POST',
       body: JSON.stringify({
           user_id: getCurrentUserId(),  // Get from localStorage
           question: userMessage.content,
           thread_id: threadId
       })
   });
   ```

2. Update UI to show sources when RAG is used
   ```typescript
   // Display sources at bottom of AI response
   {message.sources && message.sources.length > 0 && (
       <div className="mt-2 text-xs text-gray-500">
           <p>Sources:</p>
           {message.sources.map((source, i) => (
               <div key={i}>• {source.source}, Page {source.page}</div>
           ))}
       </div>
   )}
   ```

3. Update welcome message and examples
   ```typescript
   <p>Example questions:</p>
   <ul>
       <li>• Why did my calories change this week? (Personal)</li>
       <li>• Am I making progress? (Personal)</li>
       <li>• What's the optimal training volume? (General/RAG)</li>
       <li>• How should I structure my macros? (General/RAG)</li>
       <li>• Is body recomposition real? (Blended)</li>
   </ul>
   ```

**Deliverable:** Working chat UI that handles both types of questions seamlessly

---

### Phase 7: Testing & Refinement
**Goal:** Ensure all features work together

**Tasks:**
1. Unit tests for tools
   ```python
   # ai_agents/coach_orchestrator/test_coach.py
   def test_search_knowledge_base():
       result = search_knowledge_base("sleep optimization")
       assert "context" in result
       assert len(result["sources"]) > 0

   def test_get_user_profile():
       profile = get_user_profile("demo_user_90day")
       assert profile["user_id"] == "demo_user_90day"
   ```

2. Integration tests
   - Test personal data questions
   - Test general knowledge questions
   - Test blended questions
   - Test multi-turn conversations

3. Prompt refinement
   - Test various question phrasings
   - Ensure coach uses right tools
   - Check response quality

4. Cost monitoring
   - Log token usage per conversation
   - Optimize system prompts to reduce tokens
   - Consider GPT-3.5 for simple questions

**Deliverable:** Production-ready Coach Orchestrator

---

## File Structure After Implementation

```
fit-tracker/
├── ai_agents/
│   ├── coach_orchestrator/          # NEW
│   │   ├── __init__.py
│   │   ├── agent.py                 # CoachAgent with OpenAI SDK
│   │   ├── tools.py                 # All function tools
│   │   ├── prompts.py               # System prompts
│   │   └── test_coach.py            # Unit tests
│   ├── nutrition_specialist/
│   │   ├── algorithm.py             # EXISTING - used by coach
│   │   ├── tools.py
│   │   └── trend_analysis.py
│   ├── training_specialist/
│   │   ├── tools.py                 # EXISTING - used by coach
│   │   └── weekly_summary.py
│   └── shared/
│       └── models.py                # Pydantic models
│
├── backend/
│   ├── server.py                    # UPDATED - add /api/coach/ask
│   ├── retrieval.py                 # EXISTING - used by coach tools
│   ├── vector_store.py              # EXISTING
│   ├── embeddings.py                # EXISTING
│   ├── database.py                  # EXISTING - used by coach tools
│   ├── requirements.txt             # UPDATED - add openai
│   └── requirements-lambda.txt      # UPDATED - add openai
│
└── frontend/
    ├── app/chatbot/page.tsx         # EXISTING - no changes needed
    ├── components/health-chat.tsx   # UPDATED - use /api/coach/ask
    └── ...
```

---

## Example Tool Execution Flow

### Question: "My weight isn't changing. Is body recomp real?"

```
1. User sends question to /api/coach/ask

2. CoachAgent receives question
   - Initializes OpenAI conversation
   - System prompt tells it about available tools

3. OpenAI decides to call multiple tools:
   ├── get_body_logs(user_id, days=14)
   │   └── Returns: {weight stable, skinfolds down 4mm}
   ├── get_weekly_analysis(user_id)
   │   └── Returns: {body_composition_status: "recomp"}
   └── search_knowledge_base("body recomposition science")
       └── Returns: {context: "research on simultaneous fat loss + muscle gain..."}

4. OpenAI synthesizes response:
   - "YOUR data shows: weight stable, fat down, strength up"
   - "SCIENCE says: body recomp is real for intermediate lifters"
   - "CONCLUSION: You're in textbook body recomp!"

5. Response sent to user with sources
```

---

## Environment Variables Needed

```bash
# .env
OPENAI_API_KEY=sk-...                    # For Coach Orchestrator
AWS_ACCESS_KEY_ID=...                    # For OpenSearch/DynamoDB
AWS_SECRET_ACCESS_KEY=...
AWS_DEFAULT_REGION=us-east-1
OPENSEARCH_ENDPOINT=https://...          # For RAG
```

---

## Estimated Implementation Time

| Phase | Task | Time Estimate |
|-------|------|---------------|
| 1 | Setup OpenAI SDK & basic structure | 2-3 hours |
| 2 | RAG integration | 2-3 hours |
| 3 | Personal data tools | 3-4 hours |
| 4 | Specialist agent tools | 2-3 hours |
| 5 | API endpoint | 1-2 hours |
| 6 | Frontend updates | 2-3 hours |
| 7 | Testing & refinement | 3-4 hours |
| **Total** | | **15-22 hours** |

---

## Success Criteria

✅ **Functional Requirements:**
- [ ] Coach can answer general fitness questions using RAG
- [ ] Coach can answer personal questions using user data
- [ ] Coach can blend both in one conversation
- [ ] Nutrition/Training agent recommendations are explained clearly
- [ ] Sources are cited when using RAG
- [ ] Multi-turn conversations work (maintains context)

✅ **Non-Functional Requirements:**
- [ ] Response time < 5 seconds
- [ ] Cost < $0.05 per conversation
- [ ] Function calling accuracy > 95%
- [ ] User satisfaction > 4/5

---

## Next Steps

**Ready to start? Begin with Phase 1:**

```bash
# 1. Install OpenAI SDK
cd /Users/jundaqian/projects/fit-ai/fit-tracker/backend
pip install openai

# 2. Create coach orchestrator module
mkdir -p ../ai_agents/coach_orchestrator
cd ../ai_agents/coach_orchestrator
touch __init__.py agent.py tools.py prompts.py test_coach.py

# 3. Add OpenAI API key to .env
echo "OPENAI_API_KEY=sk-..." >> ../../.env
```

**Let me know when you're ready to implement Phase 1!**
