# Reporte de Calidad — OddsEngine

## Métricas de Testing

| Métrica | Valor |
|---------|-------|
| Total tests | 82 |
| Tests pasando | 82 |
| Tests fallando | 0 |
| Cobertura | 83% |
| Tiempo ejecución | ~4.2s |

## Distribución de Tests

| Archivo | Tests | Cobertura |
|---------|-------|-----------|
| test_matches.py | 11 | GET /matches, filtros, 404 |
| test_error_handling.py | 7 | JSON formato, estabilidad |
| test_combinations.py | 15 | CRUD, duplicados, validaciones |
| test_integration_hu02.py | 5 | Flujos completos |
| test_stats.py | 8 | Estadísticas, H2H, win rates |
| test_probability.py | 12 | Fórmula, factores, coherencia |
| test_history.py | 8 | Historial, completar, exportar |
| test_pagination.py | 6 | Paginación, límites |
| test_validation.py | 6 | Campos requeridos, rangos |
| test_health.py | 4 | Health básico y detallado |

## Tipos de Tests

- **Unitarios (60):** Cada endpoint y servicio probado individualmente
- **Integración (15):** Flujos completos (partidos → combinada → probabilidad → resultado)
- **Edge cases (7):** Inyección caracteres, payloads, concurrencia

## Comando para Ejecutar
```bash
cd backend
pytest tests/ -v
pytest tests/ -v --cov=app --cov-report=term-missing
```
