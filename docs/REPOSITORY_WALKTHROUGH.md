# FitTracker AI - Repository Walkthrough

## 🎯 What This App Does

**FitTracker AI** is a comprehensive AI-powered fitness coaching platform that combines:
- **Health chatbot** with RAG (4,484 medical knowledge vectors)
- **Nutrition tracking** with AI-powered analysis
- **Workout planning** and training optimization
- **Body composition monitoring**
- **Multi-agent AI system** for personalized coaching

## 📁 Repository Structure

```
fit-tracker/
├── 📱 FRONTEND (Next.js 15 + React 19)
│   ├── app/
│   │   ├── calculator/          # Energy/TDEE calculator
│   │   ├── chatbot/             # RAG health chatbot
│   │   ├── demo/                # Demo user view
│   │   ├── tracking/            # Nutrition, workouts, body logs
│   │   └── workout-planner/     # AI workout plan generator
│   ├── components/              # Reusable UI components
│   └── out/                     # Static export for S3

├── 🧠 AI_AGENTS (Multi-Agent System)
│   ├── coach_orchestrator/      # OpenAI GPT-4 - On-demand Q&A
│   ├── nutrition_specialist/    # Deterministic algorithms - NO LLM
│   ├── training_specialist/     # Deterministic algorithms - NO LLM
│   └── shared/                  # Common utilities

├── ⚙️ BACKEND (FastAPI + Python 3.12)
│   ├── server.py                # Main FastAPI server (30+ endpoints)
│   ├── lambda_handler.py        # Mangum adapter for Lambda
│   ├── database.py              # DynamoDB adapter
│   ├── dynamodb_adapter.py      # Table operations
│   ├── energy_calculator.py     # TDEE calculations (deterministic)
│   ├── workout_planner.py       # AI workout generation (Bedrock Nova)
│   ├── retrieval.py             # RAG system
│   ├── vector_store.py          # FAISS/OpenSearch integration
│   ├── food_database.py         # USDA API integration
│   ├── strength_standards.py    # 1RM calculations
│   ├── data/                    # Exercise data, muscle groups
│   ├── documents/               # Medical PDFs for RAG
│   └── lambda-package/          # Deployment package

├── 🏗️ TERRAFORM (Infrastructure as Code)
│   ├── main.tf                  # Core AWS resources
│   ├── dynamodb.tf              # 9 DynamoDB tables
│   ├── opensearch.tf            # Vector database
│   ├── variables.tf             # Configuration variables
│   └── outputs.tf               # Deployment outputs

├── 🚀 SCRIPTS (Deployment & Data Management)
│   ├── deploy.sh                # Full deployment automation
│   ├── destroy.sh               # Cleanup AWS resources
│   ├── generate_demo_data.py    # Create sample fitness data
│   ├── insert_sample_data_to_dynamodb.py
│   └── reset_demo_data.py       # Clean demo user data

├── 📚 DOCS (Specifications)
│   └── agents/
│       ├── COACH_ORCHESTRATOR_SPEC.md
│       ├── NUTRITION_AGENT_SPEC.md
│       └── TRAINING_AGENT_SPEC.md

└── 📖 DOCUMENTATION
    ├── README.md                # Project overview
    ├── ARCHITECTURE_SLIDE.md    # English architecture
    ├── ARCHITECTURE_SLIDE_JA.md # Japanese architecture
    └── REQUEST_FLOW.md          # Complete request flow
```

## 🤖 AI Agents System

### 1. **Coach Orchestrator** (ai_agents/coach_orchestrator/)
- **LLM**: OpenAI GPT-4 Turbo
- **Trigger**: On-demand (user asks questions)
- **Function**:
  - RAG-powered health Q&A
  - Dynamic tool calling
  - Orchestrates other agents
  - Conversation memory management
- **Tools**: Search knowledge base, get user data, call specialist agents

### 2. **Nutrition Specialist** (ai_agents/nutrition_specialist/)
- **LLM**: **NONE** - 100% deterministic Python algorithms
- **Trigger**: Weekly scheduled (Monday 6:00 AM UTC)
- **Function**:
  - Analyzes 14-day nutrition trends
  - Tracks weight changes & body composition
  - Adjusts calorie/macro targets using evidence-based tables
  - Estimates maintenance calories (pure math)
- **Algorithm**: Implements cutting/bulking tables as if/else logic
- **Data**: DynamoDB nutrition_logs, body_logs

### 3. **Training Specialist** (ai_agents/training_specialist/)
- **LLM**: **NONE** - 100% deterministic Python algorithms
- **Trigger**: **Dual-trigger**
  1. Post-workout (immediate feedback)
  2. Weekly scheduled (Monday 5:55 AM UTC)
- **Function**:
  - Session progression tracking (Linear Progressive & Rep Range models)
  - Plateau detection (algorithmic rules)
  - Reactive deload implementation
  - Weekly trend analysis
- **Algorithm**: Deterministic progression rules (hit reps → add weight, miss → deload)
- **Data**: DynamoDB workout_logs, user_exercises

## ☁️ AWS Infrastructure

### Core Services (Defined in `terraform/`)

**Compute:**
- **AWS Lambda** (1 function, 247MB)
  - Runtime: Python 3.12
  - Handler: Mangum (ASGI adapter for FastAPI)
  - Timeout: 120 seconds

**Storage:**
- **S3 Buckets** (3)
  - `frontend-*`: Static Next.js site
  - `memory-*`: Conversation history
  - `documents-*`: RAG medical PDFs + Lambda deployment zip
