# Guía de Instalación — OddsEngine

## Requisitos
- Python 3.12 (NO 3.14)
- Node.js 18+
- PostgreSQL 16 (opcional para desarrollo)
- Git

## Instalación Rápida

### Backend
```bash
cd backend
python -m venv venv
# Windows: venv\Scripts\activate
# Mac/Linux: source venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
uvicorn app.main:app --reload --port 8000
```

### Frontend
```bash
cd frontend
npm install
npm run dev
```

### Verificar
- Backend: http://localhost:8000/health
- Swagger: http://localhost:8000/docs
- Frontend: http://localhost:5173

## Con PostgreSQL
1. Instalar PostgreSQL 16
2. Crear base de datos: `createdb oddsengine`
3. Editar `.env`: `DATA_MODE=database` y `DATABASE_URL=postgresql+asyncpg://postgres:PASSWORD@localhost:5432/oddsengine`
4. Ejecutar seed: `python scripts/seed_database.py --clean`

## Troubleshooting

| Problema | Solución |
|----------|----------|
| `python not found` | Instalar Python 3.12 con "Add to PATH" |
| `pydantic-core build error` | Usar Python 3.12, NO 3.14 |
| `npm scripts disabled` | `Set-ExecutionPolicy -Scope CurrentUser RemoteSigned` |
| Frontend no carga partidos | Verificar backend en puerto 8000 |
| PostgreSQL connection refused | Verificar servicio PostgreSQL corriendo |
| `database does not exist` | `createdb oddsengine` |
| Tests fallan con datos compartidos | Verificar conftest.py con autouse |
| `asyncpg connection closed` | Verificar contraseña en .env |
