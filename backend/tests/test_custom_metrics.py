"""
Tests de las métricas de calidad personalizadas
================================================
test_cyclomatic_complexity.py  — Métrica 2: Complejidad Ciclomática
test_business_invariants.py    — Métrica 3: Invariantes de Lógica de Negocio

Ejecutar con:
    pytest backend/tests/test_custom_metrics.py -v
"""

import os
import sys
import textwrap
import pytest

# ── Hacer importable el paquete app ──────────────────────────────────────────
_BACKEND_DIR = os.path.join(os.path.dirname(__file__), "..")
if _BACKEND_DIR not in sys.path:
    sys.path.insert(0, _BACKEND_DIR)


# ═══════════════════════════════════════════════════════════════════════════════
#  MÉTRICA 2 — Complejidad Ciclomática
# ═══════════════════════════════════════════════════════════════════════════════

from app.metrics.cyclomatic_complexity import (
    _cc_from_ast,
    analyze_directory,
    CC_LIMIT_CRITICAL,
    CC_LIMIT_WARNING,
)


class TestCyclomaticComplexity:
    """Verifica el analizador de complejidad ciclomática."""

    def _parse(self, source: str) -> list:
        """Helper: parsea un fragmento de código y retorna lista de FunctionCC."""
        source = textwrap.dedent(source)
        return _cc_from_ast(source, "<test>")

    # ── CC base: función sin ramas ────────────────────────────────────────────
    def test_simple_function_cc_is_one(self):
        funcs = self._parse("""
            def simple():
                return 42
        """)
        assert len(funcs) == 1
        assert funcs[0].complexity == 1
        assert funcs[0].rank == "A"

    # ── Cada if agrega 1 ──────────────────────────────────────────────────────
    def test_single_if_adds_one(self):
        funcs = self._parse("""
            def with_if(x):
                if x > 0:
                    return x
                return -x
        """)
        assert funcs[0].complexity == 2

    # ── BoolOp: `a and b` agrega 1 (dos operandos → un conector) ─────────────
    def test_bool_op_adds_one(self):
        funcs = self._parse("""
            def check(a, b):
                if a and b:
                    return True
                return False
        """)
        # 1 (base) + 1 (if) + 1 (and) = 3
        assert funcs[0].complexity == 3

    # ── for + while ───────────────────────────────────────────────────────────
    def test_loops_add_complexity(self):
        funcs = self._parse("""
            def loopy(items):
                total = 0
                for item in items:
                    while item > 0:
                        total += 1
                        item -= 1
                return total
        """)
        # 1 + 1 (for) + 1 (while) = 3
        assert funcs[0].complexity == 3

    # ── Rank correcto ─────────────────────────────────────────────────────────
    def test_rank_b_for_complexity_six_to_ten(self):
        # Construir función con CC ~7 manualmente
        source = "def f(a,b,c,d,e,f_):\n"
        for i in range(6):
            source += f"    if a:\n        pass\n"
        funcs = _cc_from_ast(source, "<test>")
        assert funcs[0].rank == "B"

    # ── El propio directorio de la app no tiene funciones críticas ────────────
    def test_project_no_critical_functions(self):
        app_dir = os.path.join(os.path.dirname(__file__), "..", "app")
        if not os.path.isdir(app_dir):
            pytest.skip("Directorio app/ no encontrado")
        report = analyze_directory(app_dir)
        # Si hay funciones críticas, el test falla Y muestra cuáles son
        critical_names = [str(f) for f in report.critical]
        assert report.passed, (
            f"Funciones con CC > {CC_LIMIT_CRITICAL} encontradas:\n"
            + "\n".join(critical_names)
        )

    # ── El promedio CC del proyecto debe ser razonable ───────────────────────
    def test_project_average_cc_acceptable(self):
        app_dir = os.path.join(os.path.dirname(__file__), "..", "app")
        if not os.path.isdir(app_dir):
            pytest.skip("Directorio app/ no encontrado")
        report = analyze_directory(app_dir)
        assert report.average_cc <= CC_LIMIT_WARNING, (
            f"CC promedio {report.average_cc:.2f} supera el límite "
            f"aceptable de {CC_LIMIT_WARNING}"
        )


# ═══════════════════════════════════════════════════════════════════════════════
#  MÉTRICA 3 — Invariantes de Lógica de Negocio
# ═══════════════════════════════════════════════════════════════════════════════

from app.metrics.business_invariants import (
    check_complementary_probabilities,
    check_probability_range,
    check_risk_level_coherence,
    check_combination_monotonicity,
    check_weights_sum,
    run_all_invariants,
)
from app.services.probability_service import (
    WEIGHT_RECENT_FORM,
    WEIGHT_H2H,
    WEIGHT_SURFACE,
)


class TestBusinessInvariants:
    """Verifica que las invariantes detectan correctamente errores y aciertos."""

    # ── INV-01: Complementariedad ─────────────────────────────────────────────
    def test_inv01_passes_for_valid_sum(self):
        r = check_complementary_probabilities(62.5, 37.5)
        assert r.passed

    def test_inv01_passes_within_tolerance(self):
        # 62.6 + 37.5 = 100.1 — dentro de tolerancia 0.15
        r = check_complementary_probabilities(62.6, 37.5)
        assert r.passed

    def test_inv01_fails_for_bad_sum(self):
        # 70 + 40 = 110 — claramente incorrecto
        r = check_complementary_probabilities(70.0, 40.0)
        assert not r.passed

    # ── INV-02: Rango ─────────────────────────────────────────────────────────
    def test_inv02_passes_for_valid_prob(self):
        assert check_probability_range(0.0).passed
        assert check_probability_range(100.0).passed
        assert check_probability_range(55.3).passed

    def test_inv02_fails_for_negative(self):
        assert not check_probability_range(-1.0).passed

    def test_inv02_fails_for_over_100(self):
        assert not check_probability_range(100.1).passed

    # ── INV-03: Coherencia del riesgo ─────────────────────────────────────────
    def test_inv03_low_risk_correct(self):
        r = check_risk_level_coherence(75.0, "low")
        assert r.passed

    def test_inv03_medium_risk_correct(self):
        r = check_risk_level_coherence(35.0, "medium")
        assert r.passed

    def test_inv03_high_risk_correct(self):
        r = check_risk_level_coherence(10.0, "high")
        assert r.passed

    def test_inv03_fails_when_risk_mismatched(self):
        # 10% de prob clasificada como "low" es incorrecto
        r = check_risk_level_coherence(10.0, "low")
        assert not r.passed

    def test_inv03_boundary_exactly_50(self):
        # prob = 50 → medium (50 no supera 50, así que no es low)
        r = check_risk_level_coherence(50.0, "medium")
        assert r.passed

    # ── INV-04: Monotonicidad ─────────────────────────────────────────────────
    def test_inv04_combination_le_minimum(self):
        # 62.5 * 52.0 / 100 ≈ 32.5%
        r = check_combination_monotonicity(32.5, [62.5, 52.0])
        assert r.passed

    def test_inv04_fails_when_combination_exceeds_min(self):
        # Combinada 80% con individuales de 62.5 y 52.0 es imposible
        r = check_combination_monotonicity(80.0, [62.5, 52.0])
        assert not r.passed

    def test_inv04_passes_empty_list(self):
        r = check_combination_monotonicity(0.0, [])
        assert r.passed

    # ── INV-05: Suma de pesos ─────────────────────────────────────────────────
    def test_inv05_model_weights_sum_to_one(self):
        """El modelo de probability_service debe tener pesos que sumen 1."""
        r = check_weights_sum(
            [WEIGHT_RECENT_FORM, WEIGHT_H2H, WEIGHT_SURFACE],
            ["RECENT_FORM", "H2H", "SURFACE"],
        )
        assert r.passed, (
            f"Los pesos no suman 1.0: "
            f"{WEIGHT_RECENT_FORM} + {WEIGHT_H2H} + {WEIGHT_SURFACE} = "
            f"{WEIGHT_RECENT_FORM + WEIGHT_H2H + WEIGHT_SURFACE}"
        )

    def test_inv05_fails_for_wrong_weights(self):
        r = check_weights_sum([0.5, 0.3, 0.3])   # suma = 1.1
        assert not r.passed

    # ── run_all_invariants: integración ──────────────────────────────────────
    def test_run_all_passes_with_valid_data(self):
        report = run_all_invariants(
            individual_results=[
                {"match_id": "m1", "home_prob": 62.5, "away_prob": 37.5,
                 "home_name": "A", "away_name": "B"},
            ],
            combination_results=[
                {"total_probability": 35.0, "risk_level": "medium",
                 "individual_probs": [62.5]},
            ],
            model_weights=[WEIGHT_RECENT_FORM, WEIGHT_H2H, WEIGHT_SURFACE],
            weight_names=["RECENT_FORM", "H2H", "SURFACE"],
        )
        assert report.passed, "\n" + report.summary()

    def test_run_all_captures_failure(self):
        report = run_all_invariants(
            individual_results=[
                {"match_id": "m_bad", "home_prob": 70.0, "away_prob": 70.0,
                 "home_name": "X", "away_name": "Y"},
            ],
        )
        assert not report.passed
        assert len(report.failures) >= 1
        # La invariante de complementariedad debe estar en los fallos
        ids = [f.invariant_id for f in report.failures]
        assert "INV-01" in ids
