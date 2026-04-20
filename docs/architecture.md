# Arquitectura del Sistema — OddsEngine

## Visión General

OddsEngine es una plataforma de análisis probabilístico para apuestas de tenis. Usa una arquitectura de 3 capas: Presentación (React), Lógica de Negocio (FastAPI), y Datos (PostgreSQL).

## Stack Tecnológico

- **Frontend:** React 18 + Vite + Recharts + Axios + React Router
- **Backend:** Python 3.12 + FastAPI + SQLAlchemy async + asyncpg
- **Base de datos:** PostgreSQL 16
- **Testing:** pytest + httpx + pytest-cov

## Estructura de Carpetas

```
OddsEngine/
├── backend/
│   ├── app/
│   │   ├── core/           # Configuración, BD, errores, logging
│   │   ├── models/         # Modelos Pydantic + SQLAlchemy
│   │   ├── providers/      # Proveedores de datos (mock, API)
│   │   ├── repositories/   # Acceso a datos PostgreSQL
│   │   ├── routes/         # Endpoints REST
│   │   ├── services/       # Lógica de negocio
│   │   └── main.py         # Punto de entrada FastAPI
│   ├── scripts/            # Seed de datos
│   └── tests/              # Tests automatizados
├── frontend/
│   └── src/
│       ├── components/     # 25 componentes React
│       ├── context/        # Estado global (Combination, Notification)
│       ├── hooks/          # Hooks personalizados
│       ├── pages/          # 6 páginas
│       ├── services/       # apiClient (Axios)
│       └── styles/         # CSS global
└── docs/                   # Documentación
```

## Flujo de Datos

1. **Usuario** interactúa con React (componentes)
2. **React** envía petición HTTP via Axios (apiClient)
3. **Vite proxy** redirige /api/* al backend (puerto 8000)
4. **FastAPI Router** recibe la petición y la delega al servicio
5. **Service** ejecuta la lógica de negocio
6. **Repository/Provider** obtiene datos de PostgreSQL o Mock
7. **Respuesta JSON** viaja de vuelta al frontend
8. **React** renderiza los datos

## Patrones de Diseño

- **Strategy:** BaseMatchProvider permite intercambiar mock por PostgreSQL
- **Singleton:** Servicios y Storage con instancia única
- **Repository:** Capa de acceso a datos separada de la lógica
- **MVC adaptado:** Routes (Controller) → Services (Model/Logic) → React (View)

## Decisiones Técnicas

| Decisión | Razón |
|----------|-------|
| FastAPI sobre Django | Más ligero, async nativo, auto-documentación Swagger |
| React sobre Angular | Más flexible, ecosystem grande, equipo lo conoce |
| PostgreSQL sobre MongoDB | Datos relacionales (partidos → jugadores, combinadas → selecciones) |
| SQLAlchemy async | No bloquea el event loop de FastAPI |
| Pydantic | Validación de datos en modelos y API |
| Recharts | Gráficas simples sin configuración compleja |
