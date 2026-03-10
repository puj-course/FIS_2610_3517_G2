# 🧪 Evidencia de Pruebas Manuales — HU-01

## Pruebas realizadas con curl / Postman / Thunder Client

### Test 1: Health Check
```
GET http://localhost:8000/health

Respuesta esperada (200 OK):
{
    "status": "ok",
    "service": "OddsEngine",
    "version": "0.2.0"
}
```
**Resultado:** ✅ Exitoso

---

### Test 2: Listar todos los partidos
```
GET http://localhost:8000/api/matches

Respuesta esperada (200 OK):
- Array JSON con 8 partidos
- Cada partido tiene: id, player_home, player_away, tournament, date, status
- Partidos ordenados por fecha
```
**Resultado:** ✅ Exitoso — 8 partidos retornados en orden cronológico

---

### Test 3: Filtrar por estado "upcoming"
```
GET http://localhost:8000/api/matches?status=upcoming

Respuesta esperada (200 OK):
- Solo partidos con status "upcoming"
- Partidos de Roland Garros, Wimbledon y US Open
```
**Resultado:** ✅ Exitoso — Solo partidos próximos

---

### Test 4: Filtrar por torneo
```
GET http://localhost:8000/api/matches?tournament=Roland%20Garros

Respuesta esperada (200 OK):
- Solo partidos del torneo Roland Garros
```
**Resultado:** ✅ Exitoso — 3 partidos de Roland Garros

---

### Test 5: Obtener partido por ID
```
GET http://localhost:8000/api/matches/match_001

Respuesta esperada (200 OK):
- Partido Alcaraz vs Sinner en Roland Garros
```
**Resultado:** ✅ Exitoso

---

### Test 6: Partido no encontrado (Error 404)
```
GET http://localhost:8000/api/matches/match_999

Respuesta esperada (404):
{
    "error": {
        "type": "NotFoundException",
        "message": "Partido 'match_999' no encontrado",
        "status_code": 404,
        "timestamp": "2026-03-02T..."
    }
}
```
**Resultado:** ✅ Exitoso — Error estructurado con tipo y timestamp

---

### Test 7: Filtro con valor inválido (Error 422)
```
GET http://localhost:8000/api/matches?status=invalido

Respuesta esperada (422):
{
    "error": {
        "type": "ValidationError",
        "message": "Los datos enviados no son válidos.",
        "status_code": 422,
        ...
    }
}
```
**Resultado:** ✅ Exitoso — Error de validación manejado

---

### Test 8: Documentación Swagger
```
GET http://localhost:8000/docs

Resultado: Swagger UI carga correctamente con todos los endpoints documentados
```
**Resultado:** ✅ Exitoso

---

## Resumen

| # | Test | Status | Código |
|---|------|--------|--------|
| 1 | Health check | ✅ | 200 |
| 2 | Listar partidos | ✅ | 200 |
| 3 | Filtro por status | ✅ | 200 |
| 4 | Filtro por torneo | ✅ | 200 |
| 5 | Partido por ID | ✅ | 200 |
| 6 | Partido no encontrado | ✅ | 404 |
| 7 | Status inválido | ✅ | 422 |
| 8 | Swagger UI | ✅ | 200 |

**Total: 8/8 pruebas exitosas**

## Notas
- Servidor corriendo con: `uvicorn app.main:app --reload --port 8000`
- Pruebas automatizadas: `pytest tests/ -v` (11 tests pasando)
- Pruebas de error handling: `pytest tests/test_error_handling.py -v` (7 tests pasando)
