# 🎾 OddsEngine — Setup del Proyecto

## Estructura

```
OddsEngine/
├── backend/          ← Python + FastAPI (puerto 8000)
│   ├── app/          ← Código fuente
│   ├── tests/        ← 38 tests automatizados
│   └── requirements.txt
│
├── frontend/         ← React + Vite (puerto 5173)
│   ├── src/
│   │   ├── components/   ← MatchCard, MatchList, CombinationPanel, etc.
│   │   ├── pages/        ← Home
│   │   ├── services/     ← apiClient.js (llamadas HTTP)
│   │   ├── hooks/        ← useMatches
│   │   └── context/      ← CombinationContext, NotificationContext
│   └── package.json
│
└── docs/             ← Documentación y evidencia de testing
```

## Requisitos

- Python 3.10+
- Node.js 18+ y npm
- Git

---

## Paso 1: Backend

```bash
cd backend
python -m venv venv

# Linux/Mac:
source venv/bin/activate
# Windows:
venv\Scripts\activate

pip install -r requirements.txt
uvicorn app.main:app --reload --port 8000
```

### Verificar backend:
- http://localhost:8000/health → `{"status": "ok"}`
- http://localhost:8000/docs → Swagger UI con todos los endpoints
- http://localhost:8000/api/matches → Lista de partidos JSON

### Correr tests:
```bash
cd backend
pytest tests/ -v
# Resultado esperado: 38 passed
```

---

## Paso 2: Frontend

**En otra terminal** (el backend debe seguir corriendo):

```bash
cd frontend
npm install
npm run dev
```

### Verificar frontend:
- http://localhost:5173 → App React con lista de partidos
- Los partidos se cargan automáticamente del backend
- Se puede crear una combinada y agregar/eliminar partidos

---

## Cómo funciona la conexión

El frontend (Vite en puerto 5173) tiene un proxy configurado en `vite.config.js`:
- Cualquier llamada a `/api/*` se redirige a `http://localhost:8000`
- Esto significa que el frontend llama a `/api/matches` y Vite lo redirige al backend
- No hay problemas de CORS durante el desarrollo

---

## Endpoints disponibles

| Método | Ruta | Descripción |
|--------|------|-------------|
| GET | `/health` | Health check |
| GET | `/api/matches` | Listar partidos (filtro: `?status=upcoming`) |
| GET | `/api/matches/{id}` | Partido específico |
| POST | `/api/combinations` | Crear combinada vacía |
| GET | `/api/combinations/{id}` | Ver combinada |
| DELETE | `/api/combinations/{id}` | Eliminar combinada |
| POST | `/api/combinations/{id}/matches` | Agregar partido |
| DELETE | `/api/combinations/{id}/matches/{match_id}` | Quitar partido |

IDs de partidos en el mock: `match_001` a `match_008`

---

## Quién trabaja en qué

| Persona | Carpeta | Qué hace |
|---------|---------|----------|
| Juan Pablo | `backend/` | Modelos, servicios, lógica |
| David | `backend/` | Endpoints, tests, errores |
| Nicolás | `frontend/` | Setup, routing, estado, integración |
| Lucas | `frontend/` | Componentes UI, gráficas, estilos |
