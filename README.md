# FitTracker AI

A comprehensive AI-powered fitness coaching platform that provides personalized nutrition guidance, workout planning, training optimization, and evidence-based health information through a multi-agent system.

## Overview

FitTracker AI combines multiple specialized AI agents with deterministic algorithms to deliver personalized fitness coaching at scale. Built on AWS serverless infrastructure, it provides:

- **AI Health Coach** - RAG-powered chatbot with 4,484 medical knowledge vectors
- **Workout Planner** - Intelligent program generation using constraint optimization
- **Nutrition Tracking** - Automated analysis with evidence-based recommendations
- **Training Optimization** - Progressive overload tracking and plateau detection
- **Motivational Coaching** - Streak tracking and personalized encouragement
- **Energy Calculator** - TDEE and macro target calculations
- **Progress Monitoring** - Body composition and performance tracking

## Architecture

### Multi-Agent System

**Coach Orchestrator** (`ai_agents/coach_orchestrator/`)
- **LLM**: OpenAI GPT-4 Turbo
- **Purpose**: Conversational Q&A, tool orchestration, health information retrieval
- **Trigger**: On-demand (user-initiated)
- **Key Features**:
  - RAG with 4,484 medical document vectors
  - Dynamic tool calling
  - Conversation memory management
  - Orchestrates specialist agents

**Nutrition Specialist** (`ai_agents/nutrition_specialist/`)
- **LLM**: None (100% deterministic algorithms)
- **Purpose**: Analyzes nutrition trends, adjusts calorie/macro targets
- **Trigger**: Weekly scheduled (Monday 6:00 AM UTC)
- **Algorithm**: Evidence-based cutting/bulking tables implemented as pure logic
- **Data Sources**: nutrition_logs, body_logs tables

**Training Specialist** (`ai_agents/training_specialist/`)
- **LLM**: None (100% deterministic algorithms)
- **Purpose**: Progressive overload tracking, plateau detection, deload implementation
- **Trigger**: Dual (post-workout + weekly scheduled)
- **Models**: Linear Progressive & Rep Range progression
- **Data Sources**: workout_logs, user_exercises tables

**Motivator Specialist** (`ai_agents/motivator_specialist/`)
- **LLM**: AWS Bedrock Claude 3.5 Sonnet (message generation only)
- **Purpose**: Streak tracking and personalized motivation
- **Trigger**: Daily scheduled
- **Hybrid Approach**: Deterministic streak calculation + AI-powered messaging
- **Tracks**: Nutrition logging streaks, workout adherence streaks

### Workout Planner

Two implementation methods available:

**Deterministic Algorithm** (Recommended)
- Pure constraint satisfaction optimization
- Speed: 1-2ms (100-5000x faster than LLM)
- Cost: $0.00
- Accuracy: ~25% muscles within exact target, excellent balance
- Benefits: Deterministic, no outliers, explainable

**LLM-Based** (Fallback)
- AWS Bedrock Nova Lite with iterative validation
- Speed: 3-10 seconds
- Cost: $0.01-0.05 per plan
- Use case: Edge cases, creative variations

See `docs/WORKOUT_PLANNER_COMPARISON.md` for detailed analysis.

### Technology Stack

| Component | Technology |
|-----------|-----------|
| **Frontend** | Next.js 15, React 19, TailwindCSS 4 |
| **Backend** | FastAPI, Python 3.12, Mangum (ASGI adapter) |
| **AI/ML** | OpenAI GPT-4, AWS Bedrock (Nova, Claude, Titan) |
| **Vector DB** | OpenSearch Serverless (production) / FAISS (local) |
| **Database** | Amazon DynamoDB (9 tables, pay-per-request) |
| **Storage** | Amazon S3 (3 buckets: frontend, memory, documents) |
| **CDN** | Amazon CloudFront |
| **API** | Amazon API Gateway (HTTP API) |
| **Compute** | AWS Lambda (247MB, Python 3.12) |
| **IaC** | Terraform |
| **Package Managers** | uv (Python), npm (Node.js) |

## Quick Start

### Prerequisites

- Python 3.12+
- Node.js 20+
- AWS Account with Bedrock access
- Docker (for Lambda packaging)
- Terraform (for infrastructure deployment)
- OpenAI API key

### Local Development

#### 1. Backend Setup

```bash
cd backend

# Install uv (Python package manager)
curl -LsSf https://astral.sh/uv/install.sh | sh

# Initialize Python environment
uv init --bare
uv python pin 3.12
uv add -r requirements.txt
```

#### 2. Configure Environment

Create `backend/.env`:

