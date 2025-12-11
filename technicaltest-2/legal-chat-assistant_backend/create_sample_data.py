import pandas as pd
import os
from datetime import datetime

def create_sample_excel(file_path: str = "data/sentencias_pasadas.xlsx"):
    """Create a sample Excel file with legal cases if it doesn't exist."""
    
    # Create data directory if it doesn't exist
    os.makedirs(os.path.dirname(file_path), exist_ok=True)
    
    # Sample cases data
    cases_data = [
        {
            "caso_id": "2023-045",
            "descripcion": "Demanda por difamación en Facebook donde una persona publicó información falsa sobre un comerciante local, afectando su reputación y negocios.",
            "tipo": "difamacion",
            "sentencia": "Indemnización de $15,000 USD y retractación pública obligatoria en la misma red social.",
            "plataforma": "Facebook",
            "fecha": "2023-06-15",
            "categoria": "Redes Sociales"
        },
        {
            "caso_id": "2023-012",
            "descripcion": "Caso de acoso escolar a través de Instagram, con mensajes amenazantes y creación de perfiles falsos para hostigar a una estudiante.",
            "tipo": "acoso_escolar",
            "sentencia": "6 meses de servicios comunitarios, terapia psicológica obligatoria y prohibición de contacto digital por 2 años.",
            "plataforma": "Instagram",
            "fecha": "2023-03-22",
            "categoria": "Educación"
        },
        {
            "caso_id": "2023-078",
            "descripcion": "Uso no autorizado de fotografías protegidas por derechos de autor en campañas publicitarias de Facebook.",
            "tipo": "derechos_autor",
            "sentencia": "Multa de $8,000 USD y retiro inmediato de todo el contenido infractor.",
            "plataforma": "Facebook",
            "fecha": "2023-08-30",
            "categoria": "Propiedad Intelectual"
        },
        {
            "caso_id": "2022-112",
            "descripcion": "Caso relacionado con la falta de aplicación del Protocolo de Intervención en Acoso Escolar (PIAR) en una institución educativa.",
            "tipo": "PIAR",
            "sentencia": "Multa administrativa a la institución y capacitación obligatoria del personal en protocolos de acoso.",
            "plataforma": "Varias",
            "fecha": "2022-11-10",
            "categoria": "Educación"
        },
        {
            "caso_id": "2023-033",
            "descripcion": "Acoso escolar mediante la creación de un grupo de WhatsApp para ridiculizar a un compañero de clase.",
            "tipo": "acoso_escolar",
            "sentencia": "Servicios comunitarios de 3 meses y suspensión escolar por 15 días.",
            "plataforma": "WhatsApp",
            "fecha": "2023-02-18",
            "categoria": "Educación"
        },
        {
            "caso_id": "2023-091",
            "descripcion": "Implementación incompleta del PIAR después de un incidente de acoso documentado en redes sociales.",
            "tipo": "PIAR",
            "sentencia": "Designación de un supervisor externo por 6 meses y auditorías trimestrales del protocolo.",
            "plataforma": "Twitter",
            "fecha": "2023-09-05",
            "categoria": "Educación"
        }
    ]
    
    # Create DataFrame
    df = pd.DataFrame(cases_data)
    
    # Save to Excel
    df.to_excel(file_path, index=False)
    print(f"Sample Excel file created at: {file_path}")
    print(f"Total cases created: {len(df)}")
    
    return df

if __name__ == "__main__":
    create_sample_excel()