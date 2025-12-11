from langchain_text_splitters import RecursiveCharacterTextSplitter # Was: langchain.text_splitter
from langchain_core.documents import Document # Handles Document schema
import pandas as pd
from typing import List, Dict
import json

class LegalDocumentProcessor:
    def __init__(self):
        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=1000,
            chunk_overlap=200,
            separators=["\n\n", "\n", ". ", " ", ""]
        )
    
    def process_excel_file(self, file_path: str) -> Dict:
        """
        Process Excel file with legal cases
        Expected columns: CaseID, Title, Description, Sentence, Category, Date, etc.
        """
        try:
            # Read Excel file
            df = pd.read_excel(file_path)
            print(f"Loaded {len(df)} cases from Excel")
            
            documents = []
            
            # Convert each row to document
            for _, row in df.iterrows():
                # Create comprehensive text
                case_text = f"""
                DEMANDA: {row.get('Title', 'Sin título')}
                ID del caso: {row.get('CaseID', 'N/A')}
                Fecha: {row.get('Date', 'N/A')}
                Categoría: {row.get('Category', 'N/A')}
                
                DESCRIPCIÓN:
                {row.get('Description', 'No hay descripción disponible.')}
                
                SENTENCIA:
                {row.get('Sentence', 'No hay sentencia registrada.')}
                
                DETALLES ADICIONALES:
                {row.get('Details', 'No hay detalles adicionales.')}
                """
                
                # Create metadata
                metadata = {
                    "case_id": str(row.get('CaseID', '')),
                    "title": str(row.get('Title', '')),
                    "category": str(row.get('Category', '')),
                    "date": str(row.get('Date', '')),
                    "sentence": str(row.get('Sentence', '')),
                    "source": "excel_database"
                }
                
                # Create LangChain document
                doc = Document(
                    page_content=case_text,
                    metadata=metadata
                )
                documents.append(doc)
            
            # Split documents into chunks
            split_docs = self.text_splitter.split_documents(documents)
            print(f"Split into {len(split_docs)} document chunks")
            
            return {
                "documents": split_docs,
                "count": len(split_docs),
                "original_cases": len(df)
            }
            
        except Exception as e:
            raise Exception(f"Error processing Excel file: {str(e)}")