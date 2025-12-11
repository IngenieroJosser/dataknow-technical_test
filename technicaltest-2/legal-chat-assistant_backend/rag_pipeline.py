import os
import sys
from typing import List, Dict, Any

# Configurar importaciones seguras
try:
    from langchain.vectorstores import Chroma
    from langchain.embeddings import HuggingFaceEmbeddings
    from langchain.chains import RetrievalQA
    from langchain.prompts import PromptTemplate
    from langchain.schema import Document
    from langchain.llms import FakeListLLM
    from langchain.chat_models import ChatOpenAI
    
    print("Importaciones LangChain estándar exitosas")
    IMPORT_MODE = "standard"
    
except ImportError:
    try:
        from langchain_community.vectorstores import Chroma
        from langchain_community.embeddings import HuggingFaceEmbeddings
        from langchain.chains import RetrievalQA
        from langchain.prompts import PromptTemplate
        from langchain_core.documents import Document
        from langchain_community.llms import FakeListLLM
        from langchain_openai import ChatOpenAI
        
        print("Importaciones LangChain comunidad exitosas")
        IMPORT_MODE = "community"
        
    except ImportError as e:
        print(f"Error crítico de importación: {e}")
        print("Ejecuta: pip install langchain==0.1.17 langchain-community==0.0.28")
        sys.exit(1)

