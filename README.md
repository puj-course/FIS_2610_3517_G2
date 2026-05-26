# 🎾 OddsEngine

<p align="center">
  <img src="./Odds%20Engine.png" alt="OddsEngine Logo" width="640">
</p>

<p align="center"><i>"Un análisis, una combinada, una probabilidad real."</i></p>

---

# 📖 Descripción

* **OddsEngine** es una plataforma enfocada en el análisis probabilístico de apuestas deportivas en tenis.

* La plataforma centraliza información deportiva proveniente de APIs especializadas y procesa estadísticas para calcular probabilidades estimadas en apuestas individuales y combinadas.

* El sistema busca reducir el análisis manual realizado por los usuarios, automatizando el procesamiento de datos deportivos y permitiendo decisiones fundamentadas estadísticamente.

* OddsEngine surge como respuesta a la necesidad de contar con herramientas analíticas estructuradas para apuestas deportivas, reemplazando procesos basados únicamente en intuición por modelos probabilísticos sustentados en datos.

* La plataforma integra frontend, backend y persistencia de datos dentro de una arquitectura desacoplada y contenerizada, facilitando escalabilidad, mantenimiento y despliegue automatizado.

---

# 👥 Equipo del Proyecto

| Nombre             | Rol Scrum                               | GitHub                                                             |
| ------------------ | --------------------------------------- | ------------------------------------------------------------------ |
| David Orjuela      | Scrum Master / QA Lead                  | [https://github.com/Kerosene21](https://github.com/Kerosene21)     |
| Juan Pablo Álvarez | Product Owner / Backend Developer       | [https://github.com/Sleppyhed](https://github.com/Sleppyhed)       |
| Nicolás Sánchez    | Sprint Planner / Configuration Manager  | [https://github.com/nicosanlucon](https://github.com/nicosanlucon) |
| Lucas Rincón       | Documentation Lead / Frontend Developer | [https://github.com/Lcks07](https://github.com/Lcks07)             |

---

# 🛠 Tecnologías Utilizadas

* **Frontend:** React + Vite
* **Backend:** Python + FastAPI
* **Base de Datos:** PostgreSQL
* **Análisis de Datos:** Pandas
* **Visualización:** Recharts
* **Contenerización:** Docker + Docker Compose
* **CI/CD:** GitHub Actions
* **Calidad de Código:** SonarQube
* **Control de versiones:** Git
* **Arquitectura de repositorio:** Monorepo Fullstack

---

# 🏗 Arquitectura del Sistema

El proyecto sigue una arquitectura de **monorepo fullstack** compuesta por tres servicios principales orquestados mediante Docker Compose:

```text
Frontend (React + Vite :80)
        ↓
Backend API (FastAPI :8000)
        ↓
PostgreSQL (:5432)
```

## Componentes principales

* Cliente frontend desarrollado con React.
* API REST desarrollada en FastAPI.
* Persistencia de datos mediante PostgreSQL.
* Backend estructurado por capas utilizando servicios, rutas, repositorios y modelos.
* Contenerización completa mediante Docker.
* Orquestación de servicios con Docker Compose.
* Pipeline automatizado de integración y despliegue continuo.

---

# 📂 Estructura del Proyecto

```text
FIS_2610_3517_G2/
├── .github/
│   ├── ISSUE_TEMPLATE/
│   ├── PULL_REQUEST_TEMPLATE.md
│   └── workflows/
│       ├── build.yml
│       ├── cd.yml
│       ├── ci.yml
│       ├── docker-deploy.yml
│       ├── friday-auto-pr.yml
│       └── weekly-commits-report.yml
├── backend/
│   ├── app/
│   │   ├── core/
│   │   ├── metrics/
│   │   ├── models/
│   │   ├── providers/
│   │   ├── repositories/
│   │   ├── routes/
│   │   ├── services/
│   │   └── main.py
│   ├── scripts/
│   ├── tests/
│   ├── Dockerfile
│   ├── pyproject.toml
│   ├── requirements.txt
│   └── .env.example
├── frontend/
│   ├── src/
│   ├── index.html
│   ├── package.json
│   ├── vite.config.js
│   ├── nginx.conf
│   └── Dockerfile
├── docs/
│   ├── architecture.md
│   ├── endpoints.md
│   ├── installation_guide.md
│   ├── probability_engine.md
│   ├── frontend_components.md
│   ├── quality_metrics.md
│   ├── Diagramas.md
│   ├── DiagramasPatronGof.md
│   ├── testing/
│   ├── retrospectives/
│   └── research/
├── jupyter/
│   ├── datasets/
│   └── notebooks/
├── scripts/
│   ├── deploy.sh
│   ├── setup.sh
│   └── test.sh
├── conf/
├── src/
│   ├── main/
│   └── test/
├── temp/
├── CHANGELOG.md
├── CONTRIBUTING.md
├── DOCKER.md
├── LICENSE
├── Makefile
├── README.md
├── SETUP.md
├── docker-compose.yml
└── sonar-project.properties
```

---

# 🚀 Instalación y Ejecución

## 🔹 Requisitos

* Docker y Docker Compose
* Git
* Python 3.10+
* Node.js

---

## 🔹 Clonar el repositorio

```bash
git clone https://github.com/puj-course/FIS_2610_3517_G2.git
cd FIS_2610_3517_G2
```

---

## 🔹 Configurar variables de entorno

```bash
cp backend/.env.example .env
Editar `.env`: `DATA_MODE=database` y `DATABASE_URL=postgresql+asyncpg://postgres:PASSWORD@localhost:5432/oddsengine`

```

Configura las variables necesarias para la conexión con PostgreSQL y servicios externos.

---

## 🔹 Ejecución con Docker

```bash
docker-compose up --build
```

## Servicios disponibles

| Servicio   | Puerto |
| ---------- | ------ |
| Frontend   | 80     |
| Backend    | 8000   |
| PostgreSQL | 5432   |

---


## 🔹 Ejecución local del backend

```bash
cd backend
pip install -r requirements.txt
uvicorn app.main:app --reload
```

---

## 🔹 Ejecución local del frontend

```bash
cd frontend
npm install
npm run dev
```

---

# 🌐 API REST

La aplicación expone endpoints REST mediante FastAPI para operaciones relacionadas con:

* Consulta y procesamiento de estadísticas deportivas.
* Cálculo probabilístico.
* Gestión de combinadas.
* Integración con fuentes externas de datos deportivos.
* Métricas y monitoreo.

La documentación técnica y definición de endpoints se encuentra en:

# Endpoints disponibles

| Método | Ruta | Descripción |
|--------|------|-------------|
| GET | `/health` | Health check |
| GET | `/api/matches` | Listar partidos |
| GET | `/api/matches/{id}` | Obtener partido por ID |
| GET | `/dashboard` | Ver analisis de latencia |
| GET | `/metrics` | Datos crudos de latencia |
| GET | `/openapi.json` | Interfaces de API |
| POST | `/api/auth/login` | Inicio de sesion |
| POST | `/api/combinations` | Guardar combinada |


```text
docs/endpoints.md
```

---

# ⚙️ CI/CD y Calidad de Código

El proyecto incorpora automatización mediante GitHub Actions.

| Workflow                    | Descripción                                    |
| --------------------------- | ---------------------------------------------- |
| `ci.yml`                    | Integración continua y validación del proyecto |
| `cd.yml`                    | Flujo de despliegue continuo                   |
| `build.yml`                 | Construcción automatizada                      |
| `docker-deploy.yml`         | Despliegue de contenedores Docker              |
| `weekly-commits-report.yml` | Reporte automático semanal                     |
| `friday-auto-pr.yml`        | Automatización de Pull Requests                |

Además, el proyecto incluye:

* Métricas de calidad.
* Instrumentación Prometheus.
* Cobertura de pruebas.
* Configuración SonarQube.

---

# 🎯 Propuesta de Valor

## ¿Por qué usar OddsEngine?

* Centraliza información deportiva de tenis.
* Calcula probabilidades combinadas automáticamente.
* Reduce el análisis manual.
* Permite decisiones basadas en datos.
* Mejora la interpretación estadística de apuestas deportivas.

---

# 🔎 Diferenciador

* Plataforma enfocada exclusivamente en tenis.
* Motor probabilístico especializado.
* Arquitectura desacoplada y contenerizada.
* Integración con APIs deportivas.
* Enfoque académico y analítico.

---

# 📚 Contexto Académico

Proyecto desarrollado en el marco de la asignatura:

| Campo       | Detalle                               |
| ----------- | ------------------------------------- |
| Asignatura  | Fundamentos de Ingeniería de Software |
| Código      | FIS 2610 – Grupo 3517 G2              |
| Institución | Pontificia Universidad Javeriana      |
| Facultad    | Ingeniería                            |
| Año         | 2026                                  |

---

# 📩 Contacto

## Equipo de desarrollo

**David Orjuela**
GitHub: [https://github.com/Kerosene21](https://github.com/Kerosene21)

**Juan Pablo Álvarez**
GitHub: [https://github.com/Sleppyhed](https://github.com/Sleppyhed)

**Nicolás Sánchez**
GitHub: [https://github.com/nicosanlucon](https://github.com/nicosanlucon)

**Lucas Rincón**
GitHub: [https://github.com/Lcks07](https://github.com/Lcks07)

---

# 📄 Licencia

Proyecto desarrollado con fines académicos en el marco de la asignatura Fundamentos de Ingeniería de Software — Pontificia Universidad Javeriana.

Ver `LICENSE` para más detalles.