- **DynamoDB** (9 tables, pay-per-request)
  - user_profiles
  - workout_plans
  - nutrition_logs, workout_logs, body_logs
  - daily_summaries
  - user_exercises
  - training_recommendations
  - training_progress_summaries

**AI/ML:**
- **OpenAI API**: GPT-4 Turbo for Coach Orchestrator (main chatbot)
- **Amazon Bedrock**
  - Nova Lite: Workout plan generation only
  - Titan V1 (1536-d): Text embeddings for RAG
- **OpenSearch Serverless**: 4,484 medical knowledge vectors

**Networking:**
- **API Gateway** (HTTP API): 30+ RESTful endpoints
- **CloudFront**: Global CDN distribution

**Security:**
- **IAM Role**: Lambda execution with Bedrock, S3, DynamoDB access

## 🚀 Deployment Process

### 1. **Local Development**
```bash
# Backend
cd backend
uv run uvicorn server:app --reload  # localhost:8000

# Frontend
cd frontend
npm run dev  # localhost:3000
```

### 2. **AWS Deployment** (`scripts/deploy.sh`)

```bash
./scripts/deploy.sh dev  # or prod
```

**Steps:**
1. **Build Lambda Package** (`backend/deploy.py`)
   - Uses Docker with `public.ecr.aws/lambda/python:3.12`
   - Installs dependencies for Linux x86_64
   - Copies backend files + AI agents
   - Creates `lambda-deployment.zip` (~1.2GB)

2. **Terraform Apply** (`terraform/`)
   - Selects/creates workspace (dev/prod)
   - Provisions AWS resources
   - Uploads Lambda zip to S3 documents bucket
   - Creates Lambda function from S3 object

3. **Build Frontend** (`frontend/`)
   - Sets `NEXT_PUBLIC_API_URL` from Terraform output
   - Runs `npm run build` (static export)
   - Fixes directory structure for S3 routing
   - Syncs to S3 frontend bucket

4. **Outputs**
   - CloudFront URL: `https://d1gigxpg1cktct.cloudfront.net`
   - API Gateway: `https://qj0nsm3f9a.execute-api.us-east-1.amazonaws.com`

### 3. **Destroy** (`scripts/destroy.sh`)
```bash
./scripts/destroy.sh dev
```
- Empties all S3 buckets
- Runs `terraform destroy`
- Removes all AWS resources

## 🔄 Request Flow Example

**User Action:** "Ask Coach a health question"

```
Browser (Next.js)
  ↓ POST /api/coach/ask
CloudFront (CDN)
  ↓
API Gateway (HTTP API)
  ↓
AWS Lambda (247MB)
  ├→ Mangum converts event
  └→ FastAPI routes to /api/coach/ask endpoint
      ├→ Initialize Coach Orchestrator (OpenAI GPT-4)
      ├→ Load conversation thread
      ├→ Coach decides which tools to use:
      │   ├→ Search knowledge base (RAG)?
      │   │   ├→ Convert query → Bedrock Titan embedding (1536-d)
      │   │   └→ OpenSearch semantic search (top 5 medical docs)
      │   ├→ Get user data (nutrition/workout logs)?
      │   └→ Call specialist agents (Nutrition/Training)?
      ├→ Generate answer with OpenAI GPT-4
      ├→ Save thread to S3
      └→ Return response with sources/tool_calls
  ↓
API Gateway → CloudFront → Browser
```

## 🎨 Key Features

1. **Energy Calculator** (`/calculator`)
   - Deterministic TDEE calculation (Cunningham formula)
   - Macro targets (1.6g protein/kg, 30% fat)

2. **Workout Planner** (`/workout-planner`)
   - AI-powered (Bedrock Nova)
   - Constraint optimization (12 muscle groups, 50+ exercises)
   - Validates volume targets

3. **Nutrition Tracking** (`/tracking/nutrition`)
   - USDA food database integration
   - Daily calorie/macro logging
   - Algorithmic weekly analysis (deterministic, evidence-based)

4. **Training Tracking** (`/tracking/workouts`)
   - Exercise performance logging
   - 1RM calculations
   - Algorithmic progressive overload (Linear/Rep Range models)

5. **Health Chatbot** (`/chatbot`)
   - RAG with 4,484 medical vectors
   - Evidence-based answers only
   - Source citations

## 💰 Cost Optimization

- **DynamoDB**: Pay-per-request (no idle costs)
- **Lambda**: Charged per invocation (no servers)
- **S3**: Low storage costs
- **Deterministic Specialists**: Zero LLM costs for nutrition/training analysis
- **Bedrock Nova**: Used only for workout planner (cost-effective)
- **CloudFront**: Free tier (1TB/month)

## 🔧 Technology Stack

| Layer | Technology |
|-------|------------|
| **Frontend** | Next.js 15, React 19, TailwindCSS 4 |
| **Backend** | FastAPI, Python 3.12, Mangum |
| **AI** | OpenAI GPT-4, Bedrock Nova/Titan |
| **Database** | DynamoDB (9 tables) |
| **Vector DB** | OpenSearch Serverless / FAISS |
| **Storage** | S3 (3 buckets) |
| **CDN** | CloudFront |
| **IaC** | Terraform |
| **Package Manager** | uv (Python), npm |

---

This is a **production-ready, serverless, multi-agent AI fitness coaching platform** built entirely on AWS, demonstrating modern cloud architecture, AI orchestration, and full-stack development! 🚀
