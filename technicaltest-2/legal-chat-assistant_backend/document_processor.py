from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.schema import Document

import pandas as pd
from typing import List, Dict, Any
import json

class LegalDocumentProcessor:
    def __init__(self, chunk_size=800, chunk_overlap=150):
        """
        Inicializar procesador de documentos legales
        
        Args:
            chunk_size: Tamaño de fragmentos de texto
            chunk_overlap: Superposición entre fragmentos
        """
        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=chunk_size,
            chunk_overlap=chunk_overlap,
            separators=["\n\n", "\n", ". ", "! ", "? ", "; ", ", ", " "],
            length_function=len,
        )
    
    def process_excel_file(self, file_path: str) -> Dict[str, Any]:
        """
        Procesar archivo Excel con casos legales
        
        Columnas esperadas:
        - CaseID: Identificador único del caso
        - Title: Título del caso
        - Description: Descripción detallada
        - Sentence: Sentencia o resolución
        - Category: Categoría (Redes Sociales, Educación, etc.)
        - Date: Fecha del caso
        - Details: Detalles adicionales (opcional)
        """
        try:
            print(f"Leyendo archivo Excel: {file_path}")
            
            # Leer archivo Excel
            df = pd.read_excel(file_path)
            print(f"Cargados {len(df)} casos desde Excel")
            
            # Mostrar estructura del archivo
            print(f"Columnas disponibles: {list(df.columns)}")
            print(f"Primeros casos:\n{df.head()}")
            
            documents = []
            
            # Convertir cada fila a documento
            for idx, row in df.iterrows():
                # Crear texto comprehensivo del caso
                case_text = f"""
                DEMANDA LEGAL
                
                TÍTULO: {row.get('Title', 'Sin título')}
                ID: {row.get('CaseID', f'CASE-{idx:03d}')}
                FECHA: {row.get('Date', 'No especificada')}
                CATEGORÍA: {row.get('Category', 'General')}
                
                DESCRIPCIÓN DEL CASO:
                {row.get('Description', 'No hay descripción disponible.')}
                
                SENTENCIA O RESOLUCIÓN:
                {row.get('Sentence', 'No hay sentencia registrada.')}
                
                DETALLES ADICIONALES:
                {row.get('Details', 'No hay detalles adicionales.')}
                """
                
                # Crear metadatos
                metadata = {
                    "case_id": str(row.get('CaseID', f'CASE-{idx:03d}')),
                    "title": str(row.get('Title', 'Sin título')),
                    "category": str(row.get('Category', 'General')),
                    "date": str(row.get('Date', '')),
                    "sentence_summary": str(row.get('Sentence', '')),
                    "source": "excel_database",
                    "row_index": idx
                }
                
                # Crear documento LangChain
                doc = Document(
                    page_content=case_text.strip(),
                    metadata=metadata
                )
                documents.append(doc)
            
            # Fragmentar documentos en chunks
            print(f"Fragmentando {len(documents)} documentos...")
            split_docs = self.text_splitter.split_documents(documents)
            print(f"Fragmentados en {len(split_docs)} chunks de texto")
            
            return {
                "documents": split_docs,
                "count": len(split_docs),
                "original_cases": len(df),
                "columns": list(df.columns)
            }
            
        except FileNotFoundError:
            raise Exception(f"Archivo no encontrado: {file_path}")
        except Exception as e:
            raise Exception(f"Error procesando archivo Excel: {str(e)}")