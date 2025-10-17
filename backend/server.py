from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import os
from dotenv import load_dotenv
from typing import Optional, List, Dict
import json
import uuid
from datetime import datetime
import boto3
from botocore.exceptions import ClientError
from context import get_health_prompt
from retrieval import HealthRAG
from energy_calculator import EnergyCalculator, EnergyCalculatorInput, EnergyCalculatorOutput
from workout_planner import WorkoutPlanner, WorkoutPlannerInput, WorkoutPlanOutput

# Load environment variables
load_dotenv()

app = FastAPI()

# Configure CORS
origins = os.getenv("CORS_ORIGINS", "http://localhost:3000").split(",")
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=False,
    allow_methods=["GET", "POST", "OPTIONS"],
    allow_headers=["*"],
)

# Initialize Bedrock client
bedrock_client = boto3.client(
    service_name="bedrock-runtime",
    region_name=os.getenv("DEFAULT_AWS_REGION", "us-east-1")
)

# Bedrock model selection
BEDROCK_MODEL_ID = os.getenv("BEDROCK_MODEL_ID", "amazon.nova-lite-v1:0")

# Memory storage configuration
USE_S3 = os.getenv("USE_S3", "false").lower() == "true"
S3_BUCKET = os.getenv("S3_BUCKET", "")
MEMORY_DIR = os.getenv("MEMORY_DIR", "../memory")

# Initialize S3 client if needed
if USE_S3:
    s3_client = boto3.client("s3")

# Initialize RAG system
USE_OPENSEARCH = os.getenv("USE_OPENSEARCH", "false").lower() == "true"
rag_system = HealthRAG(use_opensearch=USE_OPENSEARCH)

# Initialize Workout Planner
workout_planner = WorkoutPlanner(bedrock_client=bedrock_client, model_id=BEDROCK_MODEL_ID)


# Request/Response models
class ChatRequest(BaseModel):
    message: str
    session_id: Optional[str] = None


class ChatResponse(BaseModel):
    response: str
    session_id: str


class Message(BaseModel):
    role: str
    content: str
    timestamp: str


# Memory management functions
def get_memory_path(session_id: str) -> str:
    return f"{session_id}.json"


def load_conversation(session_id: str) -> List[Dict]:
    """Load conversation history from storage"""
    if USE_S3:
        try:
            response = s3_client.get_object(Bucket=S3_BUCKET, Key=get_memory_path(session_id))
            return json.loads(response["Body"].read().decode("utf-8"))
        except ClientError as e:
            if e.response["Error"]["Code"] == "NoSuchKey":
                return []
            raise
    else:
        # Local file storage
        file_path = os.path.join(MEMORY_DIR, get_memory_path(session_id))
        if os.path.exists(file_path):
            with open(file_path, "r") as f:
                return json.load(f)
        return []


def save_conversation(session_id: str, messages: List[Dict]):
    """Save conversation history to storage"""
    if USE_S3:
        s3_client.put_object(
            Bucket=S3_BUCKET,
            Key=get_memory_path(session_id),
            Body=json.dumps(messages, indent=2),
            ContentType="application/json",
        )
    else:
        # Local file storage
        os.makedirs(MEMORY_DIR, exist_ok=True)
        file_path = os.path.join(MEMORY_DIR, get_memory_path(session_id))
        with open(file_path, "w") as f:
            json.dump(messages, f, indent=2)


def call_bedrock_with_context(user_message: str, context: str) -> str:
    """Call AWS Bedrock with retrieved context"""

    # Generate system prompt with context
    system_prompt = get_health_prompt(context)

    # Build messages in Bedrock format
    messages = [
        {
            "role": "user",
            "content": [{"text": f"System: {system_prompt}"}]
        },
        {
            "role": "user",
            "content": [{"text": user_message}]
        }
    ]

    try:
        # Call Bedrock using the converse API
        response = bedrock_client.converse(
            modelId=BEDROCK_MODEL_ID,
            messages=messages,
            inferenceConfig={
                "maxTokens": 2000,
                "temperature": 0.3,  # Lower temperature for more factual responses
                "topP": 0.9
            }
        )

        # Extract the response text
        return response["output"]["message"]["content"][0]["text"]

    except ClientError as e:
        error_code = e.response['Error']['Code']
        if error_code == 'ValidationException':
            print(f"Bedrock validation error: {e}")
            raise HTTPException(status_code=400, detail="Invalid message format for Bedrock")
        elif error_code == 'AccessDeniedException':
            print(f"Bedrock access denied: {e}")
            raise HTTPException(status_code=403, detail="Access denied to Bedrock model")
        else:
            print(f"Bedrock error: {e}")
            raise HTTPException(status_code=500, detail=f"Bedrock error: {str(e)}")


@app.get("/")
async def root():
    stats = rag_system.get_stats()
    return {
        "message": "Evidence-Based Health Chatbot API",
        "memory_enabled": True,
        "storage": "S3" if USE_S3 else "local",
        "ai_model": BEDROCK_MODEL_ID,
        "vector_store": stats
    }


@app.get("/health")
async def health_check():
    stats = rag_system.get_stats()
    return {
        "status": "healthy",
        "use_s3": USE_S3,
        "bedrock_model": BEDROCK_MODEL_ID,
        "vector_store": stats
    }


@app.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest):
    try:
        # Generate session ID if not provided
        session_id = request.session_id or str(uuid.uuid4())

        # Load conversation history
        conversation = load_conversation(session_id)

        # Retrieve relevant context from medical documents
        context, sources = rag_system.retrieve_context(request.message, top_k=5)

        # Call Bedrock with context for response
        assistant_response = call_bedrock_with_context(request.message, context)

        # Update conversation history
        conversation.append(
            {"role": "user", "content": request.message, "timestamp": datetime.now().isoformat()}
        )
        conversation.append(
            {
                "role": "assistant",
                "content": assistant_response,
                "timestamp": datetime.now().isoformat(),
            }
        )

        # Save conversation
        save_conversation(session_id, conversation)

        return ChatResponse(response=assistant_response, session_id=session_id)

    except HTTPException:
        raise
    except Exception as e:
        print(f"Error in chat endpoint: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/conversation/{session_id}")
async def get_conversation(session_id: str):
    """Retrieve conversation history"""
    try:
        conversation = load_conversation(session_id)
        return {"session_id": session_id, "messages": conversation}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/stats")
async def get_stats():
    """Get RAG system statistics"""
    try:
        stats = rag_system.get_stats()
        return stats
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/calculate-energy", response_model=EnergyCalculatorOutput)
async def calculate_energy(input_data: EnergyCalculatorInput):
    """
    Calculate energy expenditure and intake metrics

    Accepts user's physical attributes and training schedule,
    returns calculated energy metrics including BMR, energy expenditure,
    and target energy intake.
    """
    try:
        result = EnergyCalculator.calculate_all(input_data)
        return result
    except Exception as e:
        print(f"Error in energy calculation: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/generate-workout-plan", response_model=WorkoutPlanOutput)
async def generate_workout_plan(input_data: WorkoutPlannerInput):
    """
    Generate a personalized workout plan using AI

    Accepts user's training profile (training status, age, sex, recovery factor, etc.)
    and generates a customized workout plan that:
    - Calculates optimal training volume per muscle group
    - Selects appropriate exercises from the exercise database
    - Distributes volume across training days
    - Sets appropriate intensities based on training level

    The workout plan is generated using AWS Bedrock LLM to create flexible,
    personalized programs that meet all specified constraints.
    """
    try:
        result = workout_planner.generate_workout_plan(input_data)
        return result
    except Exception as e:
        print(f"Error in workout plan generation: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)
