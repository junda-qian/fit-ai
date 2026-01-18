# FitTracker AI - Complete Request Flow

This document explains how each AWS service and technology in the FitTracker stack works together to process user requests.

---

## Request Flow: Frontend → Backend

| Step | Service/Tech | What It Does | When It's Used |
|------|-------------|--------------|----------------|
| **1** | **Next.js 15 + React 19** | Static web application | User opens browser → Loads the app interface |
| **2** | **TailwindCSS** | Styling framework | Renders beautiful UI components |
| **3** | **Amazon CloudFront** | Global CDN | Delivers frontend files from edge locations (fast!) |
| **4** | **Amazon S3 (Frontend)** | Static file hosting | CloudFront fetches HTML/CSS/JS from S3 bucket |
| **5** | **User Action** | User clicks "Analyze Nutrition" | Browser prepares API request |
| **6** | **Amazon API Gateway** | HTTP API endpoint | Receives `/api/nutrition/analyze` request |
| **7** | **AWS Lambda** | Serverless compute | API Gateway invokes Lambda function |
| **8** | **Mangum** | ASGI adapter | Converts Lambda event → FastAPI format |
| **9** | **FastAPI** | Web framework | Routes request to `analyze_nutrition()` endpoint |
| **10** | **Python Code** | Business logic executes | Determines: need to call Nutrition Agent |
| **11a** | **Amazon Bedrock (Nova)** | LLM service | Calls Bedrock for nutrition analysis |
| **11b** | **OpenAI GPT-4** | LLM service (Coach only) | Or calls OpenAI for conversational AI |
| **12** | **Amazon DynamoDB** | NoSQL database | Fetches user's nutrition logs (past 14 days) |
| **13** | **Amazon Bedrock (Titan)** | Embeddings model | If RAG needed: converts query to vector |
| **14** | **Amazon OpenSearch** | Vector database | Searches similar health documents |
| **15** | **Amazon S3 (Memory)** | Conversation history | Loads/saves chat context |
| **16** | **USDA FoodData API** | External nutrition DB | If food search needed: queries USDA |
| **17** | **Amazon DynamoDB** | Database write | Saves analysis results/recommendations |
| **18** | **Response Flow** | ← Reverse path | Lambda → API Gateway → CloudFront → User |

---

## Detailed Flow Diagram

```
┌─────────────────────────────────────────────────────────────────┐
│ FRONTEND LAYER                                                  │
└─────────────────────────────────────────────────────────────────┘
User Browser
    ↓
[Next.js 15 + React 19 + TailwindCSS] ← Static web app
    ↓
Amazon CloudFront (CDN) ← Global content delivery
    ↓
Amazon S3 (Frontend bucket) ← Hosts HTML/CSS/JS files

┌─────────────────────────────────────────────────────────────────┐
│ API LAYER                                                       │
└─────────────────────────────────────────────────────────────────┘
User clicks "Analyze Nutrition"
    ↓
API Request: POST /api/nutrition/analyze
    ↓
Amazon API Gateway (HTTP API) ← Receives HTTP request
    ↓
Routes to Lambda function

┌─────────────────────────────────────────────────────────────────┐
│ COMPUTE LAYER (AWS Lambda - 247MB)                             │
└─────────────────────────────────────────────────────────────────┘
AWS Lambda (Python 3.12) ← Function invoked
    ↓
Mangum (ASGI adapter) ← Converts Lambda event
    ↓
FastAPI ← Routes to correct endpoint
    ↓
analyze_nutrition() function executes

┌─────────────────────────────────────────────────────────────────┐
│ DATA FETCHING LAYER                                            │
└─────────────────────────────────────────────────────────────────┘
Query Amazon DynamoDB (nutrition_logs table)
    ↓
Fetch last 14 days of nutrition data
    ↓
Load conversation context from S3 (memory bucket)

┌─────────────────────────────────────────────────────────────────┐
│ AI/ML LAYER                                                     │
└─────────────────────────────────────────────────────────────────┘
Call Amazon Bedrock (Nova Lite)
    ↓
LLM analyzes nutrition data + generates recommendations
    ↑
(If Coach Agent: Call OpenAI GPT-4 instead)
    ↑
(If health question: Use RAG)
    ├→ Amazon Bedrock (Titan) - Convert query to vector
    └→ Amazon OpenSearch Serverless - Find similar docs (4,484 vectors)

┌─────────────────────────────────────────────────────────────────┐
│ EXTERNAL INTEGRATION (if needed)                               │
└─────────────────────────────────────────────────────────────────┘
(If food search needed)
    ↓
Call USDA FoodData API ← External nutrition database

┌─────────────────────────────────────────────────────────────────┐
│ DATA PERSISTENCE LAYER                                         │
└─────────────────────────────────────────────────────────────────┘
Save results to:
    ├→ Amazon DynamoDB (nutrition recommendations)
    ├→ Amazon S3 (conversation memory)
    └→ Amazon DynamoDB (daily_summaries)

┌─────────────────────────────────────────────────────────────────┐
│ RESPONSE LAYER                                                  │
└─────────────────────────────────────────────────────────────────┘
FastAPI → Mangum → Lambda → API Gateway → CloudFront → User
```

---

## Infrastructure Management

