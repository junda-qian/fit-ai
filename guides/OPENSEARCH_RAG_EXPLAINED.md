# OpenSearch & RAG Explained - For Beginners

## What is RAG?

Imagine you're taking an open-book exam. Instead of memorizing everything, you can:
1. **Understand the question**
2. **Search your textbook** for relevant information
3. **Use that information** to write a better answer

**RAG (Retrieval-Augmented Generation)** makes AI chatbots work the same way!

### Without RAG (Regular ChatGPT):
```
User: "What's the best diet for muscle gain?"
    ↓
AI (from memory only): "Based on my training data from 2021..."
    ↓
❌ May be outdated or generic
```

### With RAG (FitTracker AI):
```
User: "What's the best diet for muscle gain?"
    ↓
1. Search knowledge base (4,484 fitness research papers)
2. Find 5 most relevant sections
3. AI reads those sections
4. AI answers with specific evidence
    ↓
✅ Current, evidence-based, with source citations
```

**RAG = Retrieval (search documents) + Augmented (add to AI context) + Generation (AI writes answer)**

---

## Real-World Analogy

### Without RAG: The Know-It-All Student
- Studied for the exam weeks ago
- Answers from memory
- Can't look up specifics
- **Problem:** Memory fades, details get fuzzy

### With RAG: The Smart Student with Textbook
- Brings textbook to open-book exam
- Looks up relevant chapters
- Cites specific pages
- **Benefit:** Accurate, detailed, verifiable answers

**FitTracker AI is like a personal fitness coach who keeps 4,484 research papers on hand and can instantly find the exact study that answers your question!**

---

## What is OpenSearch?

**OpenSearch** is a powerful search engine designed for:
- Finding similar content (semantic search)
- Storing billions of documents
- Lightning-fast searches (milliseconds)
- Vector similarity search (AI embeddings)

### The Simple Definition:
OpenSearch = Google Search + AI-Powered Similarity Matching + Cloud Database

**Think of it as:**
A massive library with a super-intelligent librarian who can find books similar to your question—even if the exact words don't match.

### Traditional Search vs Vector Search

**Traditional Search (Google):**
```
Query: "exercises for back pain"
Matches: Documents containing words "exercises", "back", "pain"
Problem: Misses "stretches for lumbar discomfort" (different words, same meaning)
```

**Vector Search (OpenSearch):**
```
Query: "exercises for back pain"
    ↓
Convert to numbers (embedding): [0.23, -0.15, 0.87, ..., 0.42] (1536 numbers)
    ↓
Find documents with SIMILAR number patterns
    ↓
Matches: "exercises for back pain", "stretches for lumbar discomfort",
         "movements to relieve spine tension"
✅ Understands meaning, not just keywords!
```

---

## How FitTracker AI Uses RAG

The fitness app has **two RAG implementations**:

### 1. Local Development (FAISS)
**FAISS** = Facebook AI Similarity Search (free, runs on your computer)

**What it is:**
- Open-source vector database
- Stores vectors in local files
- Fast similarity search
- No cost, no internet needed

**Files:**
```
backend/
├── faiss_index.bin        ← Vector database (the numbers)
└── faiss_metadata.json    ← Text chunks + metadata (the actual content)
```

**When to use:**
- Local development and testing
- Building features offline
- No AWS costs
- Instant setup

### 2. Production (OpenSearch Serverless)
**OpenSearch** = AWS's managed search service (cloud, scalable)

**What it is:**
- Hosted vector database on AWS
- Automatically scales to billions of vectors
- Built for production use
- Global availability

**Infrastructure:**
```
AWS OpenSearch Serverless Collection
├── Index: "health-docs"
├── 4,484 vectors (1536 dimensions each)
├── HNSW algorithm for fast search
└── FAISS engine under the hood
```

**When to use:**
- Production deployments
- Team collaboration (shared database)
- Large-scale applications
- Need reliability and backups

**Cost:** ~$700/month (even when idle)

**Why expensive?**
OpenSearch Serverless reserves compute capacity 24/7, even when you're not using it. That's why FitTracker uses FAISS locally to save money during development.

---

## The Complete RAG Pipeline

### Step 1: Document Ingestion (One-Time Setup)

**What happens:** Convert PDF research papers into searchable chunks.

