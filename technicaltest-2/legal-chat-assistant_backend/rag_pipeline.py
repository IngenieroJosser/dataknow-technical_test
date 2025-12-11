import faiss
import numpy as np
from sentence_transformers import SentenceTransformer
import openai


class LegalRAGPipeline:
    def __init__(self):
        self.model = SentenceTransformer("all-MiniLM-L6-v2")

        # FAISS index
        self.dimension = 384
        self.index = faiss.IndexFlatL2(self.dimension)

        # Almacén metadata
        self.metadata_store = {}

    def add_case(self, text: str, metadata: dict):
        embedding = self.model.encode([text]).astype("float32")

        # Guardar vector
        self.index.add(embedding)

        vector_id = len(self.metadata_store)

        self.metadata_store[vector_id] = {
            "text": text,
            **metadata
        }

    def query(self, question: str, k: int = 3):
        query_embed = self.model.encode([question]).astype("float32")

        distances, indices = self.index.search(query_embed, k)

        results = []
        for idx in indices[0]:
            if idx == -1:
                continue
            results.append(self.metadata_store[idx])

        answer = self._generate_answer(question, results)

        return answer, 0.85, results

    def _generate_answer(self, question: str, results: list):
        context = ""

        for r in results:
            context += f"""
Caso ID: {r.get("caso_id")}
Descripción: {r.get("descripcion")}
Tipo: {r.get("tipo")}
Sentencia: {r.get("sentencia")}
Plataforma: {r.get("plataforma")}
Fecha: {r.get("fecha")}
---
"""

        prompt = f"""
Eres un asistente legal que explica casos reales en lenguaje sencillo.

Pregunta del usuario: {question}

Basado EXCLUSIVAMENTE en los casos siguientes (NO inventes información):

{context}

Respuesta clara y coloquial:
"""

        completion = openai.ChatCompletion.create(
            model="gpt-4o-mini",
            messages=[{"role": "user", "content": prompt}]
        )

        return completion.choices[0].message["content"]