```bash
# AWS Configuration
DEFAULT_AWS_REGION=us-east-1

# OpenSearch (set to false for local FAISS)
USE_OPENSEARCH=false

# S3 Storage (set to false for local files)
USE_S3=false

# Bedrock Models
BEDROCK_MODEL_ID=amazon.nova-lite-v1:0
BEDROCK_EMBEDDING_MODEL=amazon.titan-embed-text-v1

# OpenAI (for Coach Orchestrator)
OPENAI_API_KEY=your-key-here

# CORS (for local development)
CORS_ORIGINS=http://localhost:3000
```

#### 3. Add Medical Documents (Optional)

For RAG functionality, place PDF health documents in `backend/documents/`:

```bash
backend/documents/
├── medical_textbook_1.pdf
├── health_guidelines.pdf
└── research_papers.pdf
```

#### 4. Ingest Documents

```bash
cd backend
aws configure  # Set up AWS credentials
uv run python ingest_documents.py
```

This creates embeddings using AWS Bedrock Titan and stores vectors in FAISS (local) or OpenSearch (production).

#### 5. Start Backend Server

```bash
cd backend
uv run uvicorn server:app --reload
```

Server runs at: http://localhost:8000

#### 6. Start Frontend

```bash
cd frontend
npm install
npm run dev
```

Frontend runs at: http://localhost:3000

## Project Structure

```
fit-tracker/
├── frontend/                    # Next.js 15 application
│   ├── app/
│   │   ├── calculator/         # TDEE calculator
│   │   ├── chatbot/            # Health chatbot interface
│   │   ├── demo/               # Demo user view
│   │   ├── tracking/           # Nutrition, workouts, progress, weight
│   │   └── workout-planner/    # Workout plan generator
│   └── components/             # Reusable UI components
│
├── backend/                     # FastAPI server
│   ├── server.py               # Main API (30+ endpoints)
│   ├── lambda_handler.py       # Mangum adapter for Lambda
│   ├── database.py             # DynamoDB operations
│   ├── energy_calculator.py    # TDEE calculations
│   ├── workout_planner.py      # LLM-based planner
│   ├── workout_planner_deterministic.py  # Algorithm-based planner
│   ├── retrieval.py            # RAG implementation
│   ├── vector_store.py         # FAISS/OpenSearch interface
│   ├── food_database.py        # USDA API integration
│   ├── strength_standards.py   # 1RM calculations
│   ├── data/                   # Exercise database, muscle groups
│   └── documents/              # Medical PDFs for RAG
│
├── ai_agents/                   # Multi-agent system
│   ├── coach_orchestrator/     # OpenAI GPT-4 Q&A agent
│   ├── nutrition_specialist/   # Deterministic nutrition analysis
│   ├── training_specialist/    # Deterministic training optimization
│   ├── motivator_specialist/   # Hybrid streak tracking + motivation
│   └── shared/                 # Common utilities and models
│
├── terraform/                   # Infrastructure as Code
│   ├── main.tf                 # Core AWS resources
│   ├── dynamodb.tf             # 9 DynamoDB tables
│   ├── opensearch.tf           # Vector database
│   ├── variables.tf            # Configuration
│   └── outputs.tf              # Deployment outputs
│
├── scripts/                     # Deployment & utilities
│   ├── deploy.sh               # Full deployment automation
│   ├── destroy.sh              # Clean up AWS resources
│   └── generate_demo_data.py   # Create sample data
│
├── docs/                        # Technical documentation
│   ├── ARCHITECTURE.md
│   ├── WORKOUT_PLANNER_COMPARISON.md
│   └── agents/                 # Agent specifications
│
├── guides/                      # Implementation guides
│   ├── coach-orchestrator-guide.md
│   ├── nutrition-specialist-guide.md
│   ├── training-specialist-guide.md
│   ├── motivator-specialist-guide.md
│   ├── workout-planner-guide.md
│   ├── energy-calculator-guide.md
│   ├── DYNAMODB_EXPLAINED.md
│   ├── OPENSEARCH_RAG_EXPLAINED.md
│   ├── NEXTJS_EXPLAINED.md
│   └── TERRAFORM_EXPLAINED.md
│
├── data/                        # User data (local development)
│   └── tracking/
│       ├── user_profiles.json
│       ├── nutrition_logs.json
│       ├── workout_logs.json
│       ├── body_logs.json
│       └── daily_summaries.json
│
├── REPOSITORY_WALKTHROUGH.md    # High-level overview
├── REQUEST_FLOW.md              # Complete request flow diagram
└── README.md                    # This file
```

## Key Features

### 1. Energy Calculator (`/calculator`)
- **TDEE Calculation**: Cunningham formula based on lean body mass
- **Macro Targets**: 1.6g protein/kg, 30% fat, remainder carbs
- **100% Deterministic**: No AI, pure mathematical formulas
- **Evidence-Based**: Uses scientifically validated equations