```
┌─────────────────────────────────────────────────────────────┐
│ 1. LOAD PDFs                                                │
│    backend/documents/*.pdf (9 fitness research PDFs)        │
│    Total size: ~25 MB                                       │
└─────────────────────────────────────────────────────────────┘
                           ↓
┌─────────────────────────────────────────────────────────────┐
│ 2. SPLIT INTO CHUNKS (DocumentProcessor)                    │
│    • Read each page of PDF                                  │
│    • Split into 1000-character chunks                       │
│    • 200-character overlap between chunks                   │
│    • Break at sentence boundaries (smart splitting)         │
│                                                              │
│    Example chunk:                                           │
│    "Protein intake of 1.6g/kg bodyweight is sufficient      │
│     for muscle growth. Higher intakes (2.2g/kg) show no     │
│     additional benefit in trained individuals..."           │
│                                                              │
│    Metadata: {source: "Protein-PDC-2024.pdf", page: 12}    │
└─────────────────────────────────────────────────────────────┘
                           ↓
┌─────────────────────────────────────────────────────────────┐
│ 3. GENERATE EMBEDDINGS (BedrockEmbeddings)                  │
│    • Send each chunk to AWS Bedrock Titan V1                │
│    • AI converts text → 1536 numbers (embedding vector)     │
│    • Parallel processing: 10 chunks at once                 │
│                                                              │
│    Example:                                                 │
│    Text: "Protein intake of 1.6g/kg..."                    │
│      ↓                                                       │
│    Vector: [0.023, -0.145, 0.876, ..., 0.421]              │
│             (1536 numbers representing meaning)             │
│                                                              │
│    Total chunks: 4,484                                      │
│    Time: ~15 minutes (with parallel processing)            │
└─────────────────────────────────────────────────────────────┘
                           ↓
┌─────────────────────────────────────────────────────────────┐
│ 4. STORE IN VECTOR DATABASE                                 │
│                                                              │
│    FAISS (Local):                                           │
│    • Save to faiss_index.bin (60 MB file)                   │
│    • Save metadata to faiss_metadata.json (8 MB file)       │
│    • Ready for local queries ✅                             │
│                                                              │
│    OpenSearch (Cloud):                                      │
│    • Upload to AWS OpenSearch Serverless                    │
│    • Create index with kNN (k-Nearest Neighbors) search     │
│    • Ready for production queries ✅                        │
└─────────────────────────────────────────────────────────────┘
```

**Scripts:**
```bash
# Local (FAISS)
python backend/ingest_documents.py

# Upload to OpenSearch
python backend/upload_to_opensearch.py
```

---

### Step 2: Query Time (Every Chatbot Question)

**What happens:** When a user asks a question, find relevant chunks and let AI answer.

