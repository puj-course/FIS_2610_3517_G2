# Métricas de Calidad — OddsEngine

## Resumen

| # | Métrica | Tipo | Herramienta | Resultado |
|---|---------|------|-------------|-----------|
| 1 | Latencia de endpoints | Rendimiento | Middleware propio | ✅ Pass |
| 2 | Complejidad ciclomática | Mantenibilidad | AST / radon | ✅ Pass |
| 3 | Invariantes de lógica de negocio | Corrección funcional | Módulo propio | ✅ Pass |
| 4 | Coverage | Cobertura de pruebas | SonarQube | Ver sección 4 |
| 5 | Mantenibilidad | Deuda técnica | SonarQube | Ver sección 5 |

---

## Métricas implementadas en código

### Métrica 1 — Latencia de endpoints

**Archivo:** `backend/app/main.py` — middleware `log_requests`

**¿Qué mide?**  
El tiempo de respuesta de cada endpoint HTTP en milisegundos, medido
desde que la request entra al servidor hasta que la response es enviada.

**¿Cómo funciona?**  
```python
@app.middleware("http")
async def log_requests(request: Request, call_next):
    start = time.time()
    response = await call_next(request)
    duration = round((time.time() - start) * 1000, 1)
    logger.info(f"{request.method} {request.url.path} → {response.status_code} ({duration}ms)")
    return response
```

**Interpretación del resultado:**

| Rango | Interpretación |
|-------|---------------|
| < 200ms | Aceptable para una API REST |
| 200–500ms | Requiere revisión; posible consulta lenta o lógica costosa |
| > 500ms | Inaceptable en producción; investigar cuello de botella |

**Impacto en el sistema:**  
Una latencia alta en `/api/probability/{match_id}` afecta directamente
la experiencia del usuario al consultar probabilidades antes de confirmar
una apuesta. Si el cálculo supera 500ms, el usuario puede abandonar la
sesión antes de completar la combinada.

**Acciones de mejora si el resultado fuera deficiente:**  
Implementar caché en memoria (por ejemplo con `functools.lru_cache` o
Redis) para los resultados de `calculate_individual`, dado que las
estadísticas de un partido no cambian entre requests del mismo usuario
en la misma sesión.

---

### Métrica 2 — Complejidad Ciclomática

**Archivo:** `backend/app/metrics/cyclomatic_complexity.py`  
**Tests:** `backend/tests/test_custom_metrics.py` — clase `TestCyclomaticComplexity`

**¿Qué mide?**  
El número de caminos independientes de ejecución dentro de cada función,
calculado sobre el AST (árbol de sintaxis abstracta) de Python. Se basa
en la fórmula de McCabe (1976):

```
CC = E - N + 2P
```

En la práctica equivale a contar los puntos de decisión (`if`, `elif`,
`for`, `while`, `except`, `and`, `or`) y sumarle 1.

**Umbrales:**

| CC | Rank | Nivel | Implicación |
|----|------|-------|-------------|
| 1–5 | A | Bajo | Simple, fácil de testear |
| 6–10 | B | Moderado | Manejable, requiere atención |
| 11–15 | C | Alto | Difícil de mantener |
| > 15 | D/E/F | Crítico | Refactorización urgente |

**Resultado obtenido:**  
Todas las funciones del backend se encuentran por debajo de CC=15
(ninguna en rango crítico). El promedio del proyecto está dentro del
límite aceptable de CC=10. La función con mayor complejidad es
`_determine_confidence` en `probability_service.py` con CC≈6 (Rank B),
lo cual es aceptable pero es la zona a vigilar si el modelo crece.

**Impacto en el sistema:**  
Un CC alto en `_calculate_score` o `calculate_combination` implicaría
que existen caminos del motor de probabilidad que no están cubiertos
por ningún test, aumentando la probabilidad de defectos silenciosos
en los cálculos que se muestran al usuario.

**Acciones de mejora si el resultado fuera deficiente:**  
Extraer cada factor de probabilidad a su propia función pura:
`_factor_recent_form()`, `_factor_h2h()`, `_factor_surface()`.
Esto reduciría el CC de `_calculate_score` de ~7 a ~2, y cada
factor podría testearse de forma aislada.

---

### Métrica 3 — Invariantes de Lógica de Negocio

**Archivo:** `backend/app/metrics/business_invariants.py`  
**Tests:** `backend/tests/test_custom_metrics.py` — clase `TestBusinessInvariants`