### 2. Workout Planner (`/workout-planner`)
- **Dual Methods**: Choose between deterministic algorithm or LLM
- **Smart Optimization**: Balances volume across 12 muscle groups
- **Exercise Database**: 47 exercises with activation matrices
- **Intensity Scaling**: Adapts to training status (novice to advanced)
- **Validation**: Ensures safe, effective programs

### 3. Nutrition Tracking (`/tracking/nutrition`)
- **USDA Integration**: 300,000+ foods searchable
- **Macro Tracking**: Calories, protein, carbs, fat
- **AI Analysis**: Weekly automated nutrition review
- **Target Adjustment**: Dynamic calorie/macro updates based on progress
- **Trend Analysis**: 14-day rolling windows

### 4. Training Tracking (`/tracking/workouts`)
- **Exercise Logging**: Sets, reps, weight, RPE, rest
- **1RM Calculation**: Multiple formulas (Epley, Brzycki)
- **Progressive Overload**: Automatic progression tracking
- **Plateau Detection**: Algorithm identifies stalls
- **Deload Management**: Reactive fatigue management

### 5. Progress Monitoring (`/tracking/progress`)
- **Body Composition**: Weight, body fat %, lean mass
- **Visual Trends**: Charts for all metrics
- **Photo Tracking**: Progress photos over time
- **Measurements**: Chest, waist, arms, legs, etc.

### 6. Health Chatbot (`/chatbot`)
- **RAG Architecture**: 4,484 medical knowledge vectors
- **Evidence-Based**: Only answers from medical documents
- **Source Citations**: Links to original sources
- **Conversation Memory**: Context-aware responses
- **Medical Disclaimers**: Appropriate health warnings

### 7. Motivational Coaching
- **Streak Tracking**: Nutrition logging, workout adherence
- **Personalized Messages**: AI-generated encouragement
- **Consistency Metrics**: Daily and weekly tracking
- **Accountability**: Visual progress indicators

## AWS Deployment

### Deploy to AWS

```bash
# Deploy to dev environment
./scripts/deploy.sh dev

# Deploy to production
./scripts/deploy.sh prod
```

The deployment script:
1. Builds Lambda package using Docker (Linux x86_64 binaries)
2. Provisions AWS resources with Terraform
3. Builds and deploys frontend to S3
4. Configures CloudFront distribution

### AWS Services Used

- **AWS Lambda**: Serverless compute (247MB function)
- **API Gateway**: HTTP API (30+ endpoints)
- **DynamoDB**: NoSQL database (9 tables)
- **S3**: Static hosting + conversation memory + documents
- **CloudFront**: Global CDN
- **OpenSearch Serverless**: Vector database (4,484 vectors)
- **Bedrock**: AI models (Nova, Claude, Titan)
- **IAM**: Roles and permissions

### Cost Optimization

- **DynamoDB**: Pay-per-request (no idle costs)
- **Lambda**: Only charged during execution
- **S3**: Low storage costs
- **CloudFront**: Free tier covers most usage
- **Bedrock Nova**: Cost-effective LLM for workout planning
- **Deterministic Agents**: Zero LLM costs for nutrition/training analysis

## API Endpoints

### Health & Info
- `GET /health` - Health check
- `GET /stats` - RAG vector store statistics

### Coach Orchestrator
- `POST /api/coach/ask` - Ask health questions
- `POST /api/coach/clear-memory` - Clear conversation history

### Energy Calculator
- `POST /api/calculate-energy` - Calculate TDEE and macros

### Workout Planner
- `POST /api/workout-planner` - Generate workout plan

### User Management
- `GET /api/users/{user_id}` - Get user profile
- `POST /api/users` - Create user profile
- `PUT /api/users/{user_id}` - Update user profile

### Nutrition
- `GET /api/nutrition/{user_id}/logs` - Get nutrition logs
- `POST /api/nutrition/{user_id}/logs` - Add nutrition log
- `GET /api/nutrition/search-foods` - Search USDA database

### Training
- `GET /api/workouts/{user_id}/logs` - Get workout logs
- `POST /api/workouts/{user_id}/logs` - Add workout log
- `GET /api/workouts/{user_id}/exercises` - Get user exercises
- `POST /api/workouts/{user_id}/exercises` - Add custom exercise

### Body Logs
- `GET /api/body/{user_id}/logs` - Get body measurements
- `POST /api/body/{user_id}/logs` - Add body log

### Progress
- `GET /api/progress/{user_id}` - Get progress summary

## Testing

### Test Backend API