```
┌─────────────────────────────────────────────────────────────┐
│ USER ASKS QUESTION                                          │
│ "What's the optimal protein intake for muscle growth?"     │
└─────────────────────────────────────────────────────────────┘
                           ↓
┌─────────────────────────────────────────────────────────────┐
│ 1. EMBED THE QUESTION (BedrockEmbeddings)                   │
│    • Convert question to 1536-dimension vector              │
│    • Same AI model as document embedding (Titan V1)         │
│                                                              │
│    Question: "What's the optimal protein intake..."        │
│      ↓                                                       │
│    Vector: [0.031, -0.122, 0.903, ..., 0.387]              │
└─────────────────────────────────────────────────────────────┘
                           ↓
┌─────────────────────────────────────────────────────────────┐
│ 2. SEARCH VECTOR DATABASE (VectorStore)                     │
│    • Calculate distance between question vector and all     │
│      document vectors (4,484 comparisons)                   │
│    • Find 5 closest matches (top_k=5)                       │
│                                                              │
│    FAISS (Local):                                           │
│    • Uses L2 distance (Euclidean distance)                  │
│    • Search time: ~10 milliseconds                          │
│                                                              │
│    OpenSearch (Cloud):                                      │
│    • Uses HNSW algorithm (Hierarchical Navigable Small      │
│      World graphs)                                          │
│    • Search time: ~50 milliseconds                          │
│                                                              │
│    Results (top 5 chunks):                                  │
│    1. "Protein intake of 1.6g/kg bodyweight..." (score: 0.12)│
│    2. "Muscle protein synthesis peaks at..." (score: 0.15)  │
│    3. "Research shows 2.2g/kg provides no..." (score: 0.18) │
│    4. "Protein timing is less important..." (score: 0.21)   │
│    5. "Quality matters: complete proteins..." (score: 0.24) │
└─────────────────────────────────────────────────────────────┘
                           ↓
┌─────────────────────────────────────────────────────────────┐
│ 3. FORMAT CONTEXT (HealthRAG)                               │
│    • Combine top 5 chunks into one context string           │
│    • Include source citations (PDF name, page number)       │
│                                                              │
│    Formatted context:                                       │
│    [Source 1: Protein-PDC-2024.pdf, Page 12]               │
│    Protein intake of 1.6g/kg bodyweight is sufficient...   │
│                                                              │
│    [Source 2: Muscle-Growth-PDC-2024.pdf, Page 8]          │
│    Muscle protein synthesis peaks at...                    │
│                                                              │
│    [Source 3: Protein-PDC-2024.pdf, Page 15]               │
│    Research shows 2.2g/kg provides no...                   │
└─────────────────────────────────────────────────────────────┘
                           ↓
┌─────────────────────────────────────────────────────────────┐
│ 4. SEND TO AI (OpenAI GPT-4)                                │
│    • User question                                          │
│    • Retrieved context (5 relevant chunks)                  │
│    • System prompt: "Use only the provided evidence..."     │
│                                                              │
│    Prompt to GPT-4:                                         │
│    """                                                      │
│    Context from research papers:                           │
│    [Source 1: Protein-PDC-2024.pdf, Page 12]               │
│    Protein intake of 1.6g/kg bodyweight is sufficient...   │
│    ...                                                      │
│                                                              │
│    User question:                                           │
│    What's the optimal protein intake for muscle growth?    │
│                                                              │
│    Instructions:                                            │
│    Answer using ONLY the provided context. Cite sources.   │
│    """                                                      │
└─────────────────────────────────────────────────────────────┘
                           ↓
┌─────────────────────────────────────────────────────────────┐
│ 5. AI GENERATES ANSWER                                      │
│    Based on the research, optimal protein intake for       │
│    muscle growth is 1.6g per kg of bodyweight. Studies     │
│    show that higher intakes (2.2g/kg) provide no           │
│    additional benefit in trained individuals.               │
│                                                              │
│    Sources:                                                 │
│    • Protein-PDC-2024.pdf, Page 12                         │
│    • Muscle-Growth-PDC-2024.pdf, Page 8                    │
│                                                              │
│    ✅ Evidence-based answer with citations                  │
└─────────────────────────────────────────────────────────────┘
```

**Performance:**
- Embedding question: ~500ms
- Vector search: ~10-50ms
- GPT-4 generation: ~2-5 seconds
- **Total response time:** ~3-6 seconds

---

## FAISS vs OpenSearch Comparison

| Feature | FAISS (Local) | OpenSearch (Cloud) |
|---------|---------------|-------------------|
| **Type** | Open-source library | Managed AWS service |
| **Cost** | Free | ~$700/month |
| **Setup** | pip install faiss-cpu | Terraform + AWS config |
| **Storage** | Local files (60 MB) | AWS cloud (serverless) |
| **Speed** | ~10ms search | ~50ms search |
| **Scalability** | Single machine (millions) | Billions of vectors |
| **Sharing** | Can't share (local files) | Team access (cloud) |
| **Backup** | Manual (copy files) | Automatic (AWS managed) |
| **Best for** | Local dev, testing | Production, teams |
| **Algorithm** | IndexFlatL2 (exact search) | HNSW (approximate search) |

### When to use each:

**Use FAISS when:**
- Developing locally
- Testing RAG system
- Budget-constrained
- Small to medium dataset
- Single developer

**Use OpenSearch when:**
- Production deployment
- Team collaboration needed
- Large-scale data (billions)
- Need reliability + backups
- Budget available

**FitTracker's strategy:**
- Development: FAISS (free, fast iteration)
- Production: Can use either (toggle with `USE_OPENSEARCH` env var)
- Cost savings: Disable OpenSearch when not actively demoing

---

## Document Processing Details

### PDF to Chunks Pipeline

