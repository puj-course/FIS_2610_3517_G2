# Endpoints REST — OddsEngine API v1.0.0

Base URL: `http://localhost:8000/api`

## Partidos

| Método | Ruta | Descripción |
|--------|------|-------------|
| GET | /matches | Listar partidos (filtros: status, tournament, page, limit) |
| GET | /matches/{id} | Obtener partido por ID |
| GET | /matches/{id}/stats | Estadísticas del partido |
| GET | /matches/{id}/probability | Probabilidad individual |

### GET /matches
```bash
curl http://localhost:8000/api/matches
curl http://localhost:8000/api/matches?status=upcoming
curl http://localhost:8000/api/matches?tournament=Roland%20Garros
curl http://localhost:8000/api/matches?page=1&limit=5
```
Respuesta: Array de Match objects

### GET /matches/{id}/stats
```bash
curl http://localhost:8000/api/matches/match_001/stats
```
Respuesta: { match_id, player_home_stats, player_away_stats, head_to_head, surface }

### GET /matches/{id}/probability
```bash
curl http://localhost:8000/api/matches/match_001/probability
```
Respuesta: { match_id, player_home_probability, player_away_probability, factors, confidence }

## Combinadas

| Método | Ruta | Descripción |
|--------|------|-------------|
| POST | /combinations | Crear combinada vacía |
| GET | /combinations/{id} | Obtener combinada |
| DELETE | /combinations/{id} | Eliminar combinada |
| POST | /combinations/{id}/matches | Agregar partido |
| DELETE | /combinations/{id}/matches/{mid} | Eliminar partido |
| GET | /combinations/{id}/probability | Probabilidad combinada |
| GET | /combinations/{id}/result | Resultado completo |
| POST | /combinations/{id}/complete | Completar combinada |
| GET | /combinations/{id}/export | Exportar resultado JSON |

### POST /combinations/{id}/matches
```bash
curl -X POST http://localhost:8000/api/combinations/abc123/matches \
  -H "Content-Type: application/json" \
  -d '{"match_id": "match_001"}'
```

## Historial

| Método | Ruta | Descripción |
|--------|------|-------------|
| GET | /combinations/history | Historial de combinadas |

## Health

| Método | Ruta | Descripción |
|--------|------|-------------|
| GET | /health | Health check básico |
| GET | /health/detailed | Health con estado de BD |

## Errores

Todos los errores retornan JSON:
```json
{
  "error": {
    "type": "NotFoundException",
    "message": "Partido match_999 no encontrado",
    "status_code": 404,
    "timestamp": "2026-03-21T..."
  }
}
```

| Código | Tipo | Descripción |
|--------|------|-------------|
| 404 | NotFoundException | Recurso no encontrado |
| 409 | DuplicateException | Partido ya en combinada |
| 422 | ValidationException | Datos inválidos |
| 500 | InternalError | Error interno (sin detalles) |
