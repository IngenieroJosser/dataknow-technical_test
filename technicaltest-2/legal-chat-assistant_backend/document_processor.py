import pandas as pd
import logging
from typing import List, Dict, Any
from rag_pipeline import LegalRAGPipeline

logger = logging.getLogger(__name__)

class DocumentProcessor:
    def __init__(self, rag_pipeline: LegalRAGPipeline):
        self.rag_pipeline = rag_pipeline
    
    def process_excel_file(self, file_path: str = "data/sentencias_pasadas.xlsx") -> int:
        """
        Procesa el archivo Excel con el formato REAL de columnas:
        - Relevancia, Providencia, Tipo, Fecha Sentencia, Tema - subtema, resuelve, sintesis
        """
        try:
            # Leer Excel
            df = pd.read_excel(file_path)
            logger.info(f" Excel cargado: {len(df)} casos encontrados")
            
            # Verificar columnas necesarias
            required_columns = ['Tipo', 'resuelve', 'sintesis']
            missing_columns = [col for col in required_columns if col not in df.columns]
            
            if missing_columns:
                logger.warning(f"Columnas faltantes: {missing_columns}")
            
            # Procesar cada caso
            cases_added = 0
            for idx, row in df.iterrows():
                try:
                    # Crear texto para embedding
                    case_text = self._create_case_text(row)
                    
                    # Crear metadatos con nombres de columnas CORRECTOS
                    metadata = {
                        "id": idx + 1,
                        "Relevancia": str(row.get('Relevancia', 'No especificado')),
                        "Providencia": str(row.get('Providencia', 'No especificado')),
                        "Tipo": str(row.get('Tipo', 'No especificado')),
                        "Fecha Sentencia": str(row.get('Fecha Sentencia', 'No especificada')),
                        "Tema_subtema": str(row.get('Tema - subtema', 'No especificado')),
                        "resuelve": str(row.get('resuelve', 'No especificada')),
                        "sintesis": str(row.get('sintesis', 'No especificada'))
                    }
                    
                    # Añadir al pipeline RAG
                    self.rag_pipeline.add_case(case_text, metadata)
                    cases_added += 1
                    
                except Exception as case_error:
                    logger.error(f"Error procesando caso {idx}: {case_error}")
                    continue
            
            logger.info(f" {cases_added} casos agregados a la base de datos vectorial")
            return cases_added
            
        except FileNotFoundError:
            logger.error(f" Archivo no encontrado: {file_path}")
            raise
        except Exception as e:
            logger.error(f" Error procesando Excel: {e}")
            raise
    
    def _create_case_text(self, row) -> str:
        """Crea texto completo del caso para embedding"""
        parts = []
        
        # Usar las columnas REALES del Excel
        if pd.notna(row.get('Tipo')):
            parts.append(f"Tipo de demanda: {row['Tipo']}")
        
        if pd.notna(row.get('Tema - subtema')):
            parts.append(f"Tema: {row['Tema - subtema']}")
        
        if pd.notna(row.get('resuelve')):
            parts.append(f"Resolución: {row['resuelve']}")
        
        if pd.notna(row.get('sintesis')):
            parts.append(f"Resumen: {row['sintesis']}")
        
        if pd.notna(row.get('Providencia')):
            parts.append(f"Documento legal: {row['Providencia']}")
        
        if pd.notna(row.get('Fecha Sentencia')):
            parts.append(f"Fecha: {row['Fecha Sentencia']}")
        
        return " | ".join(parts)