**¿Qué mide?**  
Propiedades matemáticas que el motor de probabilidades debe cumplir
en todo momento, independientemente de los datos de entrada. Verifica
la corrección semántica de los valores calculados, no la sintaxis del
código.

**Invariantes implementadas:**

| ID | Invariante | Fundamento |
|----|-----------|------------|
| INV-01 | P(local) + P(visitante) = 100.0 ± 0.15 | Ley de probabilidad total |
| INV-02 | 0.0 ≤ P ≤ 100.0 para cada jugador | Definición de probabilidad |
| INV-03 | RiskLevel coherente con los umbrales definidos | Consistencia del modelo de negocio |
| INV-04 | P(combinada) ≤ min(P individuales) | Regla de multiplicación de probabilidades |
| INV-05 | Suma de pesos del modelo = 1.0 | Definición de media ponderada |

**Resultado obtenido:**  
Las 5 invariantes pasan. Los pesos del modelo suman exactamente 1.0
(0.40 + 0.30 + 0.30). Las probabilidades de los casos de prueba son
complementarias y están en rango válido. Los niveles de riesgo
corresponden a los umbrales definidos en `classify_risk()`.

**Interpretación detallada:**  
Una falla en INV-01 no producirá ninguna excepción en tiempo de
ejecución; el sistema seguirá funcionando pero mostrará probabilidades
matemáticamente inválidas. Es el tipo de bug más peligroso porque es
silencioso. Una falla en INV-03 le mostraría al usuario "riesgo bajo"
para una combinada con 5% de probabilidad de éxito, violando
directamente la promesa del producto.

**Acciones de mejora si el resultado fuera deficiente:**  
Para INV-05, agregar un assert al inicio del módulo de forma que el
error falle en el arranque del servidor y no silenciosamente en
producción:
```python
assert abs(WEIGHT_RECENT_FORM + WEIGHT_H2H + WEIGHT_SURFACE - 1.0) < 1e-9, \
    "Los pesos del modelo deben sumar 1.0"
```

---

## Métricas mediante SonarQube

### Métrica 4 — Coverage (Cobertura de pruebas)

**¿Qué mide?**  
El porcentaje de líneas de código del backend que son ejecutadas por
al menos un test. Se configura en `sonar-project.properties` con el
reporte `coverage.xml` generado por `pytest-cov`.

**Interpretación:**

| Coverage | Interpretación |
|----------|---------------|
| > 80% | Buena cobertura; la mayoría de caminos están testeados |
| 60–80% | Cobertura aceptable pero con zonas de riesgo |
| < 60% | Cobertura insuficiente; cambios al código tienen alto riesgo de introducir regresiones silenciosas |

**Impacto en el sistema:**  
Un coverage del 50% en `probability_service.py` significaría que la
mitad de los caminos del motor de cálculo nunca son ejecutados durante
las pruebas. Cualquier cambio al modelo de pesos o a la lógica de
confianza podría introducir un bug que ningún test detectaría.

**Acciones de mejora:**  
Agregar tests parametrizados que cubran los casos borde de
`_calculate_score`: stats con todos los factores en cero, head-to-head
sin historial, y surface win rate igual a 50%.

---

### Métrica 5 — Mantenibilidad

**¿Qué mide?**  
SonarQube calcula la deuda técnica del proyecto: el tiempo estimado
que tomaría corregir todos los code smells detectados (nombres
confusos, funciones demasiado largas, código duplicado, etc.).
La calificación va de A a E.

**Interpretación:**

| Calificación | Deuda técnica | Significado |
|-------------|--------------|-------------|
| A | < 5% del tiempo de desarrollo | Código limpio y bien estructurado |
| B | 6–10% | Deuda manejable; algunos smells menores |
| C | 11–20% | Requiere atención; la deuda está creciendo |
| D | 21–50% | Problemático; el mantenimiento se está volviendo costoso |
| E | > 50% | Crítico; el código es difícil de modificar sin introducir bugs |

**Impacto en el sistema:**  
Una calificación C o D en mantenibilidad en los servicios de
probabilidad significaría que agregar un nuevo factor al modelo
(por ejemplo ranking ATP) tomaría desproporcionadamente más tiempo
del esperado, y con mayor riesgo de introducir regresiones.

**Acciones de mejora:**  
Resolver los code smells priorizando los del módulo `probability_service.py`
por ser el núcleo del sistema, luego `combination_service.py` por ser
el de mayor volumen de operaciones.
