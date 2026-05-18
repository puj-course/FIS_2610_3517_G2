import json
import os
import sys


def determinar_badge(score):
    """Devuelve el color y el estado según los rangos de complejidad cognitiva."""
    if score <= 5:
        return "bg-green-100 text-green-800", "Excelente"
    elif score <= 8:
        return "bg-blue-100 text-blue-800", "Aceptable"
    elif score <= 14:
        return "bg-yellow-100 text-yellow-800", "Advertencia"
    else:
        return "bg-red-100 text-red-800", "Crítico"


def generar_html(json_path, html_path):
    if not os.path.exists(json_path):
        print(f"Error: No se encontró el archivo {json_path}")
        return

    with open(json_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    total_funciones = len(data)
    if total_funciones == 0:
        promedio = 0
    else:
        promedio = round(sum(f["complexity"] for f in data) / total_funciones, 2)

    html_content = f"""<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>OddsEngine — Reporte de Complejidad Cognitiva</title>
    <script src="https://cdn.jsdelivr.net/npm/@tailwindcss/browser@4"></script>
</head>
<body class="bg-gray-50 text-gray-900 font-sans antialiased">

    <div class="max-w-6xl mx-auto px-4 py-8">
        <!-- Encabezado -->
        <header class="mb-8 border-b border-gray-200 pb-5">
            <h1 class="text-3xl font-bold text-gray-900">OddsEngine</h1>
            <p class="text-sm text-gray-500 mt-1">Reporte Estadístico de Complejidad Cognitiva (Anidamiento Condicional)</p>
        </header>

        <!-- Tarjetas de Resumen Global -->
        <div class="grid grid-cols-1 md:grid-cols-2 gap-6 mb-8">
            <div class="bg-white p-6 rounded-lg shadow-xs border border-gray-100">
                <p class="text-sm font-medium text-gray-500 uppercase tracking-wider">Total de Funciones Analizadas</p>
                <p class="text-3xl font-bold text-indigo-600 mt-2">{total_funciones}</p>
            </div>
            <div class="bg-white p-6 rounded-lg shadow-xs border border-gray-100">
                <p class="text-sm font-medium text-gray-500 uppercase tracking-wider">Promedio de Complejidad</p>
                <p class="text-3xl font-bold text-indigo-600 mt-2">{promedio}</p>
            </div>
        </div>

        <!-- Tabla de Referencia de Parámetros -->
        <div class="mb-8 bg-white shadow-xs rounded-lg border border-gray-200 p-6">
            <h2 class="text-lg font-semibold text-gray-800 mb-4">Guía de Referencia de Parámetros</h2>
            <div class="grid grid-cols-2 sm:grid-cols-4 gap-4">
                <div class="p-3 bg-green-50 border border-green-200 rounded-lg text-center">
                    <span class="px-2.5 py-0.5 text-xs font-semibold rounded-full bg-green-100 text-green-800">Excelente</span>
                    <p class="text-sm font-bold text-gray-700 mt-2">0 a 5</p>
                    <p class="text-xs text-gray-500 mt-1">Código limpio y lineal</p>
                </div>
                <div class="p-3 bg-blue-50 border border-blue-200 rounded-lg text-center">
                    <span class="px-2.5 py-0.5 text-xs font-semibold rounded-full bg-blue-100 text-blue-800">Aceptable</span>
                    <p class="text-sm font-bold text-gray-700 mt-2">6 a 8</p>
                    <p class="text-xs text-gray-500 mt-1">Estructura moderada</p>
                </div>
                <div class="p-3 bg-yellow-50 border border-yellow-200 rounded-lg text-center">
                    <span class="px-2.5 py-0.5 text-xs font-semibold rounded-full bg-yellow-100 text-yellow-800">Advertencia</span>
                    <p class="text-sm font-bold text-gray-700 mt-2">9 a 14</p>
                    <p class="text-xs text-gray-500 mt-1">Lógica densa / anidada</p>
                </div>
                <div class="p-3 bg-red-50 border border-red-200 rounded-lg text-center">
                    <span class="px-2.5 py-0.5 text-xs font-semibold rounded-full bg-red-100 text-red-800">Crítico</span>
                    <p class="text-sm font-bold text-gray-700 mt-2">15+</p>
                    <p class="text-xs text-gray-500 mt-1">Requiere refactorizar</p>
                </div>
            </div>
        </div>

        <!-- Tabla de Funciones -->
        <div class="bg-white shadow-xs rounded-lg border border-gray-200 overflow-hidden">
            <table class="min-w-full divide-y divide-gray-200">
                <thead class="bg-gray-50">
                    <tr>
                        <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Archivo</th>
                        <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Función</th>
                        <th class="px-6 py-3 text-center text-xs font-medium text-gray-500 uppercase tracking-wider">Puntaje</th>
                        <th class="px-6 py-3 text-center text-xs font-medium text-gray-500 uppercase tracking-wider">Estado</th>
                    </tr>
                </thead>
                <tbody class="bg-white divide-y divide-gray-200">
    """

    for item in data:
        badge_style, estado = determinar_badge(item["complexity"])
        html_content += f"""
                    <tr>
                        <td class="px-6 py-4 whitespace-nowrap text-sm font-mono text-gray-600">{item['file']}</td>
                        <td class="px-6 py-4 whitespace-nowrap text-sm font-medium text-gray-900">{item['function']}</td>
                        <td class="px-6 py-4 whitespace-nowrap text-sm text-center font-bold text-gray-700">{item['complexity']}</td>
                        <td class="px-6 py-4 whitespace-nowrap text-center text-sm">
                            <span class="px-2.5 py-0.5 inline-flex text-xs leading-5 font-semibold rounded-full {badge_style}">
                                {estado}
                            </span>
                        </td>
                    </tr>
        """

    html_content += """
                </tbody>
            </table>
        </div>
    </div>

</body>
</html>
    """

    with open(html_path, "w", encoding="utf-8") as f:
        f.write(html_content)

    print(f"¡Éxito! Reporte HTML generado en: {html_path}")


if __name__ == "__main__":
    json_in = (
        sys.argv[1] if len(sys.argv) > 1 else "cognitive_report.json"
    )
    html_out = (
        sys.argv[2] if len(sys.argv) > 2 else "cognitive_report.html"
    )
    generar_html(json_in, html_out)
