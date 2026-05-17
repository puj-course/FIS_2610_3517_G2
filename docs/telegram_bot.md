# Telegram Bot — OddsEngine

Bot de Telegram para consultar partidos de tenis y estado del servicio OddsEngine.

## Comandos disponibles

| Comando | Descripcion |
|---------|-------------|
| `/start` | Mensaje de bienvenida y lista de comandos |
| `/help` | Muestra ayuda con todos los comandos |
| `/health` | Estado del servicio (version, modo de datos) |
| `/matches` | Lista los partidos de tenis disponibles |
| `/matches <status>` | Filtra partidos por estado: `upcoming`, `live`, `finished` |
| `/match <id>` | Detalle completo de un partido (ej: `/match match_001`) |

## Crear el bot en Telegram

1. Abrir Telegram y buscar `@BotFather`
2. Enviar `/newbot`
3. Seguir las instrucciones para darle nombre al bot
4. BotFather devuelve un token como: `123456:ABC-DEF1234ghIkl-zyx57W2v1u123ew11`
5. Guardar el token de forma segura

## Ejecucion local

1. Agregar el token en `backend/.env`:
   ```
   TELEGRAM_BOT_TOKEN=tu-token-aqui
   ```

2. Instalar dependencias (si no se ha hecho):
   ```bash
   cd backend
   pip install -r requirements.txt
   ```

3. Iniciar el servidor:
   ```bash
   cd backend
   uvicorn app.main:app --reload
   ```

4. En los logs debe aparecer: `Telegram Bot iniciado`

5. Abrir Telegram, buscar el bot y enviar `/start`

**Sin token**: Si `TELEGRAM_BOT_TOKEN` esta vacio o no existe, el bot no inicia y FastAPI funciona normalmente.

## Ejecucion con Docker

1. Agregar el token en el archivo `.env` de la raiz del proyecto:
   ```
   TELEGRAM_BOT_TOKEN=tu-token-aqui
   ```

2. Construir e iniciar:
   ```bash
   docker-compose up --build
   ```

3. El bot arranca dentro del contenedor `backend` usando polling (conexiones salientes HTTPS). No requiere puertos adicionales.

## Notas tecnicas

- El bot usa **polling** (no webhooks), por lo que no necesita IP publica ni configuracion de red especial.
- El bot se integra en el ciclo de vida (`lifespan`) de FastAPI: arranca con el servidor y se detiene cuando se apaga.
- Si el bot falla al iniciar (token invalido, sin internet), FastAPI sigue funcionando normalmente. El error se registra en los logs.
- Dependencia: `python-telegram-bot==21.6` (async-native, v20+ API).

## Tests

Los tests no requieren token real de Telegram:

```bash
cd backend
pytest tests/test_telegram_formatters.py tests/test_telegram_handlers.py -v
```
