import faiss
import numpy as np
from sentence_transformers import SentenceTransformer
from openai import OpenAI
import os
import logging
from typing import List, Dict, Any

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class LegalRAGPipeline:
    def __init__(self):
        # Usar modelo de embeddings más pequeño y eficiente
        self.model = SentenceTransformer("all-MiniLM-L6-v2")
        self.dimension = 384
        
        # Inicializar índice FAISS
        self.index = faiss.IndexFlatL2(self.dimension)
        self.metadata_store = {}
        
        # Configurar OpenAI
        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key:
            logger.warning("OPENAI_API_KEY no encontrada. Usando respuestas simuladas.")
            self.openai_client = None
        else:
            self.openai_client = OpenAI(api_key=api_key)
    
    def add_case(self, text: str, metadata: dict):
        """Agrega un caso al vector database"""
        if not text or len(text.strip()) == 0:
            return
        
        embedding = self.model.encode([text]).astype("float32")
        vector_id = len(self.metadata_store)
        
        self.index.add(embedding)
        self.metadata_store[vector_id] = {
            "text": text,
            **metadata
        }
    
    def search_similar_cases(self, query: str, k: int = 5) -> List[Dict]:
        """Busca casos similares usando embeddings"""
        try:
            query_embedding = self.model.encode([query]).astype("float32")
            distances, indices = self.index.search(query_embedding, k)
            
            results = []
            for idx, distance in zip(indices[0], distances[0]):
                if idx != -1 and idx in self.metadata_store:
                    case = self.metadata_store[idx].copy()
                    case["similarity_score"] = float(1 / (1 + distance))
                    results.append(case)
            
            return results
        except Exception as e:
            logger.error(f"Error en búsqueda: {e}")
            return []
    
    def generate_answer(self, question: str, relevant_cases: List[Dict]) -> str:
        """Genera respuesta usando GPT o fallback"""
        
        if not relevant_cases:
            return "No encontré casos relevantes en la base de datos. ¿Podrías reformular tu pregunta?"
        
        # Construir contexto con los casos relevantes
        context = "\n\n".join([
            f"Caso #{i+1}:\n"
            f"- Tipo: {case.get('Tipo', 'No especificado')}\n"
            f"- Tema: {case.get('Tema_subtema', 'No especificado')}\n"
            f"- Resolución: {case.get('resuelve', 'No especificada')}\n"
            f"- Resumen: {case.get('sintesis', 'No especificada')}"
            for i, case in enumerate(relevant_cases[:3])  # Usar máximo 3 casos
        ])
        
        # Si no hay OpenAI, usar respuesta simple
        if not self.openai_client:
            return self._generate_simple_answer(question, relevant_cases)
        
        # Usar GPT para generar respuesta coloquial
        try:
            prompt = f"""
Eres un asistente legal que explica casos legales en lenguaje sencillo para personas sin conocimientos de derecho.

CONTEXTO (casos legales reales):
{context}

PREGUNTA DEL USUARIO:
{question}

INSTRUCCIONES:
1. Responde EN ESPAÑOL y en lenguaje coloquial
2. Usa solo la información del contexto (NO inventes nada)
3. Sé claro y conciso
4. Si hay múltiples casos, menciona los más relevantes
5. Explica qué pasó y cuál fue el resultado

RESPUESTA:
"""
            
            response = self.openai_client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {"role": "system", "content": "Eres un asistente legal amigable que explica casos legales en términos simples."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.3,
                max_tokens=500
            )
            
            return response.choices[0].message.content
            
        except Exception as e:
            logger.error(f"Error con OpenAI: {e}")
            return self._generate_simple_answer(question, relevant_cases)
    
    def _generate_simple_answer(self, question: str, cases: List[Dict]) -> str:
        """Genera respuesta simple sin OpenAI"""
        if "sentencias de 3 demandas" in question.lower():
            return self._answer_3_sentences(cases)
        elif "se trataron las 3 demandas" in question.lower():
            return self._answer_3_cases_summary(cases)
        elif "acoso escolar" in question.lower() and "sentencia" in question.lower():
            return self._answer_bullying_sentence(cases)
        elif "acoso escolar" in question.lower() and "detalle" in question.lower():
            return self._answer_bullying_detail(cases)
        elif "piar" in question.lower():
            return self._answer_piar_cases(cases)
        else:
            return self._answer_generic(question, cases)
    
    def _answer_3_sentences(self, cases):
        answer = "Aquí te explico 3 sentencias de demandas reales:\n\n"
        for i, case in enumerate(cases[:3], 1):
            answer += f"{i}. {case.get('Tipo', 'Caso legal')}\n"
            answer += f"   • Resolución: {case.get('resuelve', 'No especificada')}\n"
            answer += f"   • Fecha: {case.get('Fecha Sentencia', 'No especificada')}\n\n"
        return answer
    
    def _answer_3_cases_summary(self, cases):
        answer = "Estas fueron las 3 demandas:\n\n"
        for i, case in enumerate(cases[:3], 1):
            answer += f"{i}. {case.get('Tipo', 'Caso legal')}\n"
            answer += f"   • Resumen: {case.get('sintesis', 'No especificada')}\n"
            answer += f"   • Tema: {case.get('Tema_subtema', 'No especificado')}\n\n"
        return answer
    
    def _answer_bullying_sentence(self, cases):
        bullying_cases = [c for c in cases if "acoso" in c.get('Tipo', '').lower() or 
                         "acoso" in c.get('Tema_subtema', '').lower()]
        
        if bullying_cases:
            case = bullying_cases[0]
            answer = "Sentencia del caso de acoso escolar:\n\n"
            answer += f"Este caso trató sobre {case.get('sintesis', 'acoso escolar')}.\n\n"
            answer += f"Resultado: {case.get('resuelve', 'No se especifica la sentencia')}\n"
            answer += f"Fecha: {case.get('Fecha Sentencia', 'No especificada')}\n"
            return answer
        else:
            return "No encontré un caso específico de acoso escolar, pero puedo mostrarte casos similares."
    
    def _answer_bullying_detail(self, cases):
        bullying_cases = [c for c in cases if "acoso" in c.get('Tipo', '').lower()]
        
        if bullying_cases:
            case = bullying_cases[0]
            answer = "Detalles completos del caso de acoso escolar:\n\n"
            answer += f"Tipo de caso: {case.get('Tipo', 'Acoso escolar')}\n"
            answer += f"Documento legal: {case.get('Providencia', 'No especificado')}\n"
            answer += f"Fecha:** {case.get('Fecha Sentencia', 'No especificada')}\n"
            answer += f"Tema específico: {case.get('Tema_subtema', 'No especificado')}\n"
            answer += f"Resolución: {case.get('resuelve', 'No especificada')}\n"
            answer += f"Resumen: {case.get('sintesis', 'No especificado')}\n"
            return answer
        else:
            return "No tengo detalles específicos de un caso de acoso escolar en la base de datos actual."
    
    def _answer_piar_cases(self, cases):
        piar_cases = [c for c in cases if "piar" in str(c.get('Tipo', '')).lower() or 
                     "piar" in str(c.get('Tema_subtema', '')).lower() or
                     "piar" in str(c.get('sintesis', '')).lower()]
        
        if piar_cases:
            answer = f"**Casos sobre el PIAR (Protocolo de Inclusión y Acompañamiento):**\n\n"
            answer += f"Encontré {len(piar_cases)} caso(s):\n\n"
            
            for i, case in enumerate(piar_cases, 1):
                answer += f"{i}. {case.get('Tipo', 'Caso relacionado con PIAR')}\n"
                answer += f"   • De qué trata: {case.get('sintesis', 'No especificado')}\n"
                answer += f"   • Sentencia: {case.get('resuelve', 'No especificada')}\n"
                answer += f"   • Fecha: {case.get('Fecha Sentencia', 'No especificada')}\n\n"
            return answer
        else:
            return "No encontré casos específicos sobre el PIAR en la base de datos."
    
    def _answer_generic(self, question, cases):
        if not cases:
            return "No encontré información específica para tu pregunta. Intenta con preguntas más específicas sobre casos legales."
        
        answer = f"Encontré {len(cases)} caso(s) relevantes:\n\n"
        for i, case in enumerate(cases[:3], 1):
            answer += f"{i}. {case.get('Tipo', 'Caso legal')}\n"
            answer += f"   • {case.get('sintesis', 'No especificado')}\n"
            answer += f"   • Resultado: {case.get('resuelve', 'No especificado')}\n\n"
        return answer