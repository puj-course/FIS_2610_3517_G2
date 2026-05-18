from fastapi import FastAPI
from fastapi.responses import HTMLResponse
from prometheus_fastapi_instrumentator import Instrumentator
from prometheus_client import generate_latest, REGISTRY

_METRIC_PREFIXES = (
    "http_request_duration_seconds_sum",
    "http_request_duration_seconds_count",
)


def _parse_labels(labels_str: str) -> dict[str, str]:
    """Parsea labels Prometheus 'key="value",key2="value2"' sin regex."""
    labels: dict[str, str] = {}
    for pair in labels_str.split(","):
        if "=" not in pair:
            continue
        key, _, quoted_val = pair.partition("=")
        key = key.strip()
        val = quoted_val.strip().strip('"')
        if key:
            labels[key] = val
    return labels


def _status_badge_class(status: str) -> str:
    if status.startswith("2"):
        return "bg-success"
    if status.startswith("5"):
        return "bg-danger"
    return "bg-warning text-dark"


def _latency_evaluation(promedio: float) -> str:
    if promedio <= 100:
        return '<span class="badge bg-success">Excelente</span>'
    if promedio <= 250:
        return '<span class="badge bg-info text-dark">Bueno</span>'
    if promedio <= 500:
        return '<span class="badge bg-warning text-dark">Aceptable</span>'
    return '<span class="badge bg-danger">Lento</span>'


def _parse_metric_line(linea: str):
    """
    Parsea una línea de métrica Prometheus sin regex.

    Retorna (nombre_metrica, labels_dict, valor_float) o None.
    """
    brace_open = linea.find("{")
    brace_close = linea.find("}", brace_open + 1) if brace_open != -1 else -1

    if brace_open == -1 or brace_close == -1:
        return None

    metric_name = linea[:brace_open]
    if metric_name not in _METRIC_PREFIXES:
        return None

    labels_str = linea[brace_open + 1:brace_close]
    valor_str = linea[brace_close + 1:].strip()

    if not valor_str:
        return None

    try:
        valor = float(valor_str)
    except ValueError:
        return None

    labels = _parse_labels(labels_str)
    return metric_name, labels, valor


def _collect_latency_metrics(metrics_text: str) -> tuple[dict, dict]:
    sumas_latencia: dict = {}
    conteos_peticiones: dict = {}
    for linea in metrics_text.splitlines():
        parsed = _parse_metric_line(linea)
        if parsed is None:
            continue
        metrica, labels, valor = parsed
        handler = labels.get("handler", "unknown")
        method = labels.get("method", "unknown")
        status = labels.get("status", "unknown")
        key = (method, handler, status)
        if metrica == "http_request_duration_seconds_sum":
            sumas_latencia[key] = valor
        elif metrica == "http_request_duration_seconds_count":
            conteos_peticiones[key] = int(valor)
    return sumas_latencia, conteos_peticiones


def _consolidate_latency_data(sumas_latencia: dict, conteos_peticiones: dict) -> list[tuple]:
    datos = []
    for key in conteos_peticiones:
        method, handler, status = key
        total = conteos_peticiones[key]
        suma = sumas_latencia.get(key, 0.0)
        promedio = round((suma / total) * 1000, 1) if total > 0 else 0
        datos.append((method, handler, status, total, promedio))
    datos.sort(key=lambda x: x[4], reverse=True)
    return datos


def _build_latency_table_rows(datos_consolidados: list[tuple]) -> str:
    if not datos_consolidados:
        return '<tr><td colspan="6" class="text-center text-muted py-4">No hay peticiones registradas aún. Presiona el botón de arriba para generar tráfico de prueba.</td></tr>'
    filas = ""
    for method, handler, status, total, promedio in datos_consolidados:
        badge_status = _status_badge_class(status)
        evaluacion = _latency_evaluation(promedio)
        alerta = "table-danger fw-bold" if promedio > 500 else ""
        filas += f"""
            <tr class="{alerta}">
                <td><span class="badge bg-dark">{method}</span></td>
                <td><code>{handler}</code></td>
                <td><span class="badge {badge_status}">{status}</span></td>
                <td>{total}</td>
                <td class="font-monospace">{promedio} ms</td>
                <td>{evaluacion}</td>
            </tr>
            """
    return filas


