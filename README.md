# Evidence-Based Health Chatbot

An AI-powered health information chatbot that provides evidence-based answers using Retrieval-Augmented Generation (RAG) from verified medical textbooks and research documents.

## 🏥 Overview

This chatbot uses:
- **RAG Architecture**: Retrieves relevant information from medical documents before generating responses
- **AWS Bedrock**: Uses Amazon Nova models for natural language understanding
- **AWS Bedrock Titan Embeddings**: For semantic search of medical documents
- **Vector Database**: FAISS (local) or OpenSearch Serverless (production)
- **Strict Evidence-Based Responses**: Only answers from provided medical documents

## 🚀 Quick Start

### Prerequisites

- Python 3.12+
- Node.js 20+
- AWS Account (for production deployment)
- Docker (for Lambda packaging)
- OpenAI API key or AWS Bedrock access

### Local Development Setup

#### 1. Install Backend Dependencies

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
# AWS Configuration (for Bedrock embeddings and LLM)
DEFAULT_AWS_REGION=us-east-1

# OpenSearch (set to false for local development with FAISS)
USE_OPENSEARCH=false

# S3 Storage (set to false for local file storage)
USE_S3=false

# Bedrock Model
BEDROCK_MODEL_ID=amazon.nova-lite-v1:0

# CORS (for local development)
CORS_ORIGINS=http://localhost:3000
```

#### 3. Add Health Documents

Place your PDF health textbooks in `backend/documents/`:

```bash
# Example:
backend/documents/
├── medical_textbook_1.pdf
├── health_guidelines.pdf
└── research_paper.pdf
```

**Recommended**: 20-30 PDFs for comprehensive coverage

#### 4. Ingest Documents

Process and index your documents:

```bash
cd backend

# Make sure AWS credentials are configured
aws configure

# Run ingestion script
uv run python ingest_documents.py
```

This will:
- Extract text from PDFs
- Create text chunks (1000 chars with 200 overlap)
- Generate embeddings using AWS Bedrock Titan
- Store in FAISS vector database (local) or OpenSearch (prod)

#### 5. Start Backend Server

```bash
cd backend
uv run uvicorn server:app --reload
```

Server runs at: http://localhost:8000

#### 6. Install Frontend Dependencies

```bash
cd frontend
npm install
```

#### 7. Start Frontend

```bash
cd frontend
npm run dev
```

Frontend runs at: http://localhost:3000

## 📁 Project Structure

```
evidence-based-health-chatbot/
├── backend/
│   ├── documents/              # PDF health documents
│   ├── server.py              # FastAPI server with RAG
│   ├── context.py             # Health chatbot system prompts
│   ├── retrieval.py           # RAG retrieval logic
│   ├── vector_store.py        # Vector database operations
│   ├── embeddings.py          # AWS Bedrock Titan embeddings
│   ├── document_processor.py  # PDF processing and chunking
│   ├── ingest_documents.py    # Document ingestion script
│   └── requirements.txt       # Python dependencies
├── frontend/
│   ├── app/
│   │   └── page.tsx          # Main page
│   ├── components/
│   │   └── health-chat.tsx   # Chat interface
│   └── package.json
└── README.md
```

## 🧠 How It Works

### RAG (Retrieval-Augmented Generation) Flow

1. **User asks a health question** → "What are the symptoms of hypertension?"

2. **Query Embedding** → Convert question to vector using Bedrock Titan

3. **Semantic Search** → Find top 5 most relevant chunks from medical documents

4. **Context Building** → Combine relevant chunks with source information

5. **LLM Generation** → AWS Bedrock Nova generates answer using ONLY the retrieved context

6. **Response** → Answer with medical disclaimers

### Key Features

- ✅ **Evidence-Based Only**: Will say "I don't know" if information isn't in documents
- ✅ **Source Tracking**: Tracks which document and page information came from
- ✅ **URL Extraction**: Extracts research paper links from PDFs
- ✅ **Medical Disclaimers**: Always includes appropriate health disclaimers
- ✅ **Conversation Memory**: Maintains chat history per session

## 🔧 Configuration

### Bedrock Models

Available models (configure in `.env`):

```bash
# Fastest, most cost-effective
BEDROCK_MODEL_ID=amazon.nova-micro-v1:0

# Balanced (recommended)
BEDROCK_MODEL_ID=amazon.nova-lite-v1:0

