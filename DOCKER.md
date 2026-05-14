# 🐳 OddsEngine — Guía Docker

Instrucciones para levantar el proyecto con Docker en **Windows, Mac y Linux**.

---

## ✅ Requisitos previos

- [Docker Desktop](https://www.docker.com/products/docker-desktop/) instalado y **corriendo**
- Git para clonar el repositorio

> En Windows: asegúrate de que Docker Desktop esté abierto (el ícono de la ballena debe aparecer en la barra de tareas).

---

## 🚀 Levantar el proyecto

```bash
# 1. Clonar el repo
git clone https://github.com/puj-course/FIS_2610_3517_G2

cd FIS_2610_3517_G2

# 2. Levantar todo con Docker
docker compose up --build
```

si acaso no funciona (que no es comun que pase) hacerlo en la rama de feature/docker-deploy

```bash
git checkout feature/docker-deploy
```

Listo. Abre tu navegador en:

| Servicio  | URL                        |
|-----------|----------------------------|
| Frontend  | http://localhost     |
| Backend  | http://localhost:8000/health|
| Docks   | http://localhost:8000/docs      |
| API Docs  | http://localhost:8000 |

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

Se actualizo el workflow de CI para que, en cada push a main, develop o feature/docker-deploy, se ejecuten los siguientes pasos: 
1.  Instalacion de dependencias Python (incluyendo pytest-cov). 
2. Ejecucion de tests con cobertura: genera coverage.xml. 
3. Build del frontend con Node.js 18 para verificar que compila correctamente. 
4.  Analisis de SonarCloud usando el reporte de cobertura generado.

## Mejora en el workflow (docker-deploy.yml)
Se mejoro el workflow de Docker para que, al pasar el build, construya y suba automaticamente las imagenes a Docker Hub usando los secrets
DOCKERHUB_USERNAME y DOCKERHUB_TOKEN configurados en los Settings del repositorio.
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
