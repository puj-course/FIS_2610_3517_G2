# OddsEngine Backend

Motor probabilístico para análisis de apuestas de tenis.

## Requisitos

- Python 3.10+
- pip

## Instalación

```bash
cd backend
python -m venv venv
source venv/bin/activate      # Linux/Mac
# venv\Scripts\activate       # Windows
pip install -r requirements.txt
```

## Ejecución

```bash
uvicorn app.main:app --reload --port 8000
```

El servidor estará disponible en `http://localhost:8000`.

## Endpoints disponibles

| Método | Ruta | Descripción |
|--------|------|-------------|
| GET | `/health` | Health check |
| GET | `/api/matches` | Listar partidos |
| GET | `/api/matches/{id}` | Obtener partido por ID |

### Filtros en GET /api/matches

- `?status=upcoming` — partidos próximos
- `?status=live` — partidos en vivo
- `?status=finished` — partidos terminados
- `?tournament=Roland Garros` — filtrar por torneo

## Pruebas

```bash
pytest tests/ -v
```

## Ejemplos con curl

```bash
# Todos los partidos
curl http://localhost:8000/api/matches | python -m json.tool

# Solo próximos
curl "http://localhost:8000/api/matches?status=upcoming"

# Filtrar por torneo
curl "http://localhost:8000/api/matches?tournament=Roland%20Garros"

# Partido específico
curl http://localhost:8000/api/matches/match_001
```

## Documentación interactiva

FastAPI genera documentación automática:
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc
