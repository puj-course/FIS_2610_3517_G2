"""
Métrica de calidad #2: Complejidad Ciclomática
===============================================
Mide cuántos caminos independientes de ejecución existen en cada función
del código fuente del backend. Se basa en la teoría de grafos de McCabe (1976):

    CC = E - N + 2P

donde E = aristas, N = nodos, P = componentes conexos.

En la práctica, CC equivale al número de puntos de decisión (if, elif,
for, while, and, or, except, case) + 1 por función.

Umbrales de referencia (según el estándar de McCabe):
    1 – 5  → Baja complejidad. Código simple y fácil de probar.
    6 – 10 → Complejidad moderada. Requiere atención.
    11–15  → Complejidad alta. Difícil de mantener y testear.
    > 15   → Muy alta. Debe ser refactorizada urgentemente.

Interpretación del resultado:
    Una función con CC = 7 tiene 7 caminos independientes, lo que implica
    que se necesitan al menos 7 casos de prueba para alcanzar cobertura
    de ramas completa. Valores altos correlacionan directamente con mayor
    probabilidad de defectos y mayor costo de mantenimiento.
"""

import ast
import os
import sys
from dataclasses import dataclass
from typing import Optional

# Intentar usar radon si está disponible; si no, usar contador AST propio.
try:
    from radon.complexity import cc_visit, ComplexityVisitor
    from radon.metrics import mi_visit
    _RADON_AVAILABLE = True
except ImportError:
    _RADON_AVAILABLE = False


# ── Umbrales ──────────────────────────────────────────────────────────────────

CC_THRESHOLDS = {
    "low":       (1, 5),
    "moderate":  (6, 10),
    "high":      (11, 15),
    "very_high": (16, float("inf")),
}

CC_LIMIT_WARNING  = 10   # Alerta si alguna función supera este valor
CC_LIMIT_CRITICAL = 15   # Falla si alguna función supera este valor


# ── Resultados ────────────────────────────────────────────────────────────────

@dataclass
class FunctionCC:
    """Complejidad ciclomática de una función o método."""
    file: str
    name: str
    lineno: int
    complexity: int
    rank: str          # A=1-5, B=6-10, C=11-15, D=16-20, E/F=21+

    def grade(self) -> str:
        """Devuelve el nivel en lenguaje natural."""
        if self.complexity <= 5:
            return "low"
        elif self.complexity <= 10:
            return "moderate"
        elif self.complexity <= 15:
            return "high"
        return "very_high"

    def __str__(self) -> str:
        return (
            f"[{self.rank}] {self.file}:{self.lineno} "
            f"{self.name} → CC={self.complexity} ({self.grade()})"
        )


@dataclass
class CCReport:
    """Reporte agregado de complejidad ciclomática de un módulo o directorio."""
    total_functions: int
    average_cc: float
    max_cc: int
    functions: list
    warnings: list        # Funciones con CC > CC_LIMIT_WARNING
    critical: list        # Funciones con CC > CC_LIMIT_CRITICAL
    passed: bool          # True si ninguna función supera CC_LIMIT_CRITICAL

    def summary(self) -> str:
        lines = [
            "── Complejidad Ciclomática ──────────────────────────────────────",
            f"  Funciones analizadas : {self.total_functions}",
            f"  Promedio CC          : {self.average_cc:.2f}",
            f"  Máximo CC            : {self.max_cc}",
            f"  Advertencias (>{CC_LIMIT_WARNING})  : {len(self.warnings)}",
            f"  Críticas (>{CC_LIMIT_CRITICAL})      : {len(self.critical)}",
            f"  Estado               : {'✅ PASS' if self.passed else '❌ FAIL'}",
        ]
        if self.warnings:
            lines.append("\n  Funciones con alta complejidad:")
            for f in sorted(self.warnings, key=lambda x: -x.complexity):
                lines.append(f"    {f}")
        return "\n".join(lines)


# ── Analizador AST de respaldo (sin radon) ────────────────────────────────────

class _ASTComplexityVisitor(ast.NodeVisitor):
    """
    Contador de complejidad ciclomática basado en el AST de Python.
    Cuenta cada punto de decisión como +1 al CC base de 1.
    """
    _DECISION_NODES = (
        ast.If, ast.For, ast.While, ast.ExceptHandler,
        ast.With, ast.Assert, ast.comprehension,
    )

    def __init__(self):
        self.complexity = 1  # base

    def visit_If(self, node):
        self.complexity += 1
        self.generic_visit(node)

    def visit_For(self, node):
        self.complexity += 1
        self.generic_visit(node)

    def visit_While(self, node):
        self.complexity += 1
        self.generic_visit(node)

    def visit_ExceptHandler(self, node):
        self.complexity += 1
        self.generic_visit(node)

    def visit_BoolOp(self, node):
        # cada `and` / `or` agrega un camino
        self.complexity += len(node.values) - 1
        self.generic_visit(node)

    def visit_comprehension(self, node):
        self.complexity += 1
        self.generic_visit(node)

    def visit_Assert(self, node):
        self.complexity += 1
        self.generic_visit(node)


def _cc_from_ast(source: str, filename: str) -> list:
    """Calcula CC para todas las funciones/métodos en un archivo."""
    try:
        tree = ast.parse(source, filename=filename)
    except SyntaxError:
        return []

    results = []

    for node in ast.walk(tree):
        if not isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            continue

        visitor = _ASTComplexityVisitor()
        visitor.visit(node)
        cc = visitor.complexity

        # Rank al estilo radon
        if cc <= 5:
            rank = "A"
        elif cc <= 10:
            rank = "B"
        elif cc <= 15:
            rank = "C"
        elif cc <= 20:
            rank = "D"
        elif cc <= 25:
            rank = "E"
        else:
            rank = "F"

        results.append(FunctionCC(
            file=filename,
            name=node.name,
            lineno=node.lineno,
            complexity=cc,
            rank=rank,
        ))

    return results


# ── Analizador principal ──────────────────────────────────────────────────────

def analyze_file(filepath: str) -> list:
    """Retorna lista de FunctionCC para un archivo .py."""
    with open(filepath, "r", encoding="utf-8", errors="ignore") as f:
        source = f.read()

    if _RADON_AVAILABLE:
        results = []
        for block in cc_visit(source):
            results.append(FunctionCC(
                file=filepath,
                name=block.name,
                lineno=block.lineno,
                complexity=block.complexity,
                rank=block.rank,
            ))
        return results
    else:
        return _cc_from_ast(source, filepath)


def analyze_directory(directory: str, exclude: Optional[list] = None) -> CCReport:
    """
    Analiza recursivamente todos los archivos .py en `directory` y
    devuelve un CCReport agregado.

    Args:
        directory: Ruta al directorio raíz del código fuente.
        exclude:   Lista de nombres de directorio a omitir (ej. ["tests"]).
    """
    exclude = exclude or ["tests", "__pycache__", ".git"]
    all_functions: list[FunctionCC] = []

    for root, dirs, files in os.walk(directory):
        # Excluir directorios indicados
        dirs[:] = [d for d in dirs if d not in exclude]

        for fname in files:
            if not fname.endswith(".py"):
                continue
            filepath = os.path.join(root, fname)
            all_functions.extend(analyze_file(filepath))

    if not all_functions:
        return CCReport(
            total_functions=0,
            average_cc=0.0,
            max_cc=0,
            functions=[],
            warnings=[],
            critical=[],
            passed=True,
        )

    complexities = [f.complexity for f in all_functions]
    avg_cc = sum(complexities) / len(complexities)
    max_cc = max(complexities)

    warnings  = [f for f in all_functions if f.complexity > CC_LIMIT_WARNING]
    critical  = [f for f in all_functions if f.complexity > CC_LIMIT_CRITICAL]

    return CCReport(
        total_functions=len(all_functions),
        average_cc=round(avg_cc, 2),
        max_cc=max_cc,
        functions=all_functions,
        warnings=warnings,
        critical=critical,
        passed=len(critical) == 0,
    )


# ── Punto de entrada CLI ──────────────────────────────────────────────────────

if __name__ == "__main__":
    target = sys.argv[1] if len(sys.argv) > 1 else "."
    report = analyze_directory(target)
    print(report.summary())
    sys.exit(0 if report.passed else 1)
