# INFORME TÉCNICO - ASISTENTE LEGAL AI

## Explicación del Caso
Se desarrolló un sistema de consulta inteligente de historial de demandas legales para un consultorio jurídico, utilizando Inteligencia Artificial Generativa (Generative AI) para automatizar el proceso de asesoría inicial. El sistema permite a los abogados y clientes consultar sentencias pasadas mediante preguntas en lenguaje natural, recibiendo respuestas claras y en términos coloquiales.

### Contexto del Problema
- Los abogados debían consultar manualmente un Excel extenso con casos y sentencias
- Proceso lento y propenso a errores humanos
- Necesidad de traducir términos legales a lenguaje comprensible para clientes
- Específicamente para demandas relacionadas con redes sociales

## Supuestos del Proyecto

### Supuestos Técnicos
1. Los datos de entrada están en formato Excel con estructura consistente
2. Los usuarios finales no tienen conocimientos legales avanzados
3. El sistema operará en un entorno con acceso a internet para APIs de IA
4. La precisión del 85% es aceptable para la fase de PoC (Proof of Concept)

### Supuestos de Negocio
1. La automatización reducirá el tiempo de consulta en al menos 50%
2. Los abogados podrán enfocarse en casos más complejos
3. Los clientes recibirán respuestas más rápidas y comprensibles
4. El sistema escalará para incluir más tipos de demandas después de la PoC

## Formas para Resolver el Caso y Opción Tomada

### Alternativas Consideradas

#### Opción 1: Fine-tuning de Modelo de Lenguaje
- **Ventajas**: Alta precisión para preguntas específicas del dominio legal
- **Desventajas**: 
  - Requiere gran volumen de datos etiquetados
  - Costo computacional elevado
  - Dificultad para actualizar con nuevos casos
- **Evaluación**: Descartada por complejidad y costo para PoC

#### Opción 2: Sistema de Reglas y Búsqueda por Palabras Clave
- **Ventajas**: Simple de implementar, predecible
- **Desventajas**:
  - Poca flexibilidad para preguntas naturales
  - Requiere mantenimiento constante de reglas
  - No maneja sinónimos ni lenguaje coloquial
- **Evaluación**: Descartada por limitada usabilidad

#### Opción 3: RAG (Retrieval Augmented Generation)  **SELECCIONADA**
- **Ventajas**:
  - Combina búsqueda precisa con generación natural de lenguaje
  - Actualizable fácilmente con nuevos casos
  - Respuestas basadas en datos reales verificables
  - Maneja preguntas en lenguaje natural
  - Costo controlado al usar modelos preentrenados
- **Implementación**: FAISS + Sentence Transformers + GPT-4

### Arquitectura Final Implementada