**Example: "Protein-PDC-2024.pdf" (25 pages)**

```
Original PDF:
┌──────────────────────────────────────┐
│ Page 1: Introduction to Protein      │
│ Protein is essential for muscle...   │
│ (500 words)                           │
├──────────────────────────────────────┤
│ Page 2: Protein Requirements          │
│ Research shows that 1.6g/kg...        │
│ (650 words)                           │
├──────────────────────────────────────┤
│ ...                                   │
└──────────────────────────────────────┘
```

**After chunking (1000 chars, 200 overlap):**
```
Chunk 1 (Page 1):
"Protein is essential for muscle growth and repair.
Studies indicate that adequate protein intake is
crucial for athletes and individuals engaging in..."
Metadata: {source: "Protein-PDC-2024.pdf", page: 1, chunk_id: 0}

Chunk 2 (Page 1, overlaps with Chunk 1):
"...crucial for athletes and individuals engaging in
resistance training. The recommended dietary allowance
(RDA) for protein is 0.8g/kg, but this may not be..."
Metadata: {source: "Protein-PDC-2024.pdf", page: 1, chunk_id: 1}

Chunk 3 (Page 2):
"Research shows that 1.6g/kg bodyweight is sufficient
for maximizing muscle protein synthesis in trained
individuals. Higher intakes provide no additional..."
Metadata: {source: "Protein-PDC-2024.pdf", page: 2, chunk_id: 0}
```

**Why overlap?**
- Ensures context isn't lost at chunk boundaries
- Sentences that span chunks remain coherent
- Better search results

**Why 1000 characters?**
- Small enough for focused search results
- Large enough to preserve context
- Fits well in AI context windows

---

## Embedding Generation

### What is an Embedding?

**An embedding is a list of numbers that represents the meaning of text.**

**Simple example (2D for visualization):**
```
"dog" → [0.8, 0.2]
"cat" → [0.75, 0.25]
"car" → [0.1, 0.9]
```

Notice: "dog" and "cat" are similar (close numbers), but "car" is different!

**Real embeddings (1536D):**
```
"Protein intake of 1.6g/kg..." →
[0.023, -0.145, 0.876, 0.234, -0.567, ..., 0.421]
(1536 numbers)
```

**How similarity works:**

```
Vector A: [0.8, 0.2]  ← "dog"
Vector B: [0.75, 0.25] ← "cat"
Vector C: [0.1, 0.9]   ← "car"

Distance(A, B) = sqrt((0.8-0.75)² + (0.2-0.25)²) = 0.058 (close!)
Distance(A, C) = sqrt((0.8-0.1)² + (0.2-0.9)²) = 1.01 (far!)
```

**Result:** "dog" and "cat" are similar, "dog" and "car" are not.

### AWS Bedrock Titan V1

**What it does:**
Converts text to 1536-dimension vectors using a pre-trained AI model.

**Model:** amazon.titan-embed-text-v1
**Dimension:** 1536 (1536 numbers per text)
**Max input:** ~25,000 characters

**Code:**
```python
from embeddings import BedrockEmbeddings

embeddings = BedrockEmbeddings()

# Embed a single query
query = "What's the best protein intake?"
vector = embeddings.embed_query(query)
# Returns: [0.023, -0.145, ..., 0.421] (1536 numbers)

# Embed multiple documents (parallel)
texts = [
    "Protein is essential for muscle...",
    "Carbohydrates provide energy...",
    "Fats are crucial for hormone..."
]
vectors = embeddings.embed_documents(texts)
# Returns: [[...], [...], [...]] (3 vectors of 1536 numbers each)
```

**Performance tricks:**
- Parallel processing (10 texts at once)
- Retry logic on failures
- Text truncation (max 25k chars)

---

## Vector Search Algorithms

### FAISS: IndexFlatL2

**What it does:** Brute-force exact search using L2 distance (Euclidean distance).

**Algorithm:**
```
For each of 4,484 document vectors:
    Calculate distance to query vector
    Store (distance, document_id)

Sort by distance
Return top 5
```

**Math:**
```
Query: [q1, q2, ..., q1536]
Doc:   [d1, d2, ..., d1536]

L2 Distance = sqrt((q1-d1)² + (q2-d2)² + ... + (q1536-d1536)²)
```

