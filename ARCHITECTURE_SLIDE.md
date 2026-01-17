# FitTracker AI - System Architecture (Single Slide)

```
                            ┌──────────────┐
                            │    Users     │
                            └──────┬───────┘
                                   │
                    ┌──────────────┴──────────────┐
                    │                             │
            ┌───────▼────────┐          ┌────────▼──────────┐
            │ Amazon         │          │ Amazon API        │
            │ CloudFront     │          │ Gateway           │
            │ + S3 (Static)  │          │ (HTTP API)        │
            └────────────────┘          └────────┬──────────┘
                                                 │
                                        ┌────────▼─────────────┐
                                        │  AWS Lambda          │
                                        │  (FastAPI/Python 3.12)│
                                        └────────┬─────────────┘
                                                 │
                    ┌────────────────────────────┼─────────────────────────────┐
                    │                            │                             │
            ┌───────▼────────┐          ┌────────▼──────────┐        ┌────────▼─────────┐
            │  AI Agents     │          │  LLM Services     │        │  AWS Storage     │
            │  (on Lambda)   │          ├───────────────────┤        ├──────────────────┤
            ├────────────────┤          │ • OpenAI GPT-4    │        │ • Amazon         │
            │ • Coach        │◄────────►│ • Amazon Bedrock  │        │   DynamoDB (9)   │
            │ • Nutrition    │          │   (Nova Lite)     │        │ • Amazon S3      │
            │ • Training     │          │ • Amazon Bedrock  │        │   (3 buckets)    │
            └────────────────┘          │   Titan (Embed)   │        │ • OpenSearch     │
                                        └───────────────────┘        │   Serverless     │
                                                 │                   └──────────────────┘
                                        ┌────────▼──────────┐
                                        │ Amazon OpenSearch │
                                        │ Serverless        │
                                        │ (4,484 vectors)   │
                                        │ or FAISS (local)  │
                                        └───────────────────┘

Key Features:
• RAG-Powered Health Chatbot with 4,484 medical knowledge vectors
• Multi-Agent AI System (Coach, Nutrition, Training specialists)
• Real-time fitness & nutrition tracking across 9 DynamoDB tables
• Serverless architecture (Lambda + Bedrock + DynamoDB)
• Global CDN delivery via CloudFront
```

## Tech Stack Summary

| Layer | AWS Service / Technology | Purpose |
|-------|--------------------------|---------|
| **Frontend** | Next.js 15 + React 19 + TailwindCSS | Static web app |
| **CDN** | Amazon CloudFront | Global content delivery |
| **Frontend Storage** | Amazon S3 | Static website hosting |
| **API** | Amazon API Gateway (HTTP API) | RESTful endpoints |
| **Compute** | AWS Lambda (Python 3.12) | Serverless backend |
| **Framework** | FastAPI + Mangum | High-performance API |
| **AI/LLM** | OpenAI GPT-4 Turbo + Amazon Bedrock (Nova Lite) | Conversational AI |
| **Embeddings** | Amazon Bedrock (Titan V1 - 1536d) | Semantic search |
| **Vector DB** | Amazon OpenSearch Serverless / FAISS | RAG knowledge base |
| **Database** | Amazon DynamoDB (9 tables, Pay-per-request) | User data & logs |
| **Backend Storage** | Amazon S3 (2 buckets) | Conversation memory, RAG documents |
| **IaC** | Terraform | Infrastructure automation |
| **External** | USDA FoodData API | Nutrition database |

## AWS Resources Breakdown

| Resource Type | Service Name | Count | Usage |
|---------------|--------------|-------|-------|
| **Compute** | AWS Lambda | 1 function | Main API backend (247MB) |
| **Database** | Amazon DynamoDB | 9 tables | User profiles, logs, summaries |
| **Storage** | Amazon S3 | 3 buckets | Frontend hosting, Conversation memory, RAG documents |
| **CDN** | Amazon CloudFront | 1 distribution | Global content delivery |
| **API** | Amazon API Gateway | 1 HTTP API | 30+ REST endpoints |
| **Vector DB** | Amazon OpenSearch Serverless | 1 collection | Health knowledge (4,484 vectors) |
| **AI/ML** | Amazon Bedrock | 2 models | Nova Lite LLM + Titan Embeddings |
| **IAM** | IAM Role | 1 role | Lambda execution with policies |

