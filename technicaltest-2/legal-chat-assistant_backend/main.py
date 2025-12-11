from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from rag_pipeline import LegalRAGPipeline
import uvicorn
import logging

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title="Legal AI Assistant API", version="1.0.0")

# Configure CORS to allow requests from your React frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],  # Your React app's address
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize the RAG pipeline
rag_pipeline = LegalRAGPipeline()

class QueryRequest(BaseModel):
    question: str

class QueryResponse(BaseModel):
    answer: str
    confidence: float
    source_cases: list

@app.get("/")
def read_root():
    return {"message": "Legal AI Assistant API is running"}

@app.get("/health")
def health_check():
    return {"status": "healthy", "service": "legal-ai-assistant"}

@app.post("/query", response_model=QueryResponse)
async def query_legal_assistant(request: QueryRequest):
    """
    Main endpoint for querying the legal AI assistant.
    This is what your React frontend will call.
    """
    try:
        logger.info(f"Received query: {request.question}")
        
        # Use the RAG pipeline to get an answer
        answer, confidence, source_cases = rag_pipeline.query(request.question)
        
        return QueryResponse(
            answer=answer,
            confidence=confidence,
            source_cases=source_cases
        )
        
    except Exception as e:
        logger.error(f"Error processing query: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)