class LegalRAGPipeline:
    def __init__(self, use_local_embeddings=True):
        # Configuración
        self.persist_directory = "./chroma_db"
        self.collection_name = "legal_cases"
        self.use_local_embeddings = use_local_embeddings
        
        # Elegir embeddings basados en configuración
        if use_local_embeddings:
            print("Usando embeddings locales (Sentence Transformers)")
            self.embeddings = HuggingFaceEmbeddings(
                model_name="sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2",
                model_kwargs={'device': 'cpu'},
                encode_kwargs={'normalize_embeddings': True}
            )
        else:
            # Usar embeddings de OpenAI (requiere API key)
            print("Usando embeddings de OpenAI")
            from langchain.embeddings import OpenAIEmbeddings
            self.embeddings = OpenAIEmbeddings()
        
        # Inicializar almacén vectorial y cadena QA
        self.vectorstore = None
        self.qa_chain = None
        self.retriever = None
        
    def initialize_from_documents(self, documents: List[Document]):
        """
        Crear almacén vectorial desde documentos procesados
        """
        print(f"Creando almacén vectorial desde {len(documents)} documentos...")
        
        # Crear almacén vectorial Chroma
        self.vectorstore = Chroma.from_documents(
            documents=documents,
            embedding=self.embeddings,
            persist_directory=self.persist_directory,
            collection_name=self.collection_name
        )
        
        # Persistir en disco
        self.vectorstore.persist()
        print(f"Almacén vectorial guardado en: {self.persist_directory}")
        
        # Crear recuperador
        self.retriever = self.vectorstore.as_retriever(
            search_kwargs={
                "k": 5,  # Recuperar top 5 documentos relevantes
                "score_threshold": 0.3  # Umbral de similitud mínimo
            }
        )
        
        # Inicializar cadena QA
        self._initialize_qa_chain()
        
        print("Almacén vectorial creado y cadena QA inicializada")
        return True
    
    def _initialize_qa_chain(self):
        """
        Inicializar la cadena QA con prompt específico legal
        """
        # Plantilla de prompt específica para asesoría legal
        prompt_template = """Eres un asistente legal especializado en consulta de historial de demandas.
        
        CONTEXTO (casos legales relevantes):
        {context}
        
        PREGUNTA DEL USUARIO:
        {question}
        
        INSTRUCCIONES IMPORTANTES:
        1. Responde SOLO con la información proporcionada en el contexto
        2. Usa lenguaje coloquial y sencillo (para personas sin conocimientos de derecho)
        3. Sé claro, directo y útil
        4. Si no hay información suficiente, di: "No tengo información sobre este caso en la base de datos"
        5. Si hay varios casos relevantes, menciona los principales
        
        RESPUESTA (en español, lenguaje natural y amigable):
        """
        
        PROMPT = PromptTemplate(
            template=prompt_template,
            input_variables=["context", "question"]
        )
        
        # Inicializar LLM (modo prueba)
        print("Inicializando LLM (modo prueba con FakeListLLM)")
        
        # Respuestas de prueba para demostración
        demo_responses = [
            "Basándome en los casos de la base de datos, aquí está la información relevante:",
            "Según los registros legales que tengo disponibles, puedo indicarte que:",
            "En los casos almacenados en el sistema, se encontró la siguiente información:",
            "No tengo información específica sobre este caso en la base de datos actual."
        ]
        
        llm = FakeListLLM(
            responses=demo_responses,
            verbose=True
        )
        
        """
        # PARA PRODUCCIÓN (descomentar y configurar API key):
        # from langchain_openai import ChatOpenAI
        # llm = ChatOpenAI(
        #     model="gpt-4",
        #     temperature=0.1,
        #     openai_api_key=os.getenv("OPENAI_API_KEY")
        # )
        """
        
        # Crear cadena QA de recuperación
        self.qa_chain = RetrievalQA.from_chain_type(
            llm=llm,
            chain_type="stuff",
            retriever=self.retriever,
            chain_type_kwargs={
                "prompt": PROMPT,
                "document_variable_name": "context"
            },
            return_source_documents=True,
            verbose=True
        )
        
        print("Cadena QA configurada correctamente")
    
    def query(self, question: str, conversation_history=None) -> Dict[str, Any]:
        """
        Consultar el pipeline RAG con una pregunta legal
        
        Args:
            question: Pregunta en lenguaje natural
            conversation_history: Historial de conversación (opcional)
            
        Returns:
            Dict con respuesta, fuentes y confianza
        """
        if not self.qa_chain or not self.vectorstore:
            return {
                "answer": "El sistema no ha sido inicializado. Por favor, ejecuta primero la ingestión de documentos.",
                "sources": [],
                "confidence": 0.0,
                "status": "not_initialized"
            }
        
        try:
            print(f"Procesando pregunta: '{question}'")
            
            # Formatear pregunta con historial si existe
            formatted_question = self._format_question(question, conversation_history)
            
            # Buscar documentos similares primero
            similar_docs = self.retriever.get_relevant_documents(formatted_question)
            print(f"Documentos similares encontrados: {len(similar_docs)}")
            
            # Obtener respuesta de la cadena QA
            result = self.qa_chain({"query": formatted_question})
            
            # Extraer información de fuentes
            sources = []
            if 'source_documents' in result:
                for doc in result['source_documents'][:3]:  # Top 3 fuentes
                    sources.append({
                        "case_id": doc.metadata.get("case_id", "N/A"),
                        "title": doc.metadata.get("title", "Sin título"),
                        "category": doc.metadata.get("category", "General"),
                        "date": doc.metadata.get("date", ""),
                        "snippet": doc.page_content[:200] + "..." if len(doc.page_content) > 200 else doc.page_content
                    })
            
            # Calcular confianza aproximada basada en número de fuentes
            confidence = min(0.3 + (len(sources) * 0.2), 0.9) if sources else 0.1
            
            return {
                "answer": result['result'],
                "sources": sources,
                "confidence": confidence,
                "documents_found": len(similar_docs),
                "status": "success"
            }
            
        except Exception as e:
            print(f"Error en query: {str(e)}")
            return {
                "answer": f"Lo siento, hubo un error procesando tu consulta: {str(e)}",
                "sources": [],
                "confidence": 0.0,
                "status": "error",
                "error": str(e)
            }
    
    def _format_question(self, question: str, history=None) -> str:
        """
        Formatear pregunta con contexto del historial de conversación
        """
        if not history or len(history) < 2:
            return question
        
        # Añadir últimos 2 intercambios para contexto
        context_parts = ["Conversación anterior:"]
        for exchange in history[-2:]:
            role = "Usuario" if exchange.get("role") == "user" else "Asistente"
            context_parts.append(f"{role}: {exchange.get('content', '')}")
        
        context = "\n".join(context_parts)
        return f"{context}\n\nNueva pregunta: {question}"
    
    def get_vectorstore_info(self):
        """Obtener información sobre el almacén vectorial"""
        if not self.vectorstore:
            return {"status": "not_initialized"}
        
        try:
            # Obtener conteo de documentos
            collection = self.vectorstore._collection
            count = collection.count() if hasattr(collection, 'count') else "N/A"
            
            return {
                "status": "initialized",
                "document_count": count,
                "embedding_model": "SentenceTransformer (multilingual)" if self.use_local_embeddings else "OpenAI",
                "persist_directory": self.persist_directory
            }
        except:
            return {"status": "initialized", "details": "available"}