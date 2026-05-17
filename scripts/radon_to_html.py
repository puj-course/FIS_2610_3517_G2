#!/usr/bin/env python3
"""
Convierte el reporte JSON de radon a un reporte HTML visual.
Uso: python radon_to_html.py <input_json> <output_html>
"""

import json
import sys
import os
from datetime import datetime

def parse_radon_json(json_file_path):
    """Lee y parsea el JSON generado por radon"""
    with open(json_file_path, 'r', encoding='utf-8') as f:
        data = json.load(f)
    return data

def get_complexity_grade(complexity):
    """Determina la letra de complejidad según el valor numérico"""
    if complexity <= 5:
        return 'A', '#28a745'
    elif complexity <= 10:
        return 'B', '#17a2b8'
    elif complexity <= 20:
        return 'C', '#ffc107'
    elif complexity <= 30:
        return 'D', '#fd7e14'
    elif complexity <= 40:
        return 'E', '#dc3545'
    else:
        return 'F', '#6c757d'

def generate_html_report(json_data, output_path):
    """Genera el reporte HTML a partir de los datos del JSON"""
    
    total_blocks = 0
    total_complexity = 0
    high_complexity_blocks = []
    critical_blocks = []
    
    # Procesar cada archivo
    files_data = []
    for file_path, blocks in json_data.items():
        file_complexity = 0
        file_blocks_count = 0
        file_high_complexity = []
        
        for block in blocks:
            complexity = block.get('complexity', 0)
            total_complexity += complexity
            total_blocks += 1
            file_complexity += complexity
            file_blocks_count += 1
            
            block_info = {
                'name': block.get('name', 'unknown'),
                'lineno': block.get('lineno', 0),
                'complexity': complexity,
                'type': block.get('type', 'function'),
                'grade': get_complexity_grade(complexity)
            }
            
            if complexity > 10:
                file_high_complexity.append(block_info)
                high_complexity_blocks.append({
                    'file': file_path,
                    **block_info
                })
                
                if complexity > 20:
                    critical_blocks.append({
                        'file': file_path,
                        **block_info
                    })
        
        avg_complexity = file_complexity / file_blocks_count if file_blocks_count > 0 else 0
        
        files_data.append({
            'path': file_path,
            'blocks_count': file_blocks_count,
            'total_complexity': file_complexity,
            'avg_complexity': avg_complexity,
            'high_complexity_blocks': file_high_complexity
        })
    
    # Ordenar por complejidad promedio
    files_data.sort(key=lambda x: x['avg_complexity'], reverse=True)
    
    # Calcular promedio general
    avg_total = total_complexity / total_blocks if total_blocks > 0 else 0
    avg_grade, avg_color = get_complexity_grade(avg_total)
    
    # Preparar la sección de alerta
    alert_section = ""
    if high_complexity_blocks:
        critical_text = f" ({len(critical_blocks)} de ellas son críticas con complejidad > 20)" if critical_blocks else ""
        alert_section = f'''
        <div class="alert alert-critical">
            <strong>Atención:</strong> Se encontraron {len(high_complexity_blocks)} funciones con complejidad mayor a 10.{critical_text}
            Revisa la sección de "Funciones Problemáticas" para más detalles.
        </div>
        '''
    else:
        alert_section = '''
        <div class="alert">
            <strong>Bien!</strong> No se encontraron funciones con complejidad mayor a 10. El código tiene buena salud.
        </div>
        '''
    
    # Preparar la sección de funciones problemáticas
    problem_functions_section = ""
    if high_complexity_blocks:
        blocks_html = []
        for block in high_complexity_blocks[:20]:
            grade_letter, grade_color = block['grade']
            blocks_html.append(f'''
                <div class="block-item">
                    <strong>{block['file']}</strong><br>
                    <span style="margin-left: 20px;"><code>{block['name']}</code> (línea {block['lineno']})</span><br>
                    <span style="margin-left: 20px;">Complejidad: <span class="complexity-number" style="color: {grade_color}">{block['complexity']}</span> 
                    <span class="grade-badge" style="background-color: {grade_color}; width: 25px; height: 25px; line-height: 25px; font-size: 14px; display: inline-block;">{grade_letter}</span></span>
                </div>
            ''')
        
        more_text = ""
        if len(high_complexity_blocks) > 20:
            more_text = f'<p style="margin-top: 10px; color: #666;"><small>... y {len(high_complexity_blocks) - 20} más</small></p>'
        
        problem_functions_section = f'''
        <div class="section">
            <h2>Funciones Problemáticas (Complejidad > 10)</h2>
            <div class="block-list">
                {''.join(blocks_html)}
            </div>
            {more_text}
        </div>
        '''
    
    # Preparar la tabla de archivos
    rows_html = []
    for file in files_data[:50]:
        avg_grade_file, avg_color_file = get_complexity_grade(file['avg_complexity'])
        problem_count_color = '#dc3545' if file['high_complexity_blocks'] else '#28a745'
        rows_html.append(f'''
        <tr>
            <td style="font-family: monospace; font-size: 13px;">{file['path']}</td>
            <td>{file['blocks_count']}</td>
            <td>{file['total_complexity']:.0f}</td>
            <td>
                <div style="display: flex; align-items: center; gap: 10px;">
                    <div class="complexity-bar">
                        <div class="complexity-fill" style="width: {min(100, file['avg_complexity'] * 5)}%; background-color: {avg_color_file}"></div>
                    </div>
                    <span>{file['avg_complexity']:.1f}</span>
                </div>
            </td>
            <td style="color: {problem_count_color}">
                {len(file['high_complexity_blocks'])}
            </td>
        </tr>
        ''')
    
    files_table_footer = ""
    if len(files_data) > 50:
        files_table_footer = f'<p style="margin-top: 10px; color: #666;"><small>Mostrando los primeros 50 archivos de {len(files_data)}</small></p>'
    
    # Generar HTML
    html_content = f"""<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Reporte de Complejidad Ciclomática - OddsEngine</title>
    <style>
        * {{
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }}
        
        body {{
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue', Arial, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            padding: 20px;
        }}
        
        .container {{
            max-width: 1400px;
            margin: 0 auto;
        }}
        
        .header {{
            background: white;
            border-radius: 12px;
            padding: 30px;
            margin-bottom: 20px;
            box-shadow: 0 4px 6px rgba(0,0,0,0.1);
        }}
        
        .header h1 {{
            color: #333;
            font-size: 28px;
            margin-bottom: 10px;
        }}
        
        .header .subtitle {{
            color: #666;
            font-size: 14px;
        }}
        
        .stats-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
            gap: 20px;
            margin-bottom: 30px;
        }}
        
        .stat-card {{
            background: white;
            border-radius: 12px;
            padding: 20px;
            text-align: center;
            box-shadow: 0 4px 6px rgba(0,0,0,0.1);
            transition: transform 0.2s;
        }}
        
        .stat-card:hover {{
            transform: translateY(-5px);
        }}
        
        .stat-value {{
            font-size: 48px;
            font-weight: bold;
            color: #667eea;
            margin: 10px 0;
        }}
        
        .stat-label {{
            color: #666;
            font-size: 14px;
            text-transform: uppercase;
            letter-spacing: 1px;
        }}
        
        .grade-badge {{
            display: inline-block;
            width: 40px;
            height: 40px;
            line-height: 40px;
            text-align: center;
            border-radius: 50%;
            font-weight: bold;
            font-size: 20px;
            color: white;
        }}
        
        .section {{
            background: white;
            border-radius: 12px;
            padding: 20px;
            margin-bottom: 20px;
            box-shadow: 0 4px 6px rgba(0,0,0,0.1);
        }}
        
        .section h2 {{
            color: #333;
            font-size: 20px;
            margin-bottom: 20px;
            padding-bottom: 10px;
            border-bottom: 2px solid #e0e0e0;
        }}
        
        .file-table {{
            width: 100%;
            border-collapse: collapse;
        }}
        
        .file-table th,
        .file-table td {{
            padding: 12px;
            text-align: left;
            border-bottom: 1px solid #e0e0e0;
        }}
        
        .file-table th {{
            background-color: #f8f9fa;
            font-weight: 600;
            color: #555;
        }}
        
        .file-table tr:hover {{
            background-color: #f8f9fa;
        }}
        
        .complexity-bar {{
            background-color: #e0e0e0;
            height: 8px;
            border-radius: 4px;
            overflow: hidden;
            width: 100px;
        }}
        
        .complexity-fill {{
            height: 100%;
            border-radius: 4px;
            transition: width 0.3s;
        }}
        
        .alert {{
            background-color: #fff3cd;
            border-left: 4px solid #ffc107;
            padding: 15px;
            margin-bottom: 20px;
            border-radius: 4px;
        }}
        
        .alert-critical {{
            background-color: #f8d7da;
            border-left-color: #dc3545;
        }}
        
        .block-list {{
            margin-top: 10px;
            margin-left: 20px;
        }}
        
        .block-item {{
            padding: 8px;
            margin: 5px 0;
            background-color: #f8f9fa;
            border-radius: 4px;
            font-family: 'Courier New', monospace;
            font-size: 13px;
        }}
        
        .complexity-number {{
            font-weight: bold;
            font-family: monospace;
        }}
        
        footer {{
            text-align: center;
            color: white;
            margin-top: 30px;
            font-size: 12px;
        }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>Reporte de Complejidad Ciclomática</h1>
            <div class="subtitle">OddsEngine - Análisis de calidad de código</div>
            <div class="subtitle">Generado: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</div>
        </div>
        
        <div class="stats-grid">
            <div class="stat-card">
                <div class="stat-label">Total de bloques analizados</div>
                <div class="stat-value">{total_blocks}</div>
            </div>
            <div class="stat-card">
                <div class="stat-label">Complejidad promedio</div>
                <div class="stat-value">{avg_total:.1f}</div>
                <div><span class="grade-badge" style="background-color: {avg_color}">{avg_grade}</span></div>
            </div>
            <div class="stat-card">
                <div class="stat-label">Funciones con alta complejidad</div>
                <div class="stat-value" style="color: {'#dc3545' if high_complexity_blocks else '#28a745'}">{len(high_complexity_blocks)}</div>
                <div class="stat-label">> 10 (requiere refactorización)</div>
            </div>
            <div class="stat-card">
                <div class="stat-label">Funciones críticas</div>
                <div class="stat-value" style="color: {'#dc3545' if critical_blocks else '#28a745'}">{len(critical_blocks)}</div>
                <div class="stat-label">> 20 (refactorización urgente)</div>
            </div>
        </div>
        
        {alert_section}
        {problem_functions_section}
        
        <div class="section">
            <h2>Resumen por Archivo</h2>
            <table class="file-table">
                <thead>
                    <tr>
                        <th>Archivo</th>
                        <th>Bloques</th>
                        <th>Complejidad Total</th>
                        <th>Promedio</th>
                        <th>Bloques Problemáticos</th>
                    </tr>
                </thead>
                <tbody>
                    {''.join(rows_html)}
                </tbody>
            </table>
            {files_table_footer}
        </div>
        
        <div class="section">
            <h2>Leyenda de Complejidad</h2>
            <table style="width: 100%;">
                <tr>
                    <td><span class="grade-badge" style="background-color: #28a745;">A</span></td>
                    <td><strong>1-5</strong></td>
                    <td>Bloque simple, bajo riesgo - Excelente</td>
                </tr>
                <tr>
                    <td><span class="grade-badge" style="background-color: #17a2b8;">B</span></td>
                    <td><strong>6-10</strong></td>
                    <td>Bloque simple y estable - Bueno</td>
                </tr>
                <tr>
                    <td><span class="grade-badge" style="background-color: #ffc107;">C</span></td>
                    <td><strong>11-20</strong></td>
                    <td>Bloque ligeramente complejo - Debe refactorizarse</td>
                </tr>
                <tr>
                    <td><span class="grade-badge" style="background-color: #fd7e14;">D</span></td>
                    <td><strong>21-30</strong></td>
                    <td>Bloque más complejo - Refactorización necesaria</td>
                </tr>
                <tr>
                    <td><span class="grade-badge" style="background-color: #dc3545;">E</span></td>
                    <td><strong>31-40</strong></td>
                    <td>Bloque complejo y alarmante - Alto riesgo</td>
                </tr>
                <tr>
                    <td><span class="grade-badge" style="background-color: #6c757d;">F</span></td>
                    <td><strong>41+</strong></td>
                    <td>Bloque muy complejo, propenso a errores - Riesgo extremo</td>
                </tr>
            </table>
        </div>
        
        <footer>
            Reporte generado automáticamente por radon | OddsEngine Analytics
        </footer>
    </div>
</body>
</html>"""
    
    # Guardar el archivo HTML
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(html_content)
    
    print(f" Reporte HTML generado: {output_path}")
    return len(high_complexity_blocks), len(critical_blocks)

def main():
    if len(sys.argv) < 2:
        print(" Uso: python radon_to_html.py <input_json> [output_html]")
        print("   Ejemplo: python radon_to_html.py complejidad_report.json reporte.html")
        sys.exit(1)
    
    input_json = sys.argv[1]
    output_html = sys.argv[2] if len(sys.argv) > 2 else 'complejidad_report.html'
    
    if not os.path.exists(input_json):
        print(f" Error: No se encuentra el archivo {input_json}")
        sys.exit(1)
    
    print(f"Leyendo JSON: {input_json}")
    json_data = parse_radon_json(input_json)
    
    print("Generando reporte HTML...")
    high_count, critical_count = generate_html_report(json_data, output_html)
    
    print(f"\nResumen:")
    print(f"   - Bloques con alta complejidad (>10): {high_count}")
    print(f"   - Bloques críticos (>20): {critical_count}")
    
    if high_count > 0:
        print(f"\n  Se encontraron {high_count} funciones que requieren refactorización")
        sys.exit(1)
    else:
        print(f"\nNo se encontraron problemas de complejidad")
        sys.exit(0)

if __name__ == "__main__":
    main()