**Pros:**
- Exact results (100% accurate)
- Simple to understand
- Fast for small datasets

**Cons:**
- Slow for billions of vectors
- No approximation

**FitTracker performance:**
- 4,484 vectors
- Search time: ~10 milliseconds
- Perfect for this use case!

---

### OpenSearch: HNSW Algorithm

**HNSW** = Hierarchical Navigable Small World graphs

**What it does:** Approximate search using graph navigation (much faster for large datasets).

**Analogy:**
Instead of checking EVERY house in a city to find your friend:
1. Start at your house
2. Ask neighbor: "Who's closest to [friend's address]?"
3. Jump to that neighbor
4. Repeat until you find your friend

**Structure:**
```
Level 2 (sparse):  A ←→ Z
                    ↓    ↓
Level 1 (medium):  A ←→ M ←→ Z
                    ↓    ↓    ↓
Level 0 (dense):   A B C D ... X Y Z
```

**Search:**
1. Start at top level (sparse graph)
2. Navigate to closest neighbor
3. Drop down a level
4. Repeat until bottom level
5. Return top K neighbors

**Pros:**
- Very fast (even for billions of vectors)
- Scalable
- High accuracy (~99%)

**Cons:**
- Approximate (not 100% exact)
- More complex
- Higher memory usage

**FitTracker configuration:**
```python
{
    "name": "hnsw",
    "engine": "faiss",
    "parameters": {
        "ef_construction": 512,  # Build-time accuracy
        "m": 16                  # Neighbors per node
    }
}
```

**Performance:**
- 4,484 vectors
- Search time: ~50 milliseconds
- Accuracy: ~99%

---

## The Adapter Pattern (FAISS ↔ OpenSearch)

FitTracker uses an **adapter pattern** to support both FAISS and OpenSearch with the same code.

### The Interface

```python
class VectorStore:
    def __init__(self, use_opensearch: bool = False):
        if use_opensearch:
            self._init_opensearch()
        else:
            self._init_faiss()

    def add_documents(texts, embeddings, metadatas):
        # Add to database

    def search(query_embedding, k=5):
        # Search for similar vectors

    def get_stats():
        # Get database stats
```

### Switching Between Databases

**Environment variable:**
```bash
# Use FAISS (local)
export USE_OPENSEARCH=false

# Use OpenSearch (cloud)
export USE_OPENSEARCH=true
```

**Same code works with both:**
```python
from vector_store import VectorStore

# Automatically uses FAISS or OpenSearch based on env var
vector_store = VectorStore(use_opensearch=USE_OPENSEARCH)

# Add documents (works with both)
vector_store.add_documents(texts, embeddings, metadatas)

# Search (works with both)
results = vector_store.search(query_embedding, k=5)
```

**Why this is powerful:**
- Develop locally with FAISS (free, fast)
- Deploy to production with OpenSearch (scalable, reliable)
- No code changes needed!

---

## Local Development Workflow

### Setup (First Time Only)

**1. Install dependencies:**
```bash
cd backend
pip install faiss-cpu pypdf boto3
```

**2. Add PDF documents:**
```bash
# Place PDFs in backend/documents/
cp ~/Downloads/*.pdf backend/documents/
```

**3. Ingest documents:**
```bash
cd backend
python ingest_documents.py
```

**Output:**
```
===========================================================
Evidence-Based Health Chatbot - Document Ingestion
===========================================================

1. Initializing document processor...
2. Initializing embeddings (AWS Bedrock Titan)...
3. Initializing vector store (FAISS)...

4. Loading PDFs from ./documents...
Processing: Protein-PDC-2024.pdf
Processing: Carbohydrates-PDC-2024.pdf
...
✓ Processed 4,484 text chunks from PDFs

5. Generating embeddings in batches of 10...
   Batch 1/449: Processing 10 chunks... ✓ (2.3s - 4.3 chunks/sec)
   Batch 2/449: Processing 10 chunks... ✓ (2.1s - 4.8 chunks/sec)
   ...
   ✓ Generated 4,484 embeddings total

6. Storing in vector database...
   Added 4,484 documents to FAISS. Total: 4,484

===========================================================
✅ Document Ingestion Complete!
===========================================================

Vector Store Stats:
  Type: faiss
  Total Documents: 4,484

Local files created:
  - faiss_index.bin (60 MB)
  - faiss_metadata.json (8 MB)

Your health chatbot is now ready to answer questions!
```

