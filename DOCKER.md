# 🐳 OddsEngine — Guía Docker

Instrucciones para levantar el proyecto con Docker en **Windows, Mac y Linux**.

---

## ✅ Requisitos previos

- [Docker Desktop](https://www.docker.com/products/docker-desktop/) instalado y **corriendo**
- Git para clonar el repositorio

> En Windows: asegúrate de que Docker Desktop esté abierto (el ícono de la ballena debe aparecer en la barra de tareas).

---

## 🚀 Levantar el proyecto (modo rápido)

```bash
# 1. Clonar el repo
git clone https://github.com/puj-course/FIS_2610_3517_G2
cd FIS_2610_3517_G2

# 2. Ir a la carpeta del proyecto
cd OE_FINAL_V2

# 3. Levantar todo con Docker
docker compose up --build
```

Listo. Abre tu navegador en:

| Servicio  | URL                        |
|-----------|----------------------------|
| Frontend  | http://localhost:5173      |
| Backend   | http://localhost:8000      |
| API Docs  | http://localhost:8000/docs |

---

## 🗄️ Con base de datos PostgreSQL (opcional)

Por defecto el proyecto corre en modo `mock` (sin BD). Si quieres activar PostgreSQL:

```bash
# Edita el .env y cambia:
DATA_MODE=database

# Luego levanta incluyendo el perfil de base de datos:
docker compose --profile database up --build
```

---

## 🛑 Detener el proyecto

```bash
# Detener (mantiene los datos)
docker compose down

# Detener y borrar todo (incluyendo la base de datos)
docker compose down -v
```

---

## 🔄 Después de cambiar código

Los cambios en el código se recargan automáticamente (hot-reload).  
Si agregas una **dependencia nueva** (pip o npm), reconstruye las imágenes:

```bash
docker compose up --build
```

---

## ❓ Problemas frecuentes

### "Port is already in use"
Algún proceso ya está usando el puerto 8000 o 5173. Ciérralo o cambia el puerto en `docker-compose.yml`.

### En Windows: "Mounts denied" o errores de permisos
Abre Docker Desktop → Settings → Resources → File Sharing  
y agrega la carpeta del proyecto.

### Frontend no conecta con el backend
Verifica que ambos contenedores estén corriendo:
```bash
docker compose ps
```

### Ver logs de un servicio específico
```bash
docker compose logs backend
docker compose logs frontend
```
