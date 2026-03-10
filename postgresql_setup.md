# 🐘 Configuración de PostgreSQL para OddsEngine

## Opción A: Instalación Local

### Windows
1. Descargar de https://www.postgresql.org/download/windows/
2. Ejecutar el instalador
3. Durante la instalación:
   - Recordar la contraseña del usuario `postgres`
   - Puerto por defecto: 5432
   - Dejar Stack Builder sin marcar
4. Abrir **pgAdmin** (se instala junto con PostgreSQL)
5. Crear la base de datos:
   - Click derecho en "Databases" → Create → Database
   - Name: `oddsengine`
   - Click "Save"

### Mac
```bash
brew install postgresql@16
brew services start postgresql@16
createdb oddsengine
```

### Linux (Ubuntu/Debian)
```bash
sudo apt install postgresql postgresql-contrib
sudo systemctl start postgresql
sudo -u postgres createdb oddsengine
```

## Opción B: Servicio Cloud Gratuito (Supabase)

1. Ir a https://supabase.com → crear cuenta gratis
2. Crear nuevo proyecto "OddsEngine"
3. Ir a Settings → Database → Connection string
4. Copiar la URI de conexión (formato: `postgresql://postgres:[password]@[host]:5432/postgres`)
5. Usar esa URI en el archivo `.env`

## Configurar el proyecto

1. Copiar `.env.example` a `.env`:
```bash
cd backend
cp .env.example .env
```

2. Editar `.env` con tu configuración:
```
DATA_MODE=database
DATABASE_URL=postgresql+asyncpg://postgres:TU_PASSWORD@localhost:5432/oddsengine
DATABASE_SYNC_URL=postgresql://postgres:TU_PASSWORD@localhost:5432/oddsengine
```

3. Instalar dependencias:
```bash
pip install -r requirements.txt
```

4. Ejecutar seed (crear tablas e insertar datos):
```bash
python scripts/seed_database.py --clean
```

5. Verificar:
```bash
uvicorn app.main:app --reload --port 8000
# Ir a http://localhost:8000/health
# Debe mostrar: {"data_mode": "database", ...}
```

## Estructura de Tablas

### matches
| Columna | Tipo | Descripción |
|---------|------|-------------|
| id | VARCHAR(50) PK | ID del partido |
| player_home_id | VARCHAR(50) | ID jugador local |
| player_home_name | VARCHAR(100) | Nombre jugador local |
| player_home_country | VARCHAR(10) | País |
| player_away_id | VARCHAR(50) | ID jugador visitante |
| player_away_name | VARCHAR(100) | Nombre jugador visitante |
| tournament_name | VARCHAR(100) | Nombre del torneo |
| tournament_surface | VARCHAR(20) | Superficie (hard/clay/grass) |
| date | TIMESTAMP | Fecha y hora del partido |
| status | VARCHAR(20) | Estado (upcoming/live/finished) |
| score | VARCHAR(50) | Score (null si no ha terminado) |

### combinations
| Columna | Tipo | Descripción |
|---------|------|-------------|
| id | VARCHAR(50) PK | ID de la combinada |
| created_at | TIMESTAMP | Fecha de creación |
| updated_at | TIMESTAMP | Última modificación |

### selections
| Columna | Tipo | Descripción |
|---------|------|-------------|
| id | VARCHAR(50) PK | ID de la selección |
| combination_id | VARCHAR(50) FK | Referencia a combinations |
| match_id | VARCHAR(50) | ID del partido seleccionado |
| player_home_name | VARCHAR(100) | Snapshot: jugador local |
| player_away_name | VARCHAR(100) | Snapshot: jugador visitante |
| tournament_name | VARCHAR(100) | Snapshot: torneo |
| match_date | TIMESTAMP | Snapshot: fecha |
| added_at | TIMESTAMP | Fecha de selección |

### player_stats
| Columna | Tipo | Descripción |
|---------|------|-------------|
| id | SERIAL PK | ID auto |
| player_id | VARCHAR(50) UNIQUE | ID del jugador |
| player_name | VARCHAR(100) | Nombre |
| overall_win_rate | FLOAT | Win rate general (0-100) |
| clay_win_rate | FLOAT | Win rate en clay |
| hard_win_rate | FLOAT | Win rate en hard |
| grass_win_rate | FLOAT | Win rate en grass |
| recent_form | TEXT | JSON: ["W","L","W",...] |
| total_matches | INTEGER | Total de partidos |
| titles | INTEGER | Títulos ganados |

### head_to_head
| Columna | Tipo | Descripción |
|---------|------|-------------|
| id | SERIAL PK | ID auto |
| player1_id | VARCHAR(50) | Jugador 1 |
| player2_id | VARCHAR(50) | Jugador 2 |
| player1_wins | INTEGER | Victorias jugador 1 |
| player2_wins | INTEGER | Victorias jugador 2 |
| total_matches | INTEGER | Total enfrentamientos |
| last_matches | TEXT | JSON: últimos encuentros |

## Troubleshooting

### "connection refused" al conectar
→ PostgreSQL no está corriendo. Iniciar el servicio:
- Windows: Buscar "Services" → PostgreSQL → Start
- Mac: `brew services start postgresql`
- Linux: `sudo systemctl start postgresql`

### "database does not exist"
→ Crear la base de datos: `createdb oddsengine`
→ O desde pgAdmin: click derecho en Databases → Create → "oddsengine"

### "password authentication failed"
→ Verificar la contraseña en `.env`
→ Si instalaste PostgreSQL sin contraseña, usar: `postgresql+asyncpg://postgres@localhost:5432/oddsengine`

### "module asyncpg not found"
→ Instalar dependencias: `pip install -r requirements.txt`

### Los datos no aparecen después del seed
→ Verificar que `DATA_MODE=database` en `.env`
→ Ejecutar: `python scripts/seed_database.py --clean`
