from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional
import os
from dotenv import load_dotenv

# Cargar variables de entorno
load_dotenv()

# Importar módulos personalizados
try:
    from document_processor import LegalDocumentProcessor
    from rag_pipeline import LegalRAGPipeline
    print("Módulos importados correctamente")
except ImportError as e:
    print(f"Error de importación: {e}")
    raise

app = FastAPI(
    title="Legal AI Assistant API",
    description="API para consulta de historial de demandas legales usando IA Generativa",
    version="1.0.0"
)

# Configurar CORS para comunicación con frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:8000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Inicializar componentes principales
processor = LegalDocumentProcessor()
rag_pipeline = LegalRAGPipeline(use_local_embeddings=True)

# Modelos de solicitud/respuesta
class QueryRequest(BaseModel):
    question: str
    history: Optional[List[dict]] = None

class QueryResponse(BaseModel):
    answer: str
    source_cases: Optional[List[dict]] = None
    confidence: Optional[float] = None

class IngestionResponse(BaseModel):
    message: str
    documents_processed: int
    original_cases: int

@app.get("/")
def read_root():
    return {
        "message": "Legal AI Assistant API - Prueba de Concepto",
        "status": "operational",
        "endpoints": {
            "POST /api/query": "Consultar casos legales",
            "POST /api/ingest": "Procesar documentos Excel",
            "GET /api/health": "Verificar estado del sistema",
            "GET /api/sample-questions": "Preguntas de ejemplo"
        }
    }

@app.get("/api/health")
async def health_check():
    """Verificar que todos los componentes estén funcionando"""
    try:
        return {
            "status": "healthy",
            "embeddings": "SentenceTransformer local",
            "vector_store": "ChromaDB",
            "llm": "FakeListLLM (modo prueba)"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Health check failed: {str(e)}")

@app.post("/api/query", response_model=QueryResponse)
async def query_legal_assistant(request: QueryRequest):
    """
    Endpoint principal para consultas legales
    Procesa preguntas en lenguaje natural sobre casos legales
    """
    try:
        print(f"Consulta recibida: {request.question}")
        
        # Usar pipeline RAG para obtener respuesta contextual
        result = rag_pipeline.query(
            question=request.question,
            conversation_history=request.history
        )
        
        print(f"Respuesta generada: {len(result['answer'])} caracteres")
        
        return QueryResponse(
            answer=result["answer"],
            source_cases=result.get("sources", []),
            confidence=result.get("confidence", 0.0)
        )
    except Exception as e:
        print(f"Error en consulta: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error procesando la consulta: {str(e)}")

@app.post("/api/ingest", response_model=IngestionResponse)
async def ingest_documents():
    """
    Endpoint para procesar e ingerir archivos Excel de casos
    Convierte a vectores y almacena en base de datos vectorial
    """
    try:
        # Ruta al archivo Excel (configurar en .env)
        excel_path = os.getenv("EXCEL_CASES_PATH", "./data/sentencias_pasadas.xlsx")
        
        if not os.path.exists(excel_path):
            # Crear archivo de ejemplo si no existe
            from create_sample_data import create_sample_excel
            create_sample_excel(excel_path)
            print(f"Archivo de ejemplo creado: {excel_path}")
        
        print(f"Procesando archivo: {excel_path}")
        
        # Procesar documentos
        result = processor.process_excel_file(excel_path)
        
        # Almacenar en base de datos vectorial
        rag_pipeline.initialize_from_documents(result["documents"])
        
        return IngestionResponse(
            message="Documentos procesados e ingestados exitosamente",
            documents_processed=result["count"],
            original_cases=result["original_cases"]
        )
    except Exception as e:
        print(f"Error en ingestión: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error en ingestión: {str(e)}")

@app.get("/api/sample-questions")
async def get_sample_questions():
    """
    Retorna preguntas de ejemplo para el frontend
    """
    return {
        "questions": [
            "¿Cuáles son las sentencias de 3 demandas?",
            "¿De qué se trataron las 3 demandas anteriores?",
            "¿Cuál fue la sentencia del caso que habla de acoso escolar?",
            "¿diga el detalle de la demanda relacionada con acoso escolar?",
            "¿existen casos que hablan sobre el PIAR, indique de que trataron los casos y cuáles fueron sus sentencias?"
        ],
        "instructions": "Las respuestas se dan en lenguaje coloquial para personas sin conocimientos de derecho"
    }