**Time:** ~15 minutes for 4,484 chunks

---

### Using RAG in the Chatbot

**Backend code (server.py):**
```python
from retrieval import HealthRAG

# Initialize RAG system
rag = HealthRAG(use_opensearch=False)  # Use FAISS locally

# User asks question
user_question = "What's the optimal protein intake?"

# Retrieve relevant context
context, sources = rag.retrieve_context(user_question, top_k=5)

# Send to GPT-4 with context
prompt = f"""
Context from research papers:
{context}

User question: {user_question}

Instructions: Answer using ONLY the provided context. Cite sources.
"""

response = openai.ChatCompletion.create(
    model="gpt-4",
    messages=[
        {"role": "system", "content": "You are an evidence-based fitness coach."},
        {"role": "user", "content": prompt}
    ]
)

answer = response.choices[0].message.content
```

**Output:**
```
Based on the research, optimal protein intake for muscle growth
is 1.6g per kg of bodyweight. Studies show that higher intakes
(2.2g/kg) provide no additional benefit in trained individuals.

Sources:
• Protein-PDC-2024.pdf, Page 12
• Muscle-Growth-PDC-2024.pdf, Page 8
```

---

## Production Workflow (OpenSearch)

### Setup OpenSearch

**1. Deploy with Terraform:**
```bash
cd terraform
terraform apply
```

**Creates:**
- OpenSearch Serverless collection
- Index: "health-docs"
- Security policies
- Network access

**2. Upload FAISS data to OpenSearch:**
```bash
cd backend
export OPENSEARCH_ENDPOINT=<from terraform output>
python upload_to_opensearch.py
```

**Output:**
```
===========================================================
Upload FAISS Vector Store to OpenSearch Serverless
===========================================================

1. Connecting to OpenSearch at https://...
2. Creating index...
   ✓ Created index: health-docs with dimension 1536
3. Uploading documents...
   ✓ Uploaded batch 1/45 (100 docs)
   ✓ Uploaded batch 2/45 (100 docs)
   ...
   ✓ Uploaded batch 45/45 (84 docs)

4. Verifying upload...
   ✓ Total documents in OpenSearch: 4,484

===========================================================
✅ Upload Complete!
===========================================================
```

**3. Configure Lambda:**
```bash
# In Lambda environment variables
USE_OPENSEARCH=true
OPENSEARCH_ENDPOINT=https://...aoss.amazonaws.com
```

**4. Deploy Lambda:**
```bash
./scripts/deploy.sh dev
```

Now the chatbot uses OpenSearch in production!

---

## Cost Analysis

### FAISS (Local Development)

**Costs:**
- FAISS library: FREE
- Local storage: FREE
- Compute: Your laptop

**Total: $0/month**

---

### OpenSearch Serverless

**AWS Pricing:**
```
OpenSearch Serverless:
- 1 OCU (OpenSearch Compute Unit) = $0.24/hour
- Minimum: 2 OCUs (1 for indexing, 1 for search)
- Hours per month: 730

Monthly cost:
2 OCUs × $0.24/hour × 730 hours = $350/month

Storage:
- First 10 GB: Included
- Additional: $0.024/GB/month

Total: ~$350-400/month minimum
```

**Add Terraform infrastructure:**
```
DynamoDB: ~$5/month
Lambda: ~$1/month
S3: ~$1/month
CloudFront: FREE (free tier)

Total with OpenSearch: ~$360/month
Total without OpenSearch: ~$10/month
```

**Why so expensive?**
OpenSearch Serverless reserves capacity 24/7, even when idle. It's designed for production workloads with consistent traffic.

**Alternatives:**
- OpenSearch Managed (cheaper, but requires server management)
- Pinecone (vector database, ~$70/month)
- Weaviate Cloud ($25/month starter)
- FAISS (free, but local only)

**FitTracker's strategy:**
Use FAISS locally, only enable OpenSearch for demos or if budget allows.

---

## File Structure

### Backend Files