# Most capable
BEDROCK_MODEL_ID=amazon.nova-pro-v1:0
```

### Vector Store Options

**Local Development (FAISS)**:
```bash
USE_OPENSEARCH=false
```
- Stores vectors in `backend/faiss_index.pkl`
- Metadata in `backend/faiss_metadata.json`

**Production (OpenSearch Serverless)**:
```bash
USE_OPENSEARCH=true
OPENSEARCH_ENDPOINT=https://your-collection.us-east-1.aoss.amazonaws.com
```

### Document Chunking

Adjust in `ingest_documents.py`:

```python
processor = DocumentProcessor(
    chunk_size=1000,      # Characters per chunk
    chunk_overlap=200     # Overlap between chunks
)
```

## 🌐 AWS Deployment

### Prerequisites

1. **AWS CLI configured** with appropriate credentials
2. **Terraform installed**
3. **Docker running** (for Lambda packaging)

### Deploy to AWS

```bash
# Deploy to dev environment
./scripts/deploy.sh dev

# Deploy to production
./scripts/deploy.sh prod
```

### Required AWS Services

- **AWS Bedrock**: For embeddings and LLM
- **Amazon OpenSearch Serverless**: Vector database
- **AWS Lambda**: Serverless backend
- **API Gateway**: REST API
- **S3**: Static hosting + conversation memory
- **CloudFront**: CDN for global delivery

## 🧪 Testing

### Test Backend API

```bash
# Health check
curl http://localhost:8000/health

# Get stats
curl http://localhost:8000/stats

# Chat
curl -X POST http://localhost:8000/chat \
  -H "Content-Type: application/json" \
  -d '{"message": "What are symptoms of diabetes?"}'
```

### Test Document Ingestion

```bash
cd backend

# Test with sample documents
uv run python ingest_documents.py

# Check vector store stats
curl http://localhost:8000/stats
```

## 📊 Monitoring

### Local Development

- Backend logs: Terminal running `uvicorn`
- Frontend logs: Browser console
- Vector store: Check `faiss_index.pkl` and `faiss_metadata.json`

### AWS Production

- **CloudWatch Logs**: `/aws/lambda/health-chatbot-api`
- **Bedrock Metrics**: Token usage, latency
- **OpenSearch**: Index statistics
- **Lambda**: Invocations, duration, errors

## 🔒 Security & Disclaimers

### Medical Disclaimer

**This chatbot provides educational information only and does NOT:**
- Diagnose medical conditions
- Prescribe treatments
- Replace professional medical advice
- Handle medical emergencies

Always consult healthcare professionals for medical concerns.

### Data Privacy

- Conversations stored in S3 or local files
- No personal health information should be shared
- HIPAA compliance not guaranteed
- Use for educational purposes only

### Security Best Practices

1. **Never commit** `.env` files or AWS credentials
2. **Restrict CORS** in production
3. **Use IAM roles** with minimum required permissions
4. **Enable encryption** for S3 and OpenSearch
5. **Regular security audits** of dependencies

## 🛠️ Troubleshooting

### "No documents found"

- Ensure PDFs are in `backend/documents/`
- Check PDF file permissions
- Verify PDF format (not scanned images)

### "Bedrock access denied"

```bash
# Check AWS credentials
aws sts get-caller-identity

# Verify Bedrock model access
aws bedrock list-foundation-models --region us-east-1
```

### "Vector store empty"

- Run `ingest_documents.py` to populate
- Check for errors during ingestion
- Verify embeddings were generated

### "Context not found"

- Documents may not contain relevant information
- Try different phrasing
- Add more comprehensive medical documents

## 📚 Dependencies

### Backend

- `fastapi` - Web framework
- `boto3` - AWS SDK
- `pypdf` - PDF parsing
- `langchain` - RAG orchestration
- `faiss-cpu` - Local vector database
- `opensearch-py` - OpenSearch client

### Frontend

- `next.js` - React framework
- `tailwindcss` - Styling
- `lucide-react` - Icons

## 🤝 Contributing

1. Add more health documents to improve coverage
2. Enhance chunking strategies for better context
3. Add citation display in UI
4. Implement document management interface
5. Add conversation export features

## 📝 License

This project is for educational purposes. Ensure proper licensing for any medical documents used.

## 🎯 Next Steps

### Enhancements

- [ ] Add conversation analytics
- [ ] Implement user feedback loop
- [ ] Add document upload via UI
- [ ] Multi-language support
- [ ] Voice interface
- [ ] Mobile app

### Production Readiness

- [ ] Add rate limiting
- [ ] Implement caching layer
- [ ] Set up monitoring alerts
- [ ] Add automated testing
- [ ] HIPAA compliance review (if needed)
- [ ] Load testing

## 📞 Support

For issues or questions:
1. Check troubleshooting section
2. Review AWS Bedrock documentation
3. Check CloudWatch logs
4. Verify PDF document quality

---

**Remember**: This is an educational tool. Always consult qualified healthcare professionals for medical advice.