```bash
# Health check
curl http://localhost:8000/health

# RAG stats
curl http://localhost:8000/stats

# Chat with coach
curl -X POST http://localhost:8000/api/coach/ask \
  -H "Content-Type: application/json" \
  -d '{"user_id": "demo", "message": "What are symptoms of dehydration?"}'

# Calculate TDEE
curl -X POST http://localhost:8000/api/calculate-energy \
  -H "Content-Type: application/json" \
  -d '{
    "weight_kg": 75,
    "body_fat_percentage": 15,
    "activity_level": "moderately_active"
  }'
```

### Run Workout Planner Tests

```bash
cd backend
python test_workout_planner_comparison.py
```

This runs comparison tests between LLM and deterministic planners.

## Documentation

Comprehensive guides are available in the `guides/` directory:

- **[Coach Orchestrator Guide](guides/coach-orchestrator-guide.md)** - How the main AI coach works
- **[Nutrition Specialist Guide](guides/nutrition-specialist-guide.md)** - Deterministic nutrition analysis
- **[Training Specialist Guide](guides/training-specialist-guide.md)** - Progressive overload algorithms
- **[Motivator Specialist Guide](guides/motivator-specialist-guide.md)** - Streak tracking and motivation
- **[Workout Planner Guide](guides/workout-planner-guide.md)** - Algorithm and LLM comparison
- **[Energy Calculator Guide](guides/energy-calculator-guide.md)** - TDEE formulas explained
- **[DynamoDB Explained](guides/DYNAMODB_EXPLAINED.md)** - Database schema and design
- **[OpenSearch RAG Explained](guides/OPENSEARCH_RAG_EXPLAINED.md)** - Vector search implementation
- **[Next.js Explained](guides/NEXTJS_EXPLAINED.md)** - Frontend architecture
- **[Terraform Explained](guides/TERRAFORM_EXPLAINED.md)** - Infrastructure as code

Additional documentation:
- **[Repository Walkthrough](REPOSITORY_WALKTHROUGH.md)** - High-level overview of the entire project
- **[Request Flow](REQUEST_FLOW.md)** - Complete request flow diagrams
- **[Architecture](docs/ARCHITECTURE.md)** - System architecture documentation
- **[Workout Planner Comparison](docs/WORKOUT_PLANNER_COMPARISON.md)** - LLM vs Algorithm analysis

## Security & Disclaimers

### Medical Disclaimer

**This application provides educational information only and does NOT:**
- Diagnose medical conditions
- Prescribe treatments or supplements
- Replace professional medical advice
- Handle medical emergencies

Always consult qualified healthcare professionals and certified trainers for personalized medical and fitness advice.

### Data Privacy

- Conversations and user data stored in DynamoDB and S3
- No PHI (Protected Health Information) collection
- HIPAA compliance not guaranteed
- Use for educational and personal fitness tracking only

### Security Best Practices

1. Never commit `.env` files or AWS credentials
2. Restrict CORS in production environments
3. Use IAM roles with minimum required permissions
4. Enable encryption for S3 buckets and DynamoDB tables
5. Regular security audits of dependencies
6. Rotate API keys periodically

## Troubleshooting

### "No documents found" for RAG

- Ensure PDFs are in `backend/documents/`
- Run `ingest_documents.py` to populate vector store
- Check PDF format (not scanned images)

### "Bedrock access denied"

```bash
# Check AWS credentials
aws sts get-caller-identity

# Verify Bedrock model access
aws bedrock list-foundation-models --region us-east-1
```

### "DynamoDB table not found"

- Run Terraform to create tables: `cd terraform && terraform apply`
- Or use local JSON files by setting `USE_DYNAMODB=false`

### Frontend build errors

```bash
cd frontend
rm -rf .next node_modules
npm install
npm run build
```

## Contributing

Contributions are welcome! Areas for improvement:

1. **Additional AI Agents**: Sleep tracking, stress management, meal planning
2. **Mobile App**: React Native or Flutter implementation
3. **Social Features**: Community challenges, friend tracking
4. **Advanced Analytics**: Machine learning for injury prediction
5. **Integration**: Wearables (Apple Watch, Fitbit, Garmin)
6. **Internationalization**: Multi-language support
7. **Enhanced RAG**: More medical documents, better chunking

## License

This project is licensed under the MIT License - see the [LICENSE.txt](LICENSE.txt) file for details.

## Acknowledgments

- Exercise database inspired by Renaissance Periodization principles
- TDEE formulas based on peer-reviewed research
- RAG architecture using AWS Bedrock and OpenSearch
- Frontend built with modern React and Next.js best practices

---

**Built with** Python, FastAPI, Next.js, AWS, Terraform, OpenAI, and lots of fitness science.

For detailed technical information, see [REPOSITORY_WALKTHROUGH.md](REPOSITORY_WALKTHROUGH.md) and [REQUEST_FLOW.md](REQUEST_FLOW.md).
