from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Dict, Any
import uvicorn
import logging
from datetime import datetime
import sys
import os
import json

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Agregar directorio actual al path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Importar módulos RAG
from rag_pipeline import LegalRAGPipeline
from document_processor import DocumentProcessor

app = FastAPI(
    title="Legal AI Assistant API",
    description="API para consulta de historial de demandas legales usando RAG",
    version="3.0.0"
)

# Configuración CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # En producción, especificar dominios
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Modelos Pydantic
class QueryRequest(BaseModel):
    question: str

class QueryResponse(BaseModel):
    answer: str
    confidence: float
    matched_cases: List[dict]
    timestamp: str
    total_cases_searched: int
    rag_used: bool

# Inicializar RAG pipeline global
rag_pipeline = None
TOTAL_CASES = 0

def initialize_rag_system():
    """Inicializa el sistema RAG con datos del Excel"""
    global rag_pipeline, TOTAL_CASES
    
    try:
        logger.info(" Inicializando sistema RAG...")
        
        # 1. Crear pipeline RAG
        rag_pipeline = LegalRAGPipeline()
        
        # 2. Procesar archivo Excel
        processor = DocumentProcessor(rag_pipeline)
        
        # Ruta al archivo de datos
        data_file = "data/sentencias_pasadas.xlsx"
        
        if not os.path.exists(data_file):
            # Crear datos de ejemplo si no existe
            logger.warning(f" Archivo {data_file} no encontrado. Creando datos de ejemplo...")
            create_sample_data(data_file)
        
        # 3. Procesar casos
        TOTAL_CASES = processor.process_excel_file(data_file)
        
        logger.info(f" Sistema RAG inicializado con {TOTAL_CASES} casos")
        return True
        
    except Exception as e:
        logger.error(f" Error inicializando RAG: {e}")
        return False

def create_sample_data(file_path: str):
    """Crea datos de ejemplo para pruebas"""
    import pandas as pd
    
    sample_data = [
        {
            "Relevancia": "Alta",
            "Providencia": "Sentencia 2023-001",
            "Tipo": "Difamación en redes sociales",
            "Fecha Sentencia": "2023-01-15",
            "Tema - subtema": "Redes Sociales / Facebook",
            "resuelve": "Condena por difamación digital con multa de $10,000",
            "sintesis": "Usuario publicó información falsa sobre competidor en Facebook, afectando su reputación"
        },
        {
            "Relevancia": "Alta",
            "Providencia": "Sentencia 2023-045",
            "Tipo": "Acoso Escolar",
            "Fecha Sentencia": "2023-03-22",
            "Tema - subtema": "Educación / Acoso Digital",
            "resuelve": "Protección a víctima y medidas correctivas para el acosador",
            "sintesis": "Acoso mediante WhatsApp entre estudiantes de colegio, con mensajes amenazantes"
        },
        {
            "Relevancia": "Media",
            "Providencia": "Auto 2023-067",
            "Tipo": "PIAR - Inclusión Educativa",
            "Fecha Sentencia": "2023-05-10",
            "Tema - subtema": "Educación / Inclusión",
            "resuelve": "Obligatoriedad de implementar Protocolo de Inclusión y Acompañamiento",
            "sintesis": "Escuela no aplicó Protocolo de Inclusión y Acompañamiento para estudiante con necesidades especiales"
        },
        {
            "Relevancia": "Media",
            "Providencia": "Sentencia 2023-089",
            "Tipo": "Suplantación de identidad",
            "Fecha Sentencia": "2023-07-18",
            "Tema - subtema": "Redes Sociales / Instagram",
            "resuelve": "Cierre de cuenta falsa y compensación por daños morales",
            "sintesis": "Creación de perfil falso en Instagram usando fotos e información personal"
        },
        {
            "Relevancia": "Baja",
            "Providencia": "Auto 2023-112",
            "Tipo": "Derecho al olvido digital",
            "Fecha Sentencia": "2023-09-05",
            "Tema - subtema": "Internet / Privacidad",
            "resuelve": "Orden de eliminar información personal antigua de buscadores",
            "sintesis": "Persona solicita eliminar información personal desactualizada de resultados de búsqueda"
        }
    ]
    
    # Crear directorio si no existe
    os.makedirs(os.path.dirname(file_path), exist_ok=True)
    
    # Guardar como Excel
    df = pd.DataFrame(sample_data)
    df.to_excel(file_path, index=False)
    logger.info(f" Datos de ejemplo creados en: {file_path}")

# Inicializar al iniciar
initialize_rag_system()

@app.get("/")
async def root():
    return {
        "message": "Legal AI Assistant API - Prueba Técnica DataKnow",
        "version": "3.0.0",
        "status": "active",
        "cases_loaded": TOTAL_CASES,
        "rag_system": "Operativo" if rag_pipeline else "No disponible",
        "endpoints": {
            "GET /health": "Verificar estado del sistema",
            "POST /query": "Consultar casos legales",
            "GET /cases": "Listar casos disponibles",
            "GET /debug": "Información de diagnóstico",
            "GET /test": "Prueba de conectividad"
        }
    }

