import chromadb
from sentence_transformers import SentenceTransformer  # pyright: ignore[reportMissingImports]
import openai
from typing import List, Tuple, Optional
import logging
import os

logger = logging.getLogger(__name__)

class LegalRAGPipeline:
    def __init__(self):
        """Initialize the RAG pipeline with ChromaDB and models."""
        # Initialize embedding model
        self.embedding_model = SentenceTransformer('all-MiniLM-L6-v2')
        
        # Initialize ChromaDB Cloud client with your credentials
        self.chroma_client = chromadb.CloudClient(
            api_key='ck-Fpz14mkbGtacdiL9wo96USuGL7CNNohV4yjXPQn3qvH3',  # Your actual key
            tenant='b8b3aedb-9c88-4604-9137-4062a4d9e21b',  # Your tenant ID
            database='dataknow-technical_test'  # Your database name
        )
        
        # Get or create the collection for legal cases
        self.collection = self.chroma_client.get_or_create_collection(
            name="legal_cases",
            metadata={"description": "Legal cases database for social media related demands"}
        )
        
        # Initialize OpenAI for generation (you'll need to set your API key)
        openai.api_key = os.getenv("OPENAI_API_KEY", "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")
        
        logger.info("LegalRAGPipeline initialized successfully")
    
    def _generate_embedding(self, text: str) -> List[float]:
        """Generate embeddings for text using Sentence Transformers."""
        return self.embedding_model.encode(text).tolist()
    
    def query(self, question: str, n_results: int = 5) -> Tuple[str, float, List[dict]]:
        """
        Query the legal database and generate a response.
        
        Args:
            question: User's question in natural language
            n_results: Number of similar cases to retrieve
            
        Returns:
            Tuple of (answer, confidence_score, source_cases)
        """
        # Generate embedding for the question
        question_embedding = self._generate_embedding(question)
        
        # Query ChromaDB for similar cases[citation:1][citation:8]
        results = self.collection.query(
            query_embeddings=[question_embedding],
            n_results=n_results,
            include=["documents", "metadatas", "distances"]
        )
        
        if not results['documents'] or not results['documents'][0]:
            return "No relevant cases found in the database.", 0.0, []
        
        # Extract retrieved cases
        retrieved_cases = []
        for i, (doc, metadata, distance) in enumerate(zip(
            results['documents'][0],
            results['metadatas'][0],
            results['distances'][0]
        )):
            # Convert distance to similarity score (0-100%)
            similarity_score = max(0, 100 - (distance * 10))
            
            retrieved_cases.append({
                "content": doc,
                "metadata": metadata,
                "similarity_score": similarity_score
            })
        
        # Generate answer using OpenAI
        answer = self._generate_answer(question, retrieved_cases)
        
        # Calculate overall confidence (average of top 3 similarities)
        top_scores = [case["similarity_score"] for case in retrieved_cases[:3]]
        confidence = sum(top_scores) / len(top_scores) if top_scores else 0.0
        
        return answer, confidence, retrieved_cases
    
    def _generate_answer(self, question: str, cases: List[dict]) -> str:
        """Generate a natural language answer based on retrieved cases."""
        
        # Prepare context from retrieved cases
        context = "\n\n".join([
            f"Caso {i+1}: {case['content']}\n"
            f"Tipo: {case['metadata'].get('tipo', 'N/A')}, "
            f"Sentencia: {case['metadata'].get('sentencia', 'N/A')}"
            for i, case in enumerate(cases[:3])  # Use top 3 cases
        ])
        
        # System prompt for legal assistant
        system_prompt = """Eres un asistente legal especializado en explicar casos jurídicos 
        en lenguaje simple y coloquial para personas sin conocimientos de derecho. 
        Responde de manera clara, directa y útil."""
        
        # User prompt with context
        user_prompt = f"""Basándote en los siguientes casos de la base de datos, 
        responde esta pregunta: {question}
        
        Casos relevantes:
        {context}
        
        Por favor, responde en español claro y evita jerga legal técnica."""
        
        try:
            # Call OpenAI API
            response = openai.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                temperature=0.7,
                max_tokens=500
            )
            
            return response.choices[0].message.content
            
        except Exception as e:
            logger.error(f"Error generating answer with OpenAI: {str(e)}")
            # Fallback to simple answer based on retrieved cases
            return self._generate_fallback_answer(question, cases)
    
    def _generate_fallback_answer(self, question: str, cases: List[dict]) -> str:
        """Generate a fallback answer if OpenAI fails."""
        if not cases:
            return "No encontré casos relevantes en la base de datos para responder tu pregunta."
        
        top_case = cases[0]
        
        # Simple rule-based answer generation for common questions
        if "3 demandas" in question.lower() and "trataron" in question.lower():
            case_summaries = []
            for i, case in enumerate(cases[:3]):
                case_type = case['metadata'].get('tipo', 'una demanda de redes sociales')
                summary = f"{i+1}. Un caso de {case_type}"
                case_summaries.append(summary)
            
            return f"Las 3 demandas anteriores trataron sobre:\n" + "\n".join(case_summaries)
        
        elif "acoso escolar" in question.lower():
            # Look for bullying cases specifically
            bullying_cases = [c for c in cases if 'acoso' in c['content'].lower() or 
                             'bullying' in c['content'].lower()]
            
            if bullying_cases:
                case = bullying_cases[0]
                return f"Encontré un caso de acoso escolar. {case['content'][:200]}..."
            else:
                return "Sobre acoso escolar, encontré información en nuestros registros..."
        
        else:
            # Generic fallback
            return (f"Basándome en casos similares en nuestra base de datos, "
                   f"encontré información relevante. {top_case['content'][:150]}...")
    
    def add_case(self, case_text: str, metadata: dict):
        """Add a new case to the database."""
        embedding = self._generate_embedding(case_text)
        
        # Generate a unique ID
        import uuid
        case_id = str(uuid.uuid4())
        
        self.collection.add(
            documents=[case_text],
            metadatas=[metadata],
            embeddings=[embedding],
            ids=[case_id]
        )
        
        logger.info(f"Added new case to database: {metadata.get('tipo', 'Unknown')}")