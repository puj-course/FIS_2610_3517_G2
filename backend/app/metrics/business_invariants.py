"""
Métrica de calidad #3: Validación de Invariantes de Lógica de Negocio
=====================================================================
Verifica que las salidas del motor probabilístico de OddsEngine cumplan
con propiedades matemáticas y de negocio que DEBEN ser siempre verdaderas,
independientemente de los datos de entrada.

Estas invariantes NO son verificadas por SonarQube porque:
  - No son problemas de sintaxis ni código duplicado.
  - Dependen de la semántica del dominio (apuestas deportivas).
  - Requieren razonar sobre valores en tiempo de ejecución.

Invariantes implementadas
──────────────────────────
  INV-01  Complementariedad de probabilidades:
              P(local) + P(visitante) = 100.0  (±0.1 por redondeo)
          Una probabilidad que no sea complementaria implica que el motor
          está asignando más o menos del 100% del espacio probabilístico,
          lo que haría que las cuotas generadas sean arbitrajistas.

  INV-02  Rango de probabilidad individual:
              0.0 ≤ P ≤ 100.0  para cada jugador
          Una probabilidad fuera de rango carece de interpretación
          como frecuencia relativa y rompería la UI (barras de progreso,
          badges de color).

  INV-03  Coherencia del nivel de riesgo combinado:
              prob > 50  → RiskLevel.LOW
              20 < prob ≤ 50  → RiskLevel.MEDIUM
              prob ≤ 20  → RiskLevel.HIGH
          Si el riesgo asignado no corresponde al umbral, la comunicación
          al usuario es incorrecta (le diría "riesgo bajo" a una combinada
          con sólo 10% de probabilidad de éxito).

  INV-04  Monotonicidad de la probabilidad combinada:
              P(combinada) ≤ min(P(partidos individuales))
          La probabilidad de que ocurran N eventos independientes nunca
          puede ser mayor que la del evento menos probable. Viola la regla
          de multiplicación de probabilidades si no se cumple.

  INV-05  Pesos del modelo suman 1:
              WEIGHT_RECENT_FORM + WEIGHT_H2H + WEIGHT_SURFACE = 1.0
          Si los pesos no suman 1, el score ponderado no equivale a una
          media ponderada real, produciendo probabilidades incorrectas.

Cómo interpretar los resultados:
  - PASS: El motor es matemáticamente coherente para los datos probados.
  - FAIL: Existe al menos un caso donde el motor produce una salida
          inválida; se debe corregir la función señalada antes de
          desplegar en producción, ya que las cuotas mostradas al
          usuario serían incorrectas.

Acciones de mejora si alguna invariante falla:
  INV-01/02: Revisar la función _calculate_score y normalizar el resultado
             con max(0, min(100, value)) antes de retornarlo.
  INV-03:    Asegurarse de usar CombinationProbability.classify_risk()
             consistentemente y no hardcodear el nivel en ningún otro lugar.
  INV-04:    Cambiar la lógica de calculate_combination para que use
             total_prob *= (prob / 100) en lugar de cualquier suma.
  INV-05:    Agregar un test unitario o assert al importar el módulo que
             verifique sum([WEIGHT_RECENT_FORM, WEIGHT_H2H, WEIGHT_SURFACE]) == 1.
"""

from __future__ import annotations

import math
from dataclasses import dataclass, field
from typing import Any

# Tolerancia para comparaciones de punto flotante
_FLOAT_TOL = 0.15   # ±0.15 por redondeo en probabilidades porcentuales

# Umbrales de clasificación de riesgo (deben coincidir con CombinationProbability)
_RISK_THRESHOLDS = {
    "low":    (50.0, 100.0),
    "medium": (20.0, 50.0),
    "high":   (0.0,  20.0),
}


# ── Resultado de una invariante ───────────────────────────────────────────────

@dataclass
class InvariantResult:
    invariant_id: str
    description: str
    passed: bool
    expected: Any
    actual: Any
    context: dict = field(default_factory=dict)
    fix_hint: str = ""

    def __str__(self) -> str:
        status = "✅ PASS" if self.passed else "❌ FAIL"
        msg = f"[{self.invariant_id}] {status} — {self.description}"
        if not self.passed:
            msg += f"\n    Esperado : {self.expected}"
            msg += f"\n    Obtenido : {self.actual}"
            msg += f"\n    Contexto : {self.context}"
            msg += f"\n    Corrección: {self.fix_hint}"
        return msg


