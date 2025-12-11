# Asistente Legal AI - Prueba Técnica DataKnow

##  Descripción del Proyecto
Sistema de consulta inteligente de historial de demandas legales implementando RAG (Retrieval Augmented Generation) para automatizar la asesoría legal inicial en casos relacionados con redes sociales.

##  Características Principales
- **Consulta en lenguaje natural**: Pregunta como si hablaras con un abogado
- **Respuestas en lenguaje coloquial**: Explicaciones simples sin tecnicismos
- **Búsqueda semántica**: Encuentra casos similares aunque uses palabras diferentes
- **Base de datos vectorial**: FAISS para búsqueda ultra rápida de precedentes
- **Interfaz moderna**: UI/UX intuitiva con indicadores de confianza
- **Funciona sin internet**: Modo demo con respuestas de ejemplo

##  Arquitectura del Sistema

### Frontend (Next.js 14 + TypeScript)
- **Framework**: Next.js 14 con App Router
- **Lenguaje**: TypeScript
- **Estilos**: Tailwind CSS
- **Animaciones**: Framer Motion
- **Iconos**: Lucide React

### Backend (FastAPI + Python)
- **Framework**: FastAPI
- **Base de datos vectorial**: FAISS
- **Modelo de embeddings**: Sentence Transformers (all-MiniLM-L6-v2)
- **Generación de texto**: OpenAI GPT-4o-mini
- **Procesamiento de datos**: Pandas + Openpyxl

##  Instalación Rápida

### Requisitos Previos
- Python 3.9+
- Node.js 18+
- Cuenta de OpenAI (opcional, para respuestas mejoradas)

### 1. Clonar el Repositorio
```bash
git clone https://github.com/IngenieroJosser/dataknow-technical_test.git
cd dataknow-technical_test