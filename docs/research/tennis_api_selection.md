# T1.1 – Selección de API de tenis (Issue #28)

## Objetivo
Investigar y proponer una API de tenis para consumir datos de partidos, jugadores y torneos.

## Criterios de evaluación
- Cobertura de torneos ATP/WTA
- Facilidad de uso (Compatibilidad con FastAPI y HTTPX)
- Documentación disponible
- Formato JSON
- Plan gratuito disponible

## Estado
Completado.

## Opciones de API evaluadas
- **API-Tennis (api-tennis.com):** Especializada únicamente en tenis. Es ideal para la arquitectura asíncrona ya que sus respuestas JSON son ligeras y fáciles de procesar mediante **HTTPX** dentro de los endpoints de **FastAPI**.
- **RapidAPI (Tennis APIs):** Ofrece variedad, pero la latencia adicional de la plataforma intermedia puede afectar el rendimiento del servidor utilizado.
- **Otras opciones (Sportmonks/Generalistas):** Descartadas por falta de especialización técnica en tenis o planes gratuitos no ajustados a las necesidades del proyecto.

## Tabla comparativa

| Criterio | API-Tennis | RapidAPI (Otros) | Alternativas |
| :--- | :--- | :--- | :--- |
| **ATP/WTA** | Sí (Especializado) | Varía | Limitada |
| **Integración Async** | Excelente (JSON limpio) | Media | Media |
| **Documentación** | Completa para Python | Variable | Básica |
| **Free Tier** | 1,000 req/mes | Varía | No funcional |

## Decisión final justificada
Se selecciona **API-Tennis** como la API principal. La especialización en el deporte asegura datos más precisos para nuestro motor de predicción. Su estructura se acopla más para consumirse de forma no bloqueante con **HTTPX**, aprovechando al máximo la naturaleza asíncrona de **FastAPI** y la velocidad de ejecución sobre **Uvicorn**. 

## Plan de fallback
"si la API falla o no tiene free tier, usamos mock provider"

Se implementará un módulo `mock_data_provider.py`. Este componente simulará las funciones de red de **HTTPX**, devolviendo datos locales cuando el servidor detecte fallos en la API externa o se alcance el límite de 1,000 peticiones, permitiendo que el dashboard de FastAPI siga funcionando sin errores.

## Próximo paso
Crear el cliente asíncrono en FastAPI usando **HTTPX** para mapear los modelos de datos de los jugadores de API-Tennis.