@dataclass
class InvariantReport:
    results: list[InvariantResult] = field(default_factory=list)

    @property
    def passed(self) -> bool:
        return all(r.passed for r in self.results)

    @property
    def failures(self) -> list[InvariantResult]:
        return [r for r in self.results if not r.passed]

    def summary(self) -> str:
        total   = len(self.results)
        passing = sum(1 for r in self.results if r.passed)
        lines = [
            "── Invariantes de Lógica de Negocio ─────────────────────────────",
            f"  Invariantes evaluadas: {total}",
            f"  Pasadas: {passing}/{total}",
            f"  Estado : {'✅ PASS' if self.passed else '❌ FAIL'}",
            "",
        ]
        for r in self.results:
            lines.append(f"  {r}")
        return "\n".join(lines)


# ── Verificadores individuales ────────────────────────────────────────────────

def check_complementary_probabilities(
    home_prob: float,
    away_prob: float,
    context: dict | None = None,
) -> InvariantResult:
    """INV-01: Las dos probabilidades de un partido deben sumar 100."""
    total = home_prob + away_prob
    passed = abs(total - 100.0) <= _FLOAT_TOL
    return InvariantResult(
        invariant_id="INV-01",
        description="P(local) + P(visitante) = 100.0",
        passed=passed,
        expected=f"100.0 ± {_FLOAT_TOL}",
        actual=round(total, 3),
        context=context or {},
        fix_hint=(
            "En _calculate_score, asegurar away_prob = round(100 - home_prob, 1) "
            "en lugar de calcularla de forma independiente."
        ),
    )


def check_probability_range(
    probability: float,
    player_label: str = "jugador",
) -> InvariantResult:
    """INV-02: Toda probabilidad debe estar en [0, 100]."""
    passed = 0.0 <= probability <= 100.0
    return InvariantResult(
        invariant_id="INV-02",
        description=f"0 ≤ P({player_label}) ≤ 100",
        passed=passed,
        expected="[0.0, 100.0]",
        actual=probability,
        context={"player": player_label},
        fix_hint=(
            "Aplicar max(0.0, min(100.0, value)) al retornar cualquier "
            "probabilidad calculada en _calculate_score."
        ),
    )


def check_risk_level_coherence(
    total_probability: float,
    risk_level: str,
) -> InvariantResult:
    """INV-03: El nivel de riesgo debe corresponder al umbral definido."""
    expected_risk = None
    for level, (lo, hi) in _RISK_THRESHOLDS.items():
        if lo < total_probability <= hi or (level == "high" and total_probability <= hi):
            expected_risk = level
            break
    # Caso borde: probabilidad exactamente 0
    if total_probability == 0.0:
        expected_risk = "high"

    passed = risk_level == expected_risk
    return InvariantResult(
        invariant_id="INV-03",
        description="Nivel de riesgo coherente con probabilidad combinada",
        passed=passed,
        expected=f"risk='{expected_risk}' para prob={total_probability}%",
        actual=f"risk='{risk_level}'",
        context={"total_probability": total_probability},
        fix_hint=(
            "Usar siempre CombinationProbability.classify_risk(total_prob_pct) "
            "para asignar el nivel; no hardcodear ni recalcular en otro lugar."
        ),
    )


def check_combination_monotonicity(
    combination_prob: float,
    individual_probs: list[float],
) -> InvariantResult:
    """INV-04: P(combinada) ≤ min(P individuales)."""
    if not individual_probs:
        return InvariantResult(
            invariant_id="INV-04",
            description="P(combinada) ≤ min(P individuales)",
            passed=True,
            expected="sin partidos",
            actual="sin partidos",
        )
    min_individual = min(individual_probs)
    # Permitir tolerancia de punto flotante
    passed = combination_prob <= min_individual + _FLOAT_TOL
    return InvariantResult(
        invariant_id="INV-04",
        description="P(combinada) ≤ min(P individuales)",
        passed=passed,
        expected=f"≤ {min_individual}",
        actual=combination_prob,
        context={
            "individual_probs": individual_probs,
            "min_individual": min_individual,
        },
        fix_hint=(
            "Verificar que calculate_combination usa multiplicación de "
            "probabilidades: total_prob *= (prob / 100) y NO suma ni promedio."
        ),
    )


def check_weights_sum(
    weights: list[float],
    weight_names: list[str] | None = None,
) -> InvariantResult:
    """INV-05: Los pesos del modelo ponderado deben sumar exactamente 1.0."""
    total = sum(weights)
    passed = abs(total - 1.0) <= 1e-9
    names = weight_names or [f"w{i}" for i in range(len(weights))]
    return InvariantResult(
        invariant_id="INV-05",
        description="Suma de pesos del modelo = 1.0",
        passed=passed,
        expected=1.0,
        actual=round(total, 10),
        context=dict(zip(names, weights)),
        fix_hint=(
            "Ajustar las constantes WEIGHT_* en probability_service.py para "
            "que WEIGHT_RECENT_FORM + WEIGHT_H2H + WEIGHT_SURFACE = 1.0 exacto."
        ),
    )


# ── Función de conveniencia: verificar todo de una vez ────────────────────────

def run_all_invariants(
    individual_results: list[dict] | None = None,
    combination_results: list[dict] | None = None,
    model_weights: list[float] | None = None,
    weight_names: list[str] | None = None,
) -> InvariantReport:
    """
    Ejecuta todas las invariantes con los datos proporcionados.

    Args:
        individual_results: Lista de dicts con claves:
            'home_prob', 'away_prob', 'home_name', 'away_name'
        combination_results: Lista de dicts con claves:
            'total_probability', 'risk_level', 'individual_probs'
        model_weights: Lista de pesos del modelo de probabilidad.
        weight_names:  Nombres de los pesos (para el reporte).

    Returns:
        InvariantReport con todos los resultados.
    """
    report = InvariantReport()

    # INV-01 e INV-02 — por cada resultado individual
    for r in (individual_results or []):
        home_prob = r.get("home_prob", 0.0)
        away_prob = r.get("away_prob", 0.0)
        ctx = {
            "match_id": r.get("match_id", "?"),
            "home": r.get("home_name", "local"),
            "away": r.get("away_name", "visitante"),
        }
        report.results.append(
            check_complementary_probabilities(home_prob, away_prob, ctx)
        )
        report.results.append(check_probability_range(home_prob, ctx["home"]))
        report.results.append(check_probability_range(away_prob, ctx["away"]))

    # INV-03 e INV-04 — por cada resultado combinado
    for c in (combination_results or []):
        report.results.append(
            check_risk_level_coherence(
                c.get("total_probability", 0.0),
                c.get("risk_level", ""),
            )
        )
        report.results.append(
            check_combination_monotonicity(
                c.get("total_probability", 0.0),
                c.get("individual_probs", []),
            )
        )

    # INV-05 — pesos del modelo
    if model_weights is not None:
        report.results.append(check_weights_sum(model_weights, weight_names))

    return report


# ── Punto de entrada: smoke test con datos de ejemplo ─────────────────────────

if __name__ == "__main__":
    from app.services.probability_service import (
        WEIGHT_RECENT_FORM,
        WEIGHT_H2H,
        WEIGHT_SURFACE,
    )

    sample_individual = [
        {"match_id": "m001", "home_prob": 62.5, "away_prob": 37.5,
         "home_name": "Djokovic", "away_name": "Alcaraz"},
        {"match_id": "m002", "home_prob": 48.0, "away_prob": 52.0,
         "home_name": "Sinner", "away_name": "Medvedev"},
    ]

    sample_combination = [
        {
            "total_probability": 32.5,
            "risk_level": "medium",
            "individual_probs": [62.5, 52.0],
        },
        {
            "total_probability": 8.0,
            "risk_level": "high",
            "individual_probs": [62.5, 52.0, 24.5],
        },
    ]

    report = run_all_invariants(
        individual_results=sample_individual,
        combination_results=sample_combination,
        model_weights=[WEIGHT_RECENT_FORM, WEIGHT_H2H, WEIGHT_SURFACE],
        weight_names=["WEIGHT_RECENT_FORM", "WEIGHT_H2H", "WEIGHT_SURFACE"],
    )

    print(report.summary())
    exit(0 if report.passed else 1)