def setup_metrics(app: FastAPI):

    # 1. Monitoreo y exposición de métricas nativas
    Instrumentator().instrument(app).expose(app)

    # 2. Dashboard interactivo
    @app.get("/dashboard", response_class=HTMLResponse, include_in_schema=False)
    async def latencies_dashboard():
        data_cruda = generate_latest(REGISTRY).decode("utf-8")
        sumas, conteos = _collect_latency_metrics(data_cruda)
        datos = _consolidate_latency_data(sumas, conteos)
        filas_tabla = _build_latency_table_rows(datos)

        html_template = """
        <!DOCTYPE html>
        <html lang="es">
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>OddsEngine — Rendimiento</title>
            <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css" rel="stylesheet">
            <style>
                body { background-color: #f4f6f9; font-family: system-ui, sans-serif; }
                .card { border: none; border-radius: 10px; box-shadow: 0 4px 12px rgba(0,0,0,0.05); }
                .font-monospace { font-family: 'Courier New', Courier, monospace; }
                .text-navy { color: #1e3a8a; }
            </style>
        </head>
        <body>
            <div class="container py-5">
                <div class="d-flex justify-content-between align-items-center mb-4">
                    <div>
                        <h1 class="fw-bold text-navy">OddsEngine Analyser</h1>
                        <p class="text-muted mb-0">Monitoreo de latencia y pruebas automatizadas</p>
                    </div>
                    <button class="btn btn-outline-primary fw-bold" onclick="window.location.reload()">
                         Recargar Dashboard
                    </button>
                </div>
                
                <!-- AUTOMATIZADOR DE PETICIONES (todos los métodos HTTP) -->
                <div class="card p-4 bg-white mb-4">
                    <h5 class="fw-bold text-dark mb-1"> Ejecutor Automático de Endpoints (OpenAPI Scan)</h5>
                    <p class="text-muted small mb-3">
                        Lee el esquema OpenAPI, detecta <strong>todas</strong> las rutas y métodos HTTP
                        (GET, POST, DELETE, etc.) y les envía una petición de prueba para registrarlas en las métricas.
                    </p>
                    <div class="text-center mb-3">
                        <button id="btnMasivo" class="btn btn-danger btn-lg px-5 fw-bold" onclick="testearTodosLosEndpoints()">
                             Disparar peticiones a todas las rutas
                        </button>
                    </div>
                    <div id="logsEjecucion" class="text-start font-monospace small d-none p-3 bg-dark text-light rounded" style="max-height: 200px; overflow-y: auto; white-space: pre-wrap;"></div>
                </div>

                <!-- TABLA DE RENDIMIENTO -->
                <div class="card p-4 bg-white mb-5">
                    <h5 class="fw-bold text-secondary mb-3"> Métricas de Endpoints Actuales</h5>
                    <div class="table-responsive">
                        <table class="table table-hover align-middle mb-0">
                            <thead class="table-light">
                                <tr>
                                    <th>Método</th>
                                    <th>Ruta</th>
                                    <th>Estado HTTP</th>
                                    <th>Peticiones</th>
                                    <th>Latencia (Promedio)</th>
                                    <th>Evaluación</th>
                                </tr>
                            </thead>
                            <tbody>
                                {{FILAS_TABLA}}
                            </tbody>
                        </table>
                    </div>
                </div>

                <!-- GUÍA -->
                <div class="row">
                    <div class="col-md-8 col-lg-6">
                        <h6 class="fw-bold text-secondary mb-3">Guía de Referencia de Latencias</h6>
                        <div class="card p-3 bg-white">
                            <table class="table table-sm table-borderless mb-0 align-middle">
                                <tbody>
                                    <tr>
                                        <td style="width: 100px;"><span class="badge bg-success w-100">Excelente</span></td>
                                        <td><strong>&le; 100 ms</strong> <span class="text-muted">— Respuesta casi instantánea.</span></td>
                                    </tr>
                                    <tr>
                                        <td><span class="badge bg-info text-dark w-100">Bueno</span></td>
                                        <td><strong>&le; 250 ms</strong> <span class="text-muted">— Estándar óptimo para la web.</span></td>
                                    </tr>
                                    <tr>
                                        <td><span class="badge bg-warning text-dark w-100">Aceptable</span></td>
                                        <td><strong>&le; 500 ms</strong> <span class="text-muted">— Tolerable para operaciones complejas.</span></td>
                                    </tr>
                                    <tr>
                                        <td><span class="badge bg-danger w-100">Lento</span></td>
                                        <td><strong>&gt; 500 ms</strong> <span class="text-muted">— Lentitud perceptible, requiere optimización.</span></td>
                                    </tr>
                                </tbody>
                            </table>
                        </div>
                    </div>
                </div>
            </div>

            <script>
                /**
                 * Genera un body de prueba mínimo según el esquema OpenAPI del endpoint.
                 * Evita enviar {} vacío a rutas que requieren campos obligatorios.
                 */
                function buildBody(pathDef) {
                    try {
                        const reqBody = pathDef.requestBody;
                        if (!reqBody) return null;
                        const schema = reqBody.content?.['application/json']?.schema;
                        if (!schema) return {};
                        const props = schema.properties || {};
                        const required = schema.required || [];
                        const body = {};
                        for (const field of required) {
                            const type = props[field]?.type;
                            if (type === 'string') body[field] = 'test';
                            else if (type === 'integer' || type === 'number') body[field] = 0;
                            else if (type === 'boolean') body[field] = false;
                            else body[field] = null;
                        }
                        return body;
                    } catch (e) {
                        return {};
                    }
                }

                /**
                 * Sustituye parámetros de ruta ({match_id}, {combination_id}, etc.)
                 * con valores de prueba para que la petición llegue al servidor.
                 */
                function resolvePathParams(path, pathDef) {
                    let resolved = path;
                    const params = (pathDef.parameters || []).filter(p => p.in === 'path');
                    for (const param of params) {
                        const placeholder = `{${param.name}}`;
                        // Valor según el tipo del parámetro
                        const type = param.schema?.type || 'string';
                        const value = type === 'integer' ? '1' : 'test-id';
                        resolved = resolved.replace(placeholder, value);
                    }
                    return resolved;
                }

                async function testearTodosLosEndpoints() {
                    const btn = document.getElementById('btnMasivo');
                    const logsBox = document.getElementById('logsEjecucion');

                    btn.disabled = true;
                    btn.innerText = 'Escaneando y disparando...';
                    logsBox.classList.remove('d-none');
                    logsBox.innerHTML = 'Extrayendo esquema OpenAPI... (/openapi.json)...\\n';

                    try {
                        const resOpenApi = await fetch('/openapi.json');
                        const schema = await resOpenApi.json();
                        const paths = schema.paths || {};

                        // Construir lista de todas las combinaciones método+ruta
                        const METODOS_SOPORTADOS = ['get', 'post', 'put', 'patch', 'delete'];
                        const tareas = [];

                        for (const ruta in paths) {
                            for (const metodo of METODOS_SOPORTADOS) {
                                if (paths[ruta][metodo]) {
                                    tareas.push({ ruta, metodo, def: paths[ruta][metodo], pathDef: paths[ruta] });
                                }
                            }
                        }

                        if (tareas.length === 0) {
                            logsBox.innerHTML += ' No se encontraron endpoints en el esquema.\\n';
                            btn.disabled = false;
                            btn.innerText = ' Disparar peticiones a todas las rutas';
                            return;
                        }

                        logsBox.innerHTML += `🟢 Detectados ${tareas.length} endpoints. Iniciando ráfaga...\\n\\n`;

                        for (const { ruta, metodo, def, pathDef } of tareas) {
                            const rutaResuelta = resolvePathParams(ruta, def);
                            logsBox.innerHTML += `[${metodo.toUpperCase().padEnd(6)}] ${rutaResuelta} ... `;

                            try {
                                const opciones = {
                                    method: metodo.toUpperCase(),
                                    headers: { 'Content-Type': 'application/json' },
                                };

                                if (['post', 'put', 'patch'].includes(metodo)) {
                                    const body = buildBody(def);
                                    if (body !== null) opciones.body = JSON.stringify(body);
                                }

                                const start = performance.now();
                                const response = await fetch(rutaResuelta, opciones);
                                const diff = (performance.now() - start).toFixed(0);

                                logsBox.innerHTML += `HTTP ${response.status} en ${diff}ms\\n`;
                            } catch (err) {
                                logsBox.innerHTML += `❌ Error de red\\n`;
                            }

                            logsBox.scrollTop = logsBox.scrollHeight;
                        }

                        logsBox.innerHTML += '\\n ¡Prueba completa! Recargando métricas...\\n';
                        setTimeout(() => { window.location.reload(); }, 1500);

                    } catch (error) {
                        logsBox.innerHTML += ' Error crítico al leer el esquema OpenAPI.\\n';
                        btn.disabled = false;
                        btn.innerText = ' Disparar peticiones a todas las rutas';
                    }
                }
            </script>
        </body>
        </html>
        """
        
        return html_template.replace("{{FILAS_TABLA}}", filas_tabla)
