"""
FastAPI backend for Alaska FAQ RAG system
"""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional
import os
from dotenv import load_dotenv

# Import our existing modules
from rag_system import initialize_services, search_knowledge_base, generate_response
from prompt_validator import initialize_validator, validate_prompt

# Load environment variables
load_dotenv()

# Initialize FastAPI app
app = FastAPI(
    title="Alaska FAQ RAG API",
    description="API for Alaska Department FAQ system using RAG",
    version="1.0.0"
)

# Add CORS middleware for frontend access
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify your frontend URL
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Request/Response models
class QuestionRequest(BaseModel):
    question: str

class QuestionResponse(BaseModel):
    question: str
    answer: str
    context_found: bool
    validation_status: str
    error: Optional[str] = None

# Initialize services on startup
bq_client = None
genai_model = None
validator_model = None

@app.on_event("startup")
async def startup_event():
    """Initialize services when API starts"""
    global bq_client, genai_model, validator_model
    
    print("🚀 Initializing services...")
    try:
        bq_client, genai_model = initialize_services()
        validator_model = initialize_validator()
        print("✅ All services initialized successfully")
    except Exception as e:
        print(f"❌ Error initializing services: {e}")

# Health check endpoint
@app.get("/")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "service": "Alaska FAQ RAG API",
        "version": "1.0.0"
    }

# Main RAG endpoint
@app.post("/ask", response_model=QuestionResponse)
async def ask_question(request: QuestionRequest):
    """
    Process a question through the RAG system
    
    Steps:
    1. Validate the prompt for safety
    2. Search knowledge base for relevant context
    3. Generate response using Gemini
    """
    
    question = request.question.strip()
    
    # Check if question is empty
    if not question:
        raise HTTPException(status_code=400, detail="Question cannot be empty")
    
    try:
        # Step 1: Validate prompt
        is_valid, validation_msg = validate_prompt(validator_model, question)
        
        if not is_valid:
            return QuestionResponse(
                question=question,
                answer=f"I cannot process this question: {validation_msg}",
                context_found=False,
                validation_status="blocked",
                error=validation_msg
            )
        
        # Step 2: Search knowledge base
        context = search_knowledge_base(bq_client, question)
        
        if not context:
            return QuestionResponse(
                question=question,
                answer="I couldn't find information about that topic in the Alaska FAQ database. Please try rephrasing your question or contact support.",
                context_found=False,
                validation_status="passed",
                error=None
            )
        
        # Step 3: Generate response
        answer = generate_response(genai_model, question, context)
        
        return QuestionResponse(
            question=question,
            answer=answer,
            context_found=True,
            validation_status="passed",
            error=None
        )
        
    except Exception as e:
        # Log error (in production, use proper logging)
        print(f"Error processing question: {e}")
        
        raise HTTPException(
            status_code=500,
            detail=f"An error occurred while processing your question: {str(e)}"
        )

# Test endpoint for debugging
@app.get("/test")
async def test_endpoint():
    """Test endpoint to verify services are working"""
    return {
        "bigquery_connected": bq_client is not None,
        "gemini_connected": genai_model is not None,
        "validator_connected": validator_model is not None,
        "environment": {
            "project_id": os.getenv("PROJECT_ID"),
            "api_key_set": bool(os.getenv("GEMINI_API_KEY"))
        }
    }

# List sample questions endpoint
@app.get("/sample-questions")
async def get_sample_questions():
    """Return sample questions users can ask"""
    return {
        "questions": [
            "What are the snow removal procedures?",
            "How do I report hazardous road conditions?",
            "What are the winter emergency protocols?",
            "When do emergency shelters open?",
            "How quickly are main roads cleared after snowfall?"
        ]
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8080)