## Features & User Journey

```
┌─────────────────────────────────────────────────────────────────────┐
│                    PHASE 1: INITIAL SETUP (AI-Powered)               │
└─────────────────────────────────────────────────────────────────────┘

┌──────────────────────────────────┐    ┌──────────────────────────────────┐
│    ENERGY CALCULATOR             │    │    WORKOUT PLANNER               │
│    (Bedrock Nova)                │    │    (Bedrock Nova)                │
├──────────────────────────────────┤    ├──────────────────────────────────┤
│ Analyzes:                        │    │ Analyzes:                        │
│ • Height, Weight, Age, Sex       │    │ • Training experience            │
│ • Activity level                 │    │ • Available equipment            │
│ • Body composition (BF%)         │    │ • Training frequency             │
│ • Goals (lose/gain/maintain)     │    │ • Goals & preferences            │
│                                  │    │                                  │
│ Calculates:                      │    │ Generates:                       │
│ • Baseline TDEE                  │    │ • Exercise selection             │
│ • Initial calorie target         │    │ • Sets & rep ranges              │
│ • Macro split (P/C/F)            │    │ • Progression model              │
│ • Starting point for tracking    │    │ • Weekly training split          │
└──────────────────────────────────┘    └──────────────────────────────────┘
                    │                                  │
                    └──────────────┬───────────────────┘
                                   ▼
                        User starts logging data

┌─────────────────────────────────────────────────────────────────────┐
│              PHASE 2: CONTINUOUS AI OPTIMIZATION                     │
└─────────────────────────────────────────────────────────────────────┘

┌────────────────────────┐  ┌────────────────────────┐  ┌────────────────────────┐
│  COACH ORCHESTRATOR    │  │  NUTRITION SPECIALIST  │  │  TRAINING SPECIALIST   │
│  (On-Demand)           │  │  (Weekly Scheduled)    │  │  (Dual-Trigger)        │
├────────────────────────┤  ├────────────────────────┤  ├────────────────────────┤
│ Trigger: User Q&A      │  │ Trigger: Mon 6AM UTC   │  │ Trigger 1: Post-Workout│
│ LLM: GPT-4 Turbo       │  │ LLM: Bedrock Nova      │  │ Trigger 2: Mon 5:55 UTC│
│                        │  │                        │  │ LLM: Bedrock Nova      │
├────────────────────────┤  ├────────────────────────┤  ├────────────────────────┤
│ Features:              │  │ Features:              │  │ Features:              │
│ • Natural language Q&A │  │ • Weekly analysis      │  │ • Session progression  │
│ • RAG health knowledge │  │ • Weight trend (14d)   │  │ • Linear/Rep Range     │
│ • Dynamic tool calling │  │ • Body composition     │  │ • Plateau detection    │
│ • Personal data access │  │ • Calorie adjustments  │  │ • Exercise tracking    │
│ • Agent orchestration  │  │ • Macro optimization   │  │ • Volume monitoring    │
│ • Conversation memory  │  │ • Maintenance estimate │  │ • Weekly trend summary │
└────────────────────────┘  └────────────────────────┘  └────────────────────────┘
         │                           │                           │
         └───────────────────────────┼───────────────────────────┘
                                     ▼
                    ┌────────────────────────────────┐
                    │   UNIFIED DATA ACCESS LAYER    │
                    │  • DynamoDB (9 tables)         │
                    │  • S3 Memory (conversations)   │
                    │  • Vector Store (RAG)          │
                    │  • USDA API (food database)    │
                    └────────────────────────────────┘

COMPLETE USER JOURNEY:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
1️⃣ Setup: Energy Calculator → Initial calorie & macro targets
2️⃣ Setup: Workout Planner → AI-generated personalized training plan
3️⃣ Action: User logs meals & workouts daily
4️⃣ Analysis: AI agents analyze trends and optimize recommendations
5️⃣ Guidance: Ask health questions anytime (RAG: 4,484 medical vectors)
6️⃣ Results: Evidence-based, continuously optimized fitness coaching
```
