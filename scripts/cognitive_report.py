import os
import ast
import json
from cognitive_complexity.api import get_cognitive_complexity

reporte = []


for root, _, files in os.walk('backend/'):
    for file in files:
        if file.endswith('.py'):
            path = os.path.join(root, file)
            with open(path, 'r', encoding='utf-8') as f:
                try:
                    tree = ast.parse(f.read())
                    for node in ast.walk(tree):
                        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                            score = get_cognitive_complexity(node)
                            reporte.append({
                                'file': path,
                                'function': node.name,
                                'complexity': score
                            })
                except Exception:
                    pass


with open('cognitive_report.json', 'w', encoding='utf-8') as json_file:
    json.dump(reporte, json_file, indent=4, ensure_ascii=False)
