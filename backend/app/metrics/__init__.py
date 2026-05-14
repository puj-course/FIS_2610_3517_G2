"""
Módulo de métricas de calidad — OddsEngine
==========================================
Exporta las métricas implementadas directamente en código:

  Métrica 1 (latencia)          → app/main.py  (middleware log_requests)
  Métrica 2 (CC)                → metrics/cyclomatic_complexity.py
  Métrica 3 (invariantes)       → metrics/business_invariants.py
"""

from .cyclomatic_complexity import analyze_directory, CCReport
from .business_invariants import run_all_invariants, InvariantReport

__all__ = [
    "analyze_directory",
    "CCReport",
    "run_all_invariants",
    "InvariantReport",
]
