import pandas as pd
import logging
from typing import List, Dict, Any
from rag_pipeline import LegalRAGPipeline

logger = logging.getLogger(__name__)

class DocumentProcessor:
    def __init__(self, rag_pipeline: LegalRAGPipeline):
        self.rag_pipeline = rag_pipeline
    
    def process_excel_file(self, file_path: str):
        """
        Process an Excel file containing legal cases and add them to the vector database.
        
        Expected Excel columns:
        - caso_id: Unique case identifier
        - descripcion: Case description
        - tipo: Type of case (e.g., 'difamacion', 'acoso_escolar')
        - sentencia: Final sentence/outcome
        - plataforma: Social media platform involved
        - fecha: Date of sentence
        """
        try:
            # Read Excel file
            df = pd.read_excel(file_path)
            logger.info(f"Loaded Excel file with {len(df)} cases")
            
            # Process each case
            cases_added = 0
            for _, row in df.iterrows():
                # Create case text for embedding
                case_text = self._create_case_text(row)
                
                # Create metadata
                metadata = {
                    "caso_id": str(row.get('caso_id', '')),
                    "tipo": str(row.get('tipo', '')),
                    "sentencia": str(row.get('sentencia', '')),
                    "plataforma": str(row.get('plataforma', '')),
                    "fecha": str(row.get('fecha', '')),
                    "descripcion": str(row.get('descripcion', ''))[:100]  # Truncate if too long
                }
                
                # Add to vector database
                self.rag_pipeline.add_case(case_text, metadata)
                cases_added += 1
            
            logger.info(f"Successfully added {cases_added} cases to the database")
            return cases_added
            
        except Exception as e:
            logger.error(f"Error processing Excel file: {str(e)}")
            raise
    
    def _create_case_text(self, row) -> str:
        """Create a comprehensive text representation of a case for embedding."""
        parts = []
        
        if pd.notna(row.get('descripcion')):
            parts.append(f"Descripción: {row['descripcion']}")
        
        if pd.notna(row.get('tipo')):
            parts.append(f"Tipo de demanda: {row['tipo']}")
        
        if pd.notna(row.get('sentencia')):
            parts.append(f"Sentencia: {row['sentencia']}")
        
        if pd.notna(row.get('plataforma')):
            parts.append(f"Plataforma: {row['plataforma']}")
        
        return " | ".join(parts)