```
backend/
├── documents/                    ← PDF research papers (source)
│   ├── Protein-PDC-2024.pdf
│   ├── Carbohydrates-PDC-2024.pdf
│   └── ...
│
├── document_processor.py         ← PDF → Chunks
├── embeddings.py                 ← Text → Vectors (Bedrock Titan)
├── vector_store.py               ← FAISS/OpenSearch adapter
├── retrieval.py                  ← RAG system (search + format)
│
├── ingest_documents.py           ← Script: Build vector DB
├── upload_to_opensearch.py       ← Script: FAISS → OpenSearch
├── delete_opensearch_index.py    ← Script: Clear OpenSearch
│
├── faiss_index.bin              ← FAISS vector database (60 MB)
├── faiss_metadata.json          ← Text chunks + metadata (8 MB)
│
└── server.py                     ← FastAPI server (uses HealthRAG)
```

---

## Real-World Usage Examples

### Example 1: User Asks About Protein

**User input:**
```
"Should I eat more protein to build muscle?"
```

**What happens:**

**Step 1: Embed question**
```python
query = "Should I eat more protein to build muscle?"
query_vector = embeddings.embed_query(query)
# [0.031, -0.122, 0.903, ..., 0.387]
```

**Step 2: Search FAISS**
```python
results = vector_store.search(query_vector, k=5)
```

**Results:**
```
1. "Protein intake of 1.6g/kg bodyweight is sufficient for
    muscle growth. Higher intakes provide no additional benefit..."
    Source: Protein-PDC-2024.pdf, Page 12
    Score: 0.12

2. "Muscle protein synthesis peaks at ~20-25g protein per meal.
    Consuming more does not increase synthesis..."
    Source: Muscle-Growth-PDC-2024.pdf, Page 8
    Score: 0.15

3. "Trained individuals require 1.6-2.2g/kg daily. The upper
    range is for those in caloric deficit..."
    Source: Protein-PDC-2024.pdf, Page 15
    Score: 0.18
```

**Step 3: Format context**
```
[Source 1: Protein-PDC-2024.pdf, Page 12]
Protein intake of 1.6g/kg bodyweight is sufficient...

[Source 2: Muscle-Growth-PDC-2024.pdf, Page 8]
Muscle protein synthesis peaks at ~20-25g protein...

[Source 3: Protein-PDC-2024.pdf, Page 15]
Trained individuals require 1.6-2.2g/kg daily...
```

**Step 4: Send to GPT-4**
```
Based on the research, you should aim for 1.6g of protein
per kg of bodyweight daily for muscle growth. Higher intakes
(beyond 2.2g/kg) don't provide additional benefits for trained
individuals. Focus on consistent intake rather than excessive
amounts.

Sources:
• Protein-PDC-2024.pdf, Page 12
• Muscle-Growth-PDC-2024.pdf, Page 8
```

**Total time:** ~3-5 seconds

---

### Example 2: User Asks About Cardio

**User input:**
```
"Will cardio kill my gains?"
```

**RAG process:**

**Top 5 chunks retrieved:**
```
1. "Concurrent training (resistance + cardio) does not
    significantly impair muscle growth when managed properly..."
    Source: Cardio-PDC-2024.pdf, Page 22

2. "Low to moderate intensity cardio (60-70% max HR) has
    minimal interference with strength adaptations..."
    Source: Cardio-PDC-2024.pdf, Page 18

3. "Excessive cardio (>5 hours/week) combined with inadequate
    nutrition can impair recovery and muscle protein synthesis..."
    Source: Recovery-PDC-2024.pdf, Page 31
```

**GPT-4 answer:**
```
No, cardio won't "kill your gains" when done properly. Research
shows that low to moderate intensity cardio (60-70% max heart rate)
has minimal impact on muscle growth. The key is moderation—keep
cardio to reasonable volumes and ensure adequate nutrition and
recovery.

Sources:
• Cardio-PDC-2024.pdf, Pages 18, 22
• Recovery-PDC-2024.pdf, Page 31
```

---

## Performance Metrics

### Local (FAISS)

```
Document ingestion:
- 4,484 chunks
- Time: ~15 minutes
- Storage: 68 MB (index + metadata)

Query time:
- Embedding: 500ms
- Search: 10ms
- Total (excluding GPT-4): 510ms

Accuracy:
- 100% (exact search)
```

### Cloud (OpenSearch)

```
Document ingestion:
- 4,484 chunks
- Upload time: ~5 minutes
- Storage: Managed by AWS

Query time:
- Embedding: 500ms
- Search: 50ms
- Total (excluding GPT-4): 550ms

Accuracy:
- ~99% (approximate search with HNSW)

Cost:
- $360/month (always on)
```

---

## Troubleshooting

### Issue 1: "No PDF files found"

**Error:**
```
No PDF files found in ./documents
```

**Solution:**
```bash
# Check documents directory exists
ls backend/documents/

# Add PDFs
cp ~/Downloads/*.pdf backend/documents/
```

---

### Issue 2: "FAISS index not found"

**Error:**
```
FileNotFoundError: faiss_index.bin
```

**Cause:** Haven't run ingestion script.

**Solution:**
```bash
cd backend
python ingest_documents.py
```

---

### Issue 3: "OpenSearch connection failed"

**Error:**
```
ConnectionError: Could not connect to OpenSearch
```

**Cause:** Wrong endpoint or missing permissions.

**Solution:**
```bash
# Check environment variable
echo $OPENSEARCH_ENDPOINT

# Should be: https://...aoss.amazonaws.com
# Get from Terraform output:
cd terraform
terraform output opensearch_endpoint

# Set in environment
export OPENSEARCH_ENDPOINT=https://...
```

---

### Issue 4: "Bedrock throttling"

**Error:**
```
ThrottlingException: Rate exceeded
```

**Cause:** Too many embedding requests.

**Solution:**
Ingestion script already handles this with:
- Batch processing (10 chunks at once)
- Retry logic
- Delays between batches

If still failing:
```python
# In ingest_documents.py
batch_size = 5  # Reduce from 10
time.sleep(1.0)  # Increase delay from 0.2s
```

---

## Advanced Topics

### Custom Chunking Strategy

**Current:**
- 1000 characters per chunk
- 200 character overlap

**Customization:**
```python
processor = DocumentProcessor(
    chunk_size=1500,  # Larger chunks
    chunk_overlap=300  # More overlap
)
```

**Trade-offs:**
- Larger chunks: More context, but less precise retrieval
- Smaller chunks: More precise, but may miss context
- More overlap: Better context preservation, but more storage

---

### Hybrid Search (Future Enhancement)

**Current:** Only semantic search (vector similarity)

**Hybrid approach:**
1. Semantic search (embeddings)
2. Keyword search (traditional)
3. Combine results

**Benefits:**
- Better for exact terms (brand names, numbers)
- Handles both concepts and specifics

**Implementation:**
OpenSearch supports hybrid search natively with BM25 + kNN.

---

### Reranking (Future Enhancement)

**Current:** Use top 5 chunks directly

**Reranking approach:**
1. Retrieve top 20 chunks (cast wide net)
2. Use reranker model to score relevance
3. Select top 5 from reranked results

**Benefits:**
- More accurate final results
- Better handles multi-hop queries

**Tools:**
- Cohere Rerank API
- Cross-encoder models

---

## Summary

**RAG (Retrieval-Augmented Generation)** makes AI chatbots smarter by:
1. Storing knowledge in a searchable database
2. Finding relevant information for each question
3. Using that information to generate accurate, cited answers

**OpenSearch** is a cloud-based search engine for:
- Vector similarity search (semantic understanding)
- Billions of documents
- Production-ready reliability

**FAISS** is a local alternative for:
- Development and testing
- Cost savings (free)
- Fast iteration

**FitTracker AI uses both:**
- **Local development:** FAISS (free, fast)
- **Production (optional):** OpenSearch (scalable, reliable)
- **Same code:** Adapter pattern allows switching

**The complete pipeline:**
```
PDFs → Chunks → Embeddings → Vector DB → Semantic Search → GPT-4 → Answer
```

**Key metrics:**
- Documents: 4,484 chunks
- Embedding dimension: 1536
- Search time: 10-50ms
- Total query time: 3-6 seconds
- Accuracy: 99-100%

**Cost comparison:**
- FAISS: $0/month
- OpenSearch: ~$360/month

Think of RAG as **"giving AI a textbook for every exam."** Instead of relying on memory, the AI looks up the answer in its knowledge base and cites the exact page it found the information!