| Service | Role |
|---------|------|
| **Terraform** | Defines all infrastructure as code - creates Lambda, DynamoDB, S3, CloudFront, API Gateway automatically |

---

## Complete Example: "Ask Coach a Health Question"

**User Question:** "Is it safe to workout while sore?"

```
1. User types: "Is it safe to workout while sore?"
   ↓
2. Next.js/React sends: POST /api/chat {"message": "..."}
   ↓
3. CloudFront → S3 (already loaded static app)
   ↓
4. API Gateway receives POST /api/chat
   ↓
5. Lambda invoked → Mangum → FastAPI → coach_agent.handle_question()
   ↓
6. Load conversation history from S3 (memory bucket)
   ↓
7. Query: "workout while sore" → Bedrock Titan (convert to 1536-d vector)
   ↓
8. OpenSearch finds similar medical documents (e.g., "DOMS recovery")
   ↓
9. Fetch user's recent workouts from DynamoDB (workout_logs)
   ↓
10. Send to OpenAI GPT-4:
    - Context: Retrieved medical docs
    - User data: Recent workout intensity
    - Question: "Is it safe?"
   ↓
11. GPT-4 generates personalized answer
   ↓
12. Save conversation to S3 (memory)
   ↓
13. Response: Lambda → API Gateway → CloudFront → User sees answer
```

---

## Key Architectural Patterns

### 1. **Monolithic Lambda**
- All backend code in one Lambda function (247MB)
- FastAPI handles internal routing
- Simpler deployment, faster cold starts

### 2. **Hybrid LLM Strategy**
- **OpenAI GPT-4**: Coach Agent (conversational, high-quality responses)
- **Amazon Bedrock Nova**: Nutrition/Training Agents (automated analysis, cost-effective)
- **Amazon Bedrock Titan**: Embeddings for RAG (AWS-native, integrated)

### 3. **RAG (Retrieval-Augmented Generation)**
- 4,484 medical documents embedded as vectors
- Semantic search prevents hallucinations
- Evidence-based health recommendations

### 4. **Multi-Agent Orchestration**
- **Coach Agent**: On-demand Q&A, tool orchestration
- **Nutrition Agent**: Weekly scheduled analysis
- **Training Agent**: Dual-trigger (post-workout + weekly)

### 5. **Data Flow**
- **Reads**: DynamoDB (structured data) + S3 (conversations) + OpenSearch (vectors)
- **Writes**: DynamoDB (logs, summaries) + S3 (memory)
- **External**: USDA API (nutrition data), OpenAI API (GPT-4), Bedrock API (Nova, Titan)

---

## Service Interaction Map

```
┌──────────────────────────────────────────────────────────────────┐
│                         USER                                     │
└────────────────────────┬─────────────────────────────────────────┘
                         │
        ┌────────────────┴────────────────┐
        │                                 │
  ┌─────▼──────┐                  ┌──────▼───────┐
  │ CloudFront │                  │ API Gateway  │
  │    (CDN)   │                  │  (HTTP API)  │
  └─────┬──────┘                  └──────┬───────┘
        │                                │
  ┌─────▼──────┐                  ┌──────▼───────────────────────┐
  │  S3        │                  │  AWS Lambda (247MB)          │
  │ (Frontend) │                  │  ┌────────────────────────┐  │
  └────────────┘                  │  │  Mangum → FastAPI      │  │
                                  │  └────────────────────────┘  │
                                  │  ┌────────────────────────┐  │
                                  │  │  AI Agents             │  │
                                  │  │  - Coach               │  │
                                  │  │  - Nutrition           │  │
                                  │  │  - Training            │  │
                                  │  └────────────────────────┘  │
                                  └──────┬───────────────────────┘
                                         │
            ┌────────────────────────────┼────────────────────────┐
            │                            │                        │
     ┌──────▼───────┐          ┌────────▼────────┐      ┌────────▼────────┐
     │  DynamoDB    │          │  S3             │      │  OpenSearch     │
     │  (9 tables)  │          │  (Memory/Docs)  │      │  (4,484 vectors)│
     └──────────────┘          └─────────────────┘      └─────────────────┘
            │                            │                        │
            └────────────────────────────┼────────────────────────┘
                                         │
                          ┌──────────────┴──────────────┐
                          │                             │
                   ┌──────▼───────┐          ┌─────────▼────────┐
                   │  Bedrock     │          │  OpenAI API      │
                   │  - Nova Lite │          │  - GPT-4 Turbo   │
                   │  - Titan     │          └──────────────────┘
                   └──────────────┘
                          │
                   ┌──────▼───────┐
                   │  USDA API    │
                   │  (External)  │
                   └──────────────┘
```

---

## Summary

This architecture demonstrates:
- **Serverless scalability**: Auto-scales from 0 to thousands of requests
- **Cost optimization**: Pay only for what you use (Lambda execution time, DynamoDB reads/writes)
- **AI-first design**: Multiple LLMs orchestrated for different use cases
- **Production-ready**: CloudFront CDN, proper data modeling, infrastructure as code
- **Modern stack**: Latest frontend (Next.js 15, React 19) + high-performance backend (FastAPI)

Every component plays a specific role in delivering personalized, AI-powered fitness coaching at scale.