@app.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "service": "legal-ai-assistant",
        "timestamp": datetime.now().isoformat(),
        "cases_loaded": TOTAL_CASES,
        "rag_available": rag_pipeline is not None,
        "vector_database": "FAISS",
        "embedding_model": "all-MiniLM-L6-v2"
    }

@app.get("/test")
async def test_endpoint():
    return {
        "status": "success",
        "message": "Backend funcionando correctamente",
        "url": "http://127.0.0.1:8000",
        "timestamp": datetime.now().isoformat()
    }

@app.get("/cases")
async def get_cases(limit: int = 10):
    """Devuelve lista de casos (solo metadatos)"""
    # Nota: No podemos devolver todos los casos desde FAISS directamente
    # En un sistema real, tendríamos una base de datos adicional
    return {
        "message": f"Sistema contiene {TOTAL_CASES} casos en base de datos vectorial",
        "sample_queries": [
            "¿Cuáles son las sentencias de 3 demandas?",
            "¿De qué se trataron las 3 demandas anteriores?",
            "¿Cuál fue la sentencia del caso que habla de acoso escolar?",
            "¿Diga el detalle de la demanda relacionada con acoso escolar?",
            "¿Existen casos que hablan sobre el PIAR?"
        ]
    }

@app.post("/query")
async def query_legal_cases(request: QueryRequest):
    """Endpoint principal para consultas"""
    question = request.question
    logger.info(f" Pregunta recibida: {question}")
    
    try:
        if not rag_pipeline:
            raise HTTPException(
                status_code=503,
                detail="Sistema RAG no disponible. Intenta reiniciar el backend."
            )
        
        # 1. Buscar casos similares usando embeddings
        similar_cases = rag_pipeline.search_similar_cases(question, k=5)
        
        # 2. Generar respuesta usando RAG
        answer = rag_pipeline.generate_answer(question, similar_cases)
        
        # 3. Calcular confianza basada en similitud
        confidence = 0.8
        if similar_cases and len(similar_cases) > 0:
            confidence = min(0.95, similar_cases[0].get("similarity_score", 0.7))
        
        # 4. Preparar respuesta
        response = {
            "answer": answer,
            "confidence": confidence,
            "matched_cases": [
                {
                    "Tipo": case.get("Tipo", "Desconocido"),
                    "Tema": case.get("Tema_subtema", "No especificado"),
                    "Resumen": case.get("sintesis", "No especificado")[:150] + "...",
                    "Similaridad": f"{case.get('similarity_score', 0)*100:.1f}%"
                }
                for case in similar_cases[:3]  # Mostrar solo top 3
            ],
            "timestamp": datetime.now().isoformat(),
            "total_cases_searched": TOTAL_CASES,
            "rag_used": True
        }
        
        logger.info(f" Pregunta procesada: {len(similar_cases)} casos encontrados")
        return response
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f" Error en query: {e}")
        raise HTTPException(status_code=500, detail=f"Error interno: {str(e)}")

@app.get("/debug")
async def debug_info():
    """Endpoint para diagnóstico"""
    return {
        "backend_status": "running",
        "python_version": sys.version,
        "working_directory": os.getcwd(),
        "data_file_exists": os.path.exists("data/sentencias_pasadas.xlsx"),
        "total_cases": TOTAL_CASES,
        "rag_initialized": rag_pipeline is not None,
        "openai_available": rag_pipeline.openai_client is not None if rag_pipeline else False,
        "faiss_index_size": TOTAL_CASES,
        "timestamp": datetime.now().isoformat()
    }

if __name__ == "__main__":
    print("=" * 70)
    print("LEGAL AI ASSISTANT - BACKEND COMPLETO V3.0")
    print("=" * 70)
    print(f" Casos cargados en FAISS: {TOTAL_CASES}")
    print(f" URL API: http://127.0.0.1:8000")
    print(f" Health check: http://127.0.0.1:8000/health")
    print(f" Debug info: http://127.0.0.1:8000/debug")
    print("=" * 70)
    print("Preguntas de prueba técnica listas:")
    print("1. ¿Cuáles son las sentencias de 3 demandas?")
    print("2. ¿De qué se trataron las 3 demandas anteriores?")
    print("3. ¿Cuál fue la sentencia del caso que habla de acoso escolar?")
    print("4. ¿Diga el detalle de la demanda relacionada con acoso escolar?")
    print("5. ¿Existen casos que hablan sobre el PIAR?")
    print("=" * 70)
    
    uvicorn.run(
        app,
        host="127.0.0.1",
        port=8000,
        reload=True,
        log_level="info"
    )