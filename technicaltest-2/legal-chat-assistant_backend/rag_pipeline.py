from langchain_community.vectorstores import Chroma  # En lugar de langchain_chroma
from langchain_community.embeddings import OpenAIEmbeddings  # En lugar de langchain_openai
from langchain_community.embeddings import SentenceTransformerEmbeddings
from langchain.chains import RetrievalQA  # Esta debería funcionar si tienes langchain instalado
from langchain_core.prompts import PromptTemplate
from langchain_core.documents import Document
from langchain_community.llms import FakeListLLM
from langchain_openai import ChatOpenAI  # Mantén esta si usas OpenAI

import os
from typing import List, Dict
import json

class LegalRAGPipeline:
    def __init__(self, use_local_embeddings=True):
        # Configuration
        self.persist_directory = "./chroma_db"
        self.collection_name = "legal_cases"
        
        # Choose embeddings based on configuration
        if use_local_embeddings:
            self.embeddings = SentenceTransformerEmbeddings(
                model_name="sentence-transformers/all-MiniLM-L6-v2"
            )
        else:
            # Using OpenAI embeddings (requires API key)
            self.embeddings = OpenAIEmbeddings()
        
        # Initialize vector store
        self.vectorstore = None
        self.qa_chain = None
        
    def initialize_from_documents(self, documents: List[Document]):
        """
        Create vector store from processed documents
        """
        print(f"Creating vector store from {len(documents)} documents...")
        
        # Create Chroma vector store
        self.vectorstore = Chroma.from_documents(
            documents=documents,
            embedding=self.embeddings,
            persist_directory=self.persist_directory,
            collection_name=self.collection_name
        )
        
        # Persist to disk
        self.vectorstore.persist()
        
        # Initialize QA chain
        self._initialize_qa_chain()
        
        print("Vector store created and QA chain initialized")
    
    def _initialize_qa_chain(self):
        """
        Initialize the QA chain with legal-specific prompt
        """
        # Legal-specific prompt template
        prompt_template = """
        Eres un asistente legal especializado en consulta de historial de demandas.
        Tu tarea es responder preguntas sobre casos legales usando SOLO la información proporcionada.
        
        Responde en un lenguaje coloquial y sencillo, para personas sin conocimientos de derecho.
        Si no encuentras información suficiente, di que no tienes esa información.
        
        Información de contexto:
        {context}
        
        Pregunta: {question}
        
        Respuesta clara y sencilla:
        """
        
        PROMPT = PromptTemplate(
            template=prompt_template,
            input_variables=["context", "question"]
        )
        
        # Initialize LLM (configure based on available API)
        # Option 1: OpenAI GPT
        # llm = ChatOpenAI(model_name="gpt-4", temperature=0.1)
        
        # Option 2: Local LLM (using Ollama, GPT4All, etc.)
        # from langchain.llms import Ollama
        # llm = Ollama(model="llama2")
        
        # For this example, using a simple implementation
        from langchain_community.llms import FakeListLLM
        llm = FakeListLLM(responses=["I'm a placeholder LLM. In production, connect to real LLM."])
        
        # Create retriever
        retriever = self.vectorstore.as_retriever(
            search_kwargs={"k": 4}  # Retrieve top 4 relevant documents
        )
        
        # Create QA chain
        self.qa_chain = RetrievalQA.from_chain_type(
            llm=llm,
            chain_type="stuff",
            retriever=retriever,
            chain_type_kwargs={"prompt": PROMPT},
            return_source_documents=True
        )
    
    def query(self, question: str, conversation_history=None) -> Dict:
        """
        Query the RAG pipeline with a legal question
        """
        if not self.qa_chain:
            return {
                "answer": "El sistema no ha sido inicializado con documentos. Por favor, ingiere documentos primero.",
                "sources": [],
                "confidence": 0.0
            }
        
        try:
            # Format question based on conversation history
            formatted_question = self._format_question(question, conversation_history)
            
            # Get response from QA chain
            result = self.qa_chain({"query": formatted_question})
            
            # Extract source information
            sources = []
            if hasattr(result, 'source_documents'):
                for doc in result['source_documents'][:3]:  # Top 3 sources
                    sources.append({
                        "title": doc.metadata.get("title", "Sin título"),
                        "case_id": doc.metadata.get("case_id", "N/A"),
                        "category": doc.metadata.get("category", "N/A")
                    })
            
            return {
                "answer": result['result'],
                "sources": sources,
                "confidence": 0.85  # Placeholder - in production, calculate actual confidence
            }
            
        except Exception as e:
            return {
                "answer": f"Error procesando la consulta: {str(e)}",
                "sources": [],
                "confidence": 0.0
            }
    
    def _format_question(self, question: str, history=None) -> str:
        """
        Format question with context from conversation history
        """
        if not history or len(history) < 2:
            return question
        
        # Add last 2 exchanges for context
        context_parts = []
        for exchange in history[-2:]:
            role = "Usuario" if exchange.get("role") == "user" else "Asistente"
            context_parts.append(f"{role}: {exchange.get('content', '')}")
        
        context = "\n".join(context_parts)
        return f"Contexto de conversación anterior:\n{context}\n\nNueva pregunta: {question}"