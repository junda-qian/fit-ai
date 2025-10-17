# 🏗️ Architecture Documentation

## Evidence-Based Fitness Chatbot & Energy Calculator

A full-stack SaaS application deployed on AWS, combining RAG-powered AI chatbot with evidence-based fitness calculations.

---

## 📋 Table of Contents

- [System Overview](#system-overview)
- [Tech Stack](#tech-stack)
- [Architecture Diagrams](#architecture-diagrams)
- [Component Details](#component-details)
- [Data Flow](#data-flow)
- [AWS Infrastructure](#aws-infrastructure)
- [Security](#security)
- [Deployment](#deployment)

---

## 🎯 System Overview

### Features
1. **RAG-Powered Fitness Chatbot**
   - Evidence-based responses from scientific fitness PDFs
   - AWS Bedrock Nova LLM
   - Vector semantic search
   - Conversation memory

2. **Energy Intake Calculator**
   - Cunningham BMR calculations
   - Training-aware energy expenditure
   - Personalized nutrition targets

### Architecture Pattern
- **Frontend**: Static SPA (Next.js)
- **Backend**: Serverless API (AWS Lambda + FastAPI)
- **AI/ML**: AWS Bedrock (Nova + Titan)
- **Storage**: S3 + OpenSearch Serverless
- **Infrastructure**: Terraform (IaC)

---

## 🛠️ Tech Stack

### Backend
```
┌─────────────────────────────────────────┐
│           Backend Stack                 │
├─────────────────────────────────────────┤
│ • FastAPI         - Web framework       │
│ • Python 3.12     - Runtime             │
│ • boto3           - AWS SDK             │
│ • langchain       - RAG orchestration   │
│ • pypdf           - PDF processing      │
│ • faiss-cpu       - Local vector DB     │
│ • opensearch-py   - Production vector DB│
│ • mangum          - Lambda ASGI adapter │
└─────────────────────────────────────────┘
```

### Frontend
```
┌─────────────────────────────────────────┐
│           Frontend Stack                │
├─────────────────────────────────────────┤
│ • Next.js 15.5.4  - React framework     │
│ • React 19        - UI library          │
│ • TypeScript      - Type safety         │
│ • Tailwind CSS v4 - Styling             │
│ • Lucide React    - Icons               │
└─────────────────────────────────────────┘
```

### AWS Services
```
┌─────────────────────────────────────────┐
│            AWS Services                 │
├─────────────────────────────────────────┤
│ • Lambda              - Compute         │
│ • API Gateway         - HTTP API        │
│ • S3                  - Storage         │
│ • CloudFront          - CDN             │
│ • Bedrock             - AI/LLM          │
│ • OpenSearch          - Vector DB       │
│ • Route53             - DNS (optional)  │
│ • ACM                 - SSL certs       │
└─────────────────────────────────────────┘
```

---

## 📐 Architecture Diagrams

### High-Level System Architecture

```
┌─────────────────────────────────────────────────────────────────────┐
│                           USER BROWSER                               │
└────────────────────────────────┬────────────────────────────────────┘
                                 │
                                 ▼
                    ┌────────────────────────┐
                    │   CloudFront (CDN)     │
                    │   Global Distribution   │
                    └───────────┬────────────┘
                                │
                ┌───────────────┴───────────────┐
                │                               │
                ▼                               ▼
    ┌──────────────────────┐        ┌──────────────────────┐
    │  S3 Static Website   │        │   API Gateway        │
    │  (Next.js Frontend)  │        │   (HTTP API)         │
    └──────────────────────┘        └──────────┬───────────┘
                                               │
                                               ▼
                                    ┌──────────────────────┐
                                    │   Lambda Function    │
                                    │   (FastAPI + Mangum) │
                                    └──────────┬───────────┘
                                               │
                ┌──────────────────────────────┼──────────────────────┐
                │                              │                      │
                ▼                              ▼                      ▼
    ┌──────────────────────┐      ┌──────────────────────┐  ┌────────────────┐
    │   AWS Bedrock        │      │  OpenSearch          │  │  S3 Buckets    │
    │   • Nova LLM         │      │  Serverless          │  │  • Documents   │
    │   • Titan Embeddings │      │  (Vector Database)   │  │  • Memory      │
    └──────────────────────┘      └──────────────────────┘  └────────────────┘
```

### RAG Chatbot Flow

```
┌─────────────────────────────────────────────────────────────────────────┐
│                        RAG CHATBOT FLOW                                  │
└─────────────────────────────────────────────────────────────────────────┘

 1. USER QUESTION                2. QUERY EMBEDDING           3. VECTOR SEARCH
┌─────────────────┐             ┌─────────────────┐         ┌──────────────────┐
│ "What's optimal │             │ AWS Bedrock     │         │ OpenSearch/FAISS │
│ training volume │  ───────►   │ Titan Embeddings│ ─────►  │ Similarity Search│
│ for hypertrophy?"│             │                 │         │ (Top 5 chunks)   │
└─────────────────┘             │ Returns: [1536] │         └──────────────────┘
                                └─────────────────┘                  │
                                                                     │
                                                                     ▼
 6. DISPLAY RESPONSE            5. SAVE TO MEMORY           4. LLM GENERATION
┌─────────────────┐             ┌─────────────────┐         ┌──────────────────┐
│ Frontend UI     │             │ S3 or Local     │         │ AWS Bedrock Nova │
│ • Message       │  ◄────────  │ session.json    │  ◄────  │ • Context +      │
│ • Timestamp     │             │                 │         │   Prompt         │
│ • Session ID    │             └─────────────────┘         │ • temp=0.3       │
└─────────────────┘                                         └──────────────────┘
```

### Document Ingestion Pipeline

```
┌─────────────────────────────────────────────────────────────────────────┐
│                    DOCUMENT INGESTION PIPELINE                           │
│                        (One-time Setup)                                  │
└─────────────────────────────────────────────────────────────────────────┘

    FITNESS PDFs                  TEXT EXTRACTION              CHUNKING
┌─────────────────┐             ┌─────────────────┐         ┌──────────────────┐
│ documents/      │             │ PyPDF           │         │ DocumentProcessor│
│ • Training.pdf  │  ───────►   │ • Page-by-page  │ ─────►  │ • 1000 chars     │
│ • Nutrition.pdf │             │ • Text extract  │         │ • 200 overlap    │
│ • Sleep.pdf     │             │                 │         │ • Metadata       │
└─────────────────┘             └─────────────────┘         └──────────────────┘
                                                                     │
                                                                     ▼
    VECTOR STORAGE                   EMBEDDINGS
┌─────────────────┐             ┌─────────────────────────────────────────┐
│ Vector Database │             │ AWS Bedrock Titan Embeddings            │
│ • FAISS (local) │  ◄────────  │ • Parallel processing (10 workers)      │
│ • OpenSearch    │             │ • 1536 dimensions per chunk             │
│   (production)  │             │ • Retry logic for failures              │
└─────────────────┘             └─────────────────────────────────────────┘
```

## How it fits in the pipeline

1. document_processor.py extracts text and splits into chunks.
2. embeddings.py generates vector representations (embeddings).
3. vector_store.py stores those vectors

   - In FAISS (for local development) — stored as .faiss index files.

   - Or in OpenSearch (for production), which can handle vector search at scale and integrate with other AWS services.


### 🧩 Why We Split Text into Chunks and Create Vector Embeddings

| Step                     | Purpose                                        | Why it’s Needed                              |
| ------------------------ | ---------------------------------------------- | -------------------------------------------- |
| **Chunking**             | Split large text into manageable sections      | LLM context limits & better search precision |
| **Embedding**            | Represent text meaning as vectors              | Enables semantic (meaning-based) search      |
| **Vector Store (FAISS)** | Efficiently store and retrieve similar vectors | Makes retrieval fast and scalable            |


### 🧩 Difference between FAISS and Opensearch Example analogy

Think of FAISS as:
- A super-fast, lightweight search engine on your laptop.

And OpenSearch as:
- A distributed search engine cluster running in the cloud, handling many users and huge datasets — still using FAISS-like math internally.


### Energy Calculator Flow

```
┌─────────────────────────────────────────────────────────────────────────┐
│                    ENERGY CALCULATOR FLOW                                │
└─────────────────────────────────────────────────────────────────────────┘

 USER INPUT                     BACKEND API                  CALCULATIONS
┌─────────────────┐             ┌─────────────────┐         ┌──────────────────┐
│ • Bodyweight    │             │ POST /calculate-│         │ EnergyCalculator │
│ • Body fat %    │  ───────►   │ energy          │ ─────►  │                  │
│ • Training days │             │                 │         │ 1. FFM = BW×(1-BF%)
│ • PAF, TEF      │             │ FastAPI endpoint│         │ 2. BMR = 370+21.6×FFM
│ • Balance goal  │             │                 │         │ 3. Training EE   │
└─────────────────┘             └─────────────────┘         │ 4. Rest day EE   │
                                                            │ 5. Training day EE
                                                            │ 6. Maintenance   │
 DISPLAY + SAVE                     RETURN JSON             │ 7. Target intake │
┌─────────────────┐             ┌─────────────────┐         └──────────────────┘
│ Results UI      │             │ {                │                  │
│ • BMR: 2000kcal │  ◄────────  │   "cunningham_  │  ◄───────────────┘
│ • Target: 2400  │             │    bmr": 2000,  │
│ localStorage    │             │   "target": 2400│
└─────────────────┘             │ }               │
                                └─────────────────┘
```

---

## 🔧 Component Details

### Backend Components

#### 1. **server.py** - Main FastAPI Application
```python
# Key Endpoints:
GET  /                      # API info + stats
GET  /health               # Health check
POST /chat                 # Chatbot (RAG-powered)
POST /calculate-energy     # Energy calculator
GET  /stats                # Vector DB statistics
GET  /conversation/{id}    # Conversation history
```

**Key Features:**
- CORS middleware for cross-origin requests
- Session-based conversation memory
- S3 or local file storage for chat history
- Bedrock client initialization
- Error handling and validation

#### 2. **retrieval.py** - RAG System
```python
class HealthRAG:
    def retrieve_context(query: str, top_k: int = 5):
        # 1. Embed query using Bedrock Titan
        # 2. Search vector store for similar chunks
        # 3. Format context with source citations
        # 4. Extract URLs from retrieved text
        # 5. Return context + sources
```

**Process:**
- Query embedding → Vector search → Context formatting
- Extracts source metadata (document, page)
- Identifies research URLs in text

#### 3. **vector_store.py** - Unified Vector Database
```python
class VectorStore:
    # Development: FAISS (local files)
    # Production: OpenSearch Serverless

    def add_documents()    # Batch insert vectors
    def search()           # K-nearest neighbor search
    def get_stats()        # Database statistics
    def clear()            # Delete all vectors
```

**Storage Modes:**
- **FAISS**: `faiss_index.pkl` + `faiss_metadata.json`
- **OpenSearch**: KNN index with HNSW algorithm

#### 4. **embeddings.py** - Bedrock Titan Embeddings
```python
class BedrockEmbeddings:
    # Parallel processing with ThreadPoolExecutor
    # 10 concurrent workers
    # Retry logic for API failures
    # 1536-dimensional vectors
```

**Features:**
- Parallel API calls for batch processing
- Automatic retry with exponential backoff
- Text truncation (max 25k chars)
- Error handling and logging

#### 5. **energy_calculator.py** - Evidence-Based Formulas
```python
# Cunningham BMR Formula (1991)
BMR = 370 + (21.6 × FFM)

# Training Energy Expenditure
Training_EE = 0.1 × Bodyweight × Duration

# Maintenance Energy Intake
Maintenance = (Training_days × Training_EE + Rest_days × Rest_EE) / 7
```

#### 6. **lambda_handler.py** - AWS Lambda Entry Point
```python
from mangum import Mangum
from server import app

handler = Mangum(app)  # ASGI adapter for Lambda
```

### Frontend Components

#### 1. **health-chat.tsx** - Chatbot Interface
- Real-time chat UI with message history
- Session ID management
- Auto-scroll to latest message
- Loading states and error handling
- Keyboard shortcuts (Enter to send)

#### 2. **energy-calculator.tsx** - Calculator Interface
- Form inputs with validation
- localStorage persistence
- Real-time calculation
- Results visualization with color-coded metrics

#### 3. **navigation.tsx** - Page Navigation
- Switch between chatbot and calculator
- Clean URL routing

#### 4. **page.tsx** - Main Layout
- Responsive container
- Gradient background
- Footer with disclaimers

---

## 🔄 Data Flow

### Chatbot Request Flow

```
1. User types message in frontend
   ↓
2. POST /chat with { message, session_id }
   ↓
3. Lambda receives request via API Gateway
   ↓
4. Load conversation history from S3/local
   ↓
5. RAG System:
   a. Embed query (Bedrock Titan)
   b. Search vectors (OpenSearch/FAISS)
   c. Retrieve top 5 chunks with metadata
   ↓
6. Build system prompt with context
   ↓
7. Call Bedrock Nova LLM
   a. Model: amazon.nova-lite-v1:0
   b. Temperature: 0.3 (factual)
   c. Max tokens: 2000
   ↓
8. Extract response text
   ↓
9. Save conversation to memory (S3/local)
   ↓
10. Return { response, session_id }
    ↓
11. Frontend displays message
```

### 🌐 What is HTTP?

HTTP (HyperText Transfer Protocol) is the “language” that web browsers and servers use to talk to each other.

Every time you open a webpage, click a button, or send a form, your browser makes an HTTP request — asking the server to do something and return a response.

### 🔍 Quick comparison

| Feature               | **GET**                      | **POST**                                          |
| --------------------- | ---------------------------- | ------------------------------------------------- |
| Purpose               | Retrieve data                | Send data                                         |
| Has request body?     | ❌ No                         | ✅ Yes                                             |
| Shown in browser URL? | ✅ Yes (`?query=params`)      | ❌ No                                              |
| Changes server data?  | ❌ Usually not                | ✅ Often yes                                       |
| Used for              | Fetching data, reading pages | Submitting forms, creating chat messages, uploads |

### 🧭 Example in your chatbot flow

When you load your chat page:
```
GET /health-chat
```

→ Browser asks the server for the page itself.

When you send a message:
```
POST /chat
```

→ Browser sends your message to the backend so the model can respond.

### ☁️ What is API Gateway?

API Gateway is a service (for example, AWS API Gateway) that acts as a bridge between your frontend and backend — especially when your backend runs as a serverless function (like AWS Lambda).

### Why use API Gateway?
| Benefit                  | Explanation                                                                |
| ------------------------ | -------------------------------------------------------------------------- |
| **Security**             | You don’t expose your Lambda or backend directly to the internet           |
| **Scalability**          | Handles many concurrent requests automatically                             |
| **Routing**              | Can map multiple endpoints (`/chat`, `/ingest`, etc.) to different Lambdas |
| **Integration**          | Works natively with AWS Lambda, Cognito, Bedrock, etc.                     |
| **Logging & Monitoring** | Built-in CloudWatch integration for debugging                              |


### 🔗 How Lambda(server.py) and HealthRAG(retrieval.py) realte
| File           | Role                                      | Think of it as    |
| -------------- | ----------------------------------------- | ----------------- |
| `server.py`    | Entry point, manages API and conversation | The **conductor** |
| `retrieval.py` | Fetches relevant document context         | The **librarian** |

### 🧠 Analogy

Imagine you’re running a library chatbot:

#### server.py: 
The receptionist — greets users, records the conversation, asks what they need, and gives them an answer.

#### retrieval.py: 
The researcher — searches the bookshelves for the most relevant paragraphs.


### Calculator Request Flow

```
1. User fills form and submits
   ↓
2. POST /calculate-energy with parameters
   ↓
3. Lambda validates input (Pydantic models)
   ↓
4. Calculate all metrics:
   • Fat-free mass
   • Cunningham BMR
   • Training energy expenditure
   • Rest/training day expenditure
   • Maintenance intake
   • Target intake
   ↓
5. Return JSON with results
   ↓
6. Frontend displays + saves to localStorage
```

---

## ☁️ AWS Infrastructure

### Terraform Resources

#### Core Infrastructure
```hcl
# S3 Buckets
- fitness-dev-frontend-{account-id}    # Static website
- fitness-dev-documents-{account-id}   # PDFs + Lambda zip
- fitness-dev-memory-{account-id}      # Conversations

# Lambda Function
- Name: fitness-dev-api
- Runtime: python3.12
- Handler: lambda_handler.handler
- Timeout: 300s (configurable)
- Memory: 512MB (configurable)

# API Gateway
- Type: HTTP API
- Routes: /, /health, /chat, /calculate-energy, /stats
- CORS: Enabled
- Throttling: Configurable burst/rate limits

# CloudFront
- Origin: S3 website endpoint
- SSL: AWS managed or custom ACM cert
- Caching: 1 hour default
- Error handling: SPA routing (404→index.html)
```

### 🧠 CloudFront in simple terms

CloudFront is not a URL service, but rather a Content Delivery Network (CDN).
It sits in front of your S3 (or other origins) and distributes content to users from nearby edge locations for faster loading.

Think of it like a global delivery network for your website’s files.


### ⚙️ Relationship between CloudFront and S3
| Aspect           | CloudFront                                                   | S3                                        |
| ---------------- | ------------------------------------------------------------ | ----------------------------------------- |
| **Role**         | CDN / Global cache                                           | Storage (origin)                          |
| **Stores data?** | Temporarily (cached)                                         | Permanently                               |
| **Purpose**      | Deliver content fast and securely                            | Host and store static website files       |
| **User access**  | Users access CloudFront URL (e.g., `d123abc.cloudfront.net`) | CloudFront fetches from S3                |
| **Connection**   | CloudFront “origin” is S3 bucket                             | S3 serves files to CloudFront when needed |

### 🔁 Example Flow

1. User visits your site → https://www.myapp.com
2. DNS routes them to CloudFront.
3. CloudFront checks if it already has the requested file cached.
- ✅ If yes → serves it immediately (fast).
- ❌ If no → fetches it from your S3 bucket, caches it, then serves it.
4. Next user nearby gets it instantly from the cache.

### 🧩 Why this setup?

- Speed: Faster global delivery (users in Japan get files from Tokyo edge server).
- Cost: Reduces direct S3 access requests → saves bandwidth cost.
- Security: You can block direct public access to S3; only CloudFront can fetch files.

#### Vector Database (OpenSearch Serverless)
```hcl
# Collection
- Name: fitness-dev-health-docs
- Type: VECTORSEARCH
- Index: health-docs

# KNN Configuration
- Algorithm: HNSW (Hierarchical NSW)
- Engine: FAISS
- Dimension: 1536
- ef_construction: 512
- m: 16

# Security Policies
- Encryption: AWS owned key
- Network: Public access (restricted by data policy)
- Data Access: Lambda role + IAM user
```

#### IAM Permissions
```hcl
# Lambda Execution Role
- AWSLambdaBasicExecutionRole    # CloudWatch Logs
- AmazonBedrockFullAccess        # Nova + Titan
- AmazonS3FullAccess             # Storage
- Custom OpenSearch policy       # Vector DB access
```

#### Optional Custom Domain
```hcl
# Route53 + ACM
- Certificate: ACM (us-east-1 for CloudFront)
- Validation: DNS
- Records: A, AAAA for root + www
- Aliases point to CloudFront
```

### Environment Variables

**Local Development (.env)**
```bash
DEFAULT_AWS_REGION=us-east-1
USE_OPENSEARCH=false
USE_S3=false
BEDROCK_MODEL_ID=amazon.nova-lite-v1:0
CORS_ORIGINS=http://localhost:3000
```

**Production (Lambda)**
```bash
CORS_ORIGINS=https://yourdomain.com
S3_BUCKET=fitness-prod-memory-{account}
USE_S3=true
BEDROCK_MODEL_ID=amazon.nova-lite-v1:0
USE_OPENSEARCH=true
OPENSEARCH_ENDPOINT=https://{collection}.aoss.amazonaws.com
DEFAULT_AWS_REGION=us-east-1
```

---

## 🔐 Security

### Authentication & Authorization

**AWS IAM:**
- Lambda uses execution role
- OpenSearch data access policy
- S3 bucket policies (private by default)
- API Gateway has no authentication (add API key/Cognito for production)

**CORS Configuration:**
```python
# Development
allow_origins = ["http://localhost:3000"]

# Production
allow_origins = ["https://yourdomain.com", "https://www.yourdomain.com"]
```

  📊 Comparison Table

  | Aspect    | NEXT_PUBLIC_API_URL       | CORS_ORIGINS             |
  |-----------|---------------------------|--------------------------|
  | Location  | Frontend .env.local       | Backend .env             |
  | Direction | Frontend → Backend        | Backend checks Frontend  |
  | Purpose   | "Where to send requests?" | "Who can send requests?" |
  | Example   | http://localhost:8000     | http://localhost:3000    |
  | Type      | Destination address       | Security whitelist       |

  ---
  🔄 How They Work Together

  Frontend (localhost:3000)
  
  ↓
  
  Uses NEXT_PUBLIC_API_URL to know where to send request:
     fetch("http://localhost:8000/chat")
     
   ↓
  
  Backend (localhost:8000) receives request
  
   ↓
  
  Checks CORS_ORIGINS: "Is localhost:3000 allowed?"
  
   ↓
  
  ✅ Yes, it's in the whitelist → Process request
  
   ↓
   
   Return response to frontend

  ---
  🌐 Real-World Example

  Local Development:

  Frontend .env.local:
  NEXT_PUBLIC_API_URL=http://localhost:8000
  👉 Frontend knows to send requests to local backend

  Backend .env:
  CORS_ORIGINS=http://localhost:3000,http://localhost:3002
  👉 Backend accepts requests from local frontend (port 3000 or 3002)

  ---
  Production:

  Frontend .env.production:
  NEXT_PUBLIC_API_URL=https://abc123.execute-api.us-east-1.amazonaws.com
  👉 Frontend sends requests to AWS API Gateway

  Backend (Lambda environment):
  CORS_ORIGINS=https://yourdomain.com,https://www.yourdomain.com
  👉 Backend only accepts requests from your production domain

  ---
  🛡️ Why CORS Exists (Security)

  Without CORS protection, any website could call your API:

  ❌ Bad scenario without CORS:
  - EvilWebsite.com loads in browser
  - Their JavaScript calls YOUR backend API
  - Steals data or makes unauthorized requests

  With CORS:
  ✅ Good scenario with CORS:
  - EvilWebsite.com tries to call your API
  - Backend checks CORS_ORIGINS
  - "EvilWebsite.com is NOT in whitelist"
  - Request BLOCKED! 🛑

  ---
  🎯 Summary

  | Variable            | Who Uses It        | What It Does                            |
  |---------------------|--------------------|-----------------------------------------|
  | NEXT_PUBLIC_API_URL | Frontend (browser) | Points to backend URL                   |
  | CORS_ORIGINS        | Backend (server)   | Security whitelist of allowed frontends |

  They're complementary:
  - Frontend uses API_URL to find the backend
  - Backend uses CORS_ORIGINS to protect itself from unauthorized frontends

  Think of it like:
  - API_URL = "The address I need to visit"
  - CORS_ORIGINS = "The guest list at the door"


### Data Security

**Encryption:**
- S3: Server-side encryption (SSE-S3)
- OpenSearch: AWS owned key
- CloudFront: HTTPS enforced
- API Gateway: TLS 1.2+

**Privacy:**
- No PII/PHI stored
- Conversations in isolated S3 objects
- Session IDs are UUIDs
- No user authentication (stateless)

**Best Practices:**
1. Never commit `.env` files
2. Use IAM roles (no hardcoded keys)
3. Restrict CORS in production
4. Enable CloudWatch logging
5. Set API Gateway throttling limits
6. Regular dependency updates

---

## 🚀 Deployment

### Local Development

**Quick Start (Everything Already Set Up):**
```bash
# 1. Start backend server
cd backend
uv run uvicorn server:app --reload
# → http://localhost:8000
# uv run python -m uvicorn server:app --reload (when the above command doesn't work)

# 2. Start frontend (in new terminal)
cd frontend
npm run dev
# → http://localhost:3000
```

**Note:**
- Environment variables are pre-configured in `backend/.env` and `frontend/.env.local`
- Python environment, dependencies, and document ingestion are already complete
- Simply start both servers and you're ready to go!

---

**First-Time Setup (Only if starting fresh):**
```bash
# Backend Setup
cd backend
uv init --bare              # Initialize uv project
uv python pin 3.12          # Pin Python version to 3.12
uv add -r requirements.txt  # Install dependencies
uv run python ingest_documents.py  # Ingest PDFs into vector store

# Frontend Setup
cd ../frontend
npm install                 # Install Node dependencies
```

**When to Re-run Ingestion:**
- Only run `uv run python ingest_documents.py` when you add new PDFs to `backend/documents/`

### AWS Deployment

**Prerequisites:**
```bash
- AWS CLI configured
- Terraform installed
- Docker running (for Lambda packaging)
```

**⚠️ CRITICAL: Frontend Build Issue**

Next.js prioritizes `.env.local` over `.env.production` during build. If `.env.local` exists when running `npm run build`, it will embed localhost URLs into the production build, causing "Sorry, I encountered an error" in production.

**Two solutions:**

**Option A: Manual Rename (Current)**
```bash
cd frontend
mv .env.local .env.local.backup  # Before deployment
npm run build
mv .env.local.backup .env.local  # After deployment
```

**Option B: Delete .env.local (Recommended)**
- Delete `frontend/.env.local` entirely
- Use only `.env.development` (for `npm run dev`) and `.env.production` (for `npm run build`)
- No secrets needed (API URLs are public)

---

**First-Time Deployment:**
```bash
# 1. Deploy infrastructure and application
./scripts/deploy.sh dev    # Development
./scripts/deploy.sh prod   # Production

# 2. Configure OpenSearch endpoint (after Terraform completes)
cd terraform
terraform output -raw opensearch_endpoint
# Copy the output endpoint URL

cd ../backend
# Add to backend/.env:
# OPENSEARCH_ENDPOINT=<paste-endpoint-url-here>

# 3. Ingest documents to OpenSearch
uv run python upload_to_opensearch.py
```

**What deploy.sh does:**
1. Package Lambda dependencies (runs `backend/deploy.py`)
2. Initialize and apply Terraform (creates OpenSearch, Lambda, S3, API Gateway, CloudFront)
3. Build Next.js static export with production API URL
4. Upload frontend build to S3
5. Output CloudFront and API Gateway URLs

**What upload_to_opensearch.py does:**
- Reads local FAISS index files (faiss_index.pkl, faiss_metadata.json)
- Creates OpenSearch index with KNN vector search configuration
- Uploads all document vectors to OpenSearch in batches of 100
- Verifies upload completion

**Subsequent Deployments (Code Updates):**
```bash
./scripts/deploy.sh dev    # Only need to redeploy, data persists in OpenSearch
```

**When to Re-ingest Documents:**
- First deployment (OpenSearch is empty)
- Added new PDFs to `backend/documents/`
- OpenSearch index was deleted/recreated
- Note: Re-ingestion replaces all existing data

**After Infrastructure Rebuild:**
If you run `./scripts/destroy.sh` and then `./scripts/deploy.sh`, OpenSearch gets a new random endpoint URL. You must update `backend/.env`:
```bash
cd terraform
terraform output -raw opensearch_endpoint
# Copy the new endpoint

cd ../backend
# Update OPENSEARCH_ENDPOINT in .env with the new value
```

**Destroy Infrastructure:**
```bash
./scripts/destroy.sh dev
```

### Deployment Checklist

**Pre-deployment:**
- [ ] PDFs in `backend/documents/`
- [ ] AWS credentials configured
- [ ] Terraform variables set (`terraform.tfvars`)
- [ ] Frontend env vars set (`.env.production`)

**Post-deployment:**
- [ ] Test API Gateway endpoints
- [ ] Verify CloudFront distribution
- [ ] Check OpenSearch index populated
- [ ] Test chatbot with sample queries
- [ ] Validate calculator calculations
- [ ] Monitor CloudWatch logs

---

## 📊 Monitoring & Observability

### CloudWatch

**Lambda Metrics:**
- Invocations
- Duration
- Error rate
- Throttles
- Concurrent executions

**Log Groups:**
- `/aws/lambda/fitness-{env}-api`
- API request/response logs
- Error stack traces

**Bedrock Metrics:**
- Token usage (input/output)
- Model latency
- Throttling events
- Cost tracking

### Application Metrics

**Vector Store Stats:**
```bash
curl https://api.yourdomain.com/stats

{
  "type": "opensearch",
  "total_docs": 2847
}
```

**Health Check:**
```bash
curl https://api.yourdomain.com/health

{
  "status": "healthy",
  "bedrock_model": "amazon.nova-lite-v1:0",
  "vector_store": { "total_docs": 2847 }
}
```

---

## 🎯 Performance Optimization

### Backend
- **Parallel embeddings**: 10 concurrent workers
- **Chunking strategy**: 1000 chars, 200 overlap
- **Caching**: FAISS loaded once (Lambda warm start)
- **Timeout**: 300s for large document processing

### Frontend
- **Static generation**: Next.js SSG
- **CDN caching**: CloudFront with 1h TTL
- **Code splitting**: Automatic with Next.js
- **localStorage**: Persist calculator inputs

### Cost Optimization
- **Local FAISS**: Free development
- **Lambda**: Pay per request
- **S3**: Minimal storage costs
- **Bedrock**: Pay per token
- **OpenSearch Serverless**: OCU-based pricing

---

## 🔄 Scaling Considerations

### Current Limits
- Lambda: 1000 concurrent executions (default)
- API Gateway: 10,000 RPS (default)
- OpenSearch: Auto-scales with data
- S3: Unlimited

### Future Enhancements
- [ ] Add caching layer (ElastiCache/CloudFront)
- [ ] Implement rate limiting (API Gateway)
- [ ] Add user authentication (Cognito)
- [ ] Conversation analytics (Athena)
- [ ] Multi-region deployment
- [ ] WebSocket support (real-time streaming)

---

## 📚 References

### Documentation
- [AWS Bedrock](https://docs.aws.amazon.com/bedrock/)
- [OpenSearch Serverless](https://docs.aws.amazon.com/opensearch-service/latest/developerguide/serverless.html)
- [FastAPI](https://fastapi.tiangolo.com/)
- [Next.js](https://nextjs.org/docs)
- [Terraform AWS Provider](https://registry.terraform.io/providers/hashicorp/aws/latest/docs)

### Research Papers
- Cunningham et al. (1991) - BMR Formula
- HNSW Algorithm (2016) - Efficient vector search

---

**Last Updated:** 2025-10-12
**Version:** 1.0
**Maintained By:** AI Engineer Team
