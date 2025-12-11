from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Import custom modules
from document_processor import LegalDocumentProcessor
from rag_pipeline import LegalRAGPipeline

app = FastAPI(title="Legal AI Assistant API")

# Configure CORS for frontend communication
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],  # Next.js default
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize core components
processor = LegalDocumentProcessor()
rag_pipeline = LegalRAGPipeline()

# Request/Response models
class QueryRequest(BaseModel):
    question: str
    history: Optional[List[dict]] = None

class QueryResponse(BaseModel):
    answer: str
    source_cases: Optional[List[str]] = None
    confidence: Optional[float] = None

class IngestionResponse(BaseModel):
    message: str
    documents_processed: int

@app.get("/")
def read_root():
    return {"message": "Legal AI Assistant API", "status": "operational"}

@app.post("/api/query", response_model=QueryResponse)
async def query_legal_assistant(request: QueryRequest):
    """
    Main endpoint for legal queries
    Processes natural language questions about legal cases
    """
    try:
        # Use RAG pipeline to get grounded response
        result = rag_pipeline.query(
            question=request.question,
            conversation_history=request.history
        )
        
        return QueryResponse(
            answer=result["answer"],
            source_cases=result.get("sources", []),
            confidence=result.get("confidence", 0.0)
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Query processing error: {str(e)}")

@app.post("/api/ingest")
async def ingest_documents():
    """
    Endpoint to process and ingest Excel case files
    Converts to vectors and stores in vector database
    """
    try:
        # Path to Excel file (configure in .env)
        excel_path = os.getenv("EXCEL_CASES_PATH", "./data/sentencias_pasadas.xlsx")
        
        # Process documents
        result = processor.process_excel_file(excel_path)
        
        # Store in vector database
        rag_pipeline.initialize_from_documents(result["documents"])
        
        return IngestionResponse(
            message="Documents successfully ingested",
            documents_processed=result["count"]
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Ingestion error: {str(e)}")

@app.get("/api/sample-questions")
async def get_sample_questions():
    """
    Returns sample questions for the frontend
    """
    return {
        "questions": [
            "¿Cuáles son las sentencias de 3 demandas?",
            "¿De qué se trataron las 3 demandas anteriores?",
            "¿Cuál fue la sentencia del caso que habla de acoso escolar?",
            "¿diga el detalle de la demanda relacionada con acoso escolar?",
            "¿existen casos que hablan sobre el PIAR, indique de que trataron los casos y cuáles fueron sus sentencias?"
        ]
    }