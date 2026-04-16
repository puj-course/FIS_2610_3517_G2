# Motor Probabilístico — OddsEngine

## Probabilidad Individual

### Fórmula
```
score = (0.40 × forma_reciente) + (0.30 × h2h_factor) + (0.30 × superficie_factor)
prob_A = score_A / (score_A + score_B) × 100
prob_B = 100 - prob_A
```

### Factores

| Factor | Peso | Descripción |
|--------|------|-------------|
| Forma reciente | 40% | Win rate de los últimos 10 partidos |
| Head-to-Head | 30% | Win rate en enfrentamientos directos |
| Superficie | 30% | Win rate en la superficie del torneo |

### Nivel de Confianza
- **Alta:** Datos completos (stats + H2H + superficie)
- **Media:** Sin H2H (primer enfrentamiento)
- **Baja:** Datos insuficientes → fallback 50/50

### Ejemplo 1: Alcaraz vs Sinner en Roland Garros (clay)

| Dato | Alcaraz | Sinner |
|------|---------|--------|
| Forma reciente | 80% | 80% |
| H2H | 5/9 = 55.6% | 4/9 = 44.4% |
| Clay win rate | 80.2% | 68.5% |

```
score_alcaraz = (0.40 × 80) + (0.30 × 55.6) + (0.30 × 80.2) = 32 + 16.68 + 24.06 = 72.74
score_sinner  = (0.40 × 80) + (0.30 × 44.4) + (0.30 × 68.5) = 32 + 13.32 + 20.55 = 65.87
prob_alcaraz  = 72.74 / (72.74 + 65.87) × 100 = 52.5%
prob_sinner   = 47.5%
Confianza: Alta
```

### Ejemplo 2: Zverev vs Ruud en Madrid Open (clay)

| Dato | Zverev | Ruud |
|------|--------|------|
| Forma reciente | 70% | 60% |
| H2H | 7/10 = 70% | 3/10 = 30% |
| Clay win rate | 65.3% | 72.8% |

```
score_zverev = (0.40 × 70) + (0.30 × 70) + (0.30 × 65.3) = 28 + 21 + 19.59 = 68.59
score_ruud   = (0.40 × 60) + (0.30 × 30) + (0.30 × 72.8) = 24 + 9 + 21.84 = 54.84
prob_zverev  = 68.59 / (68.59 + 54.84) × 100 = 55.6%
prob_ruud    = 44.4%
Confianza: Alta
```

## Probabilidad Combinada

### Fórmula
```
P_total = P1 × P2 × ... × Pn
(multiplicación de las probabilidades favoritas de cada partido)
```

### Clasificación de Riesgo
| Nivel | P_total | Mensaje |
|-------|---------|---------|
| Bajo | > 50% | "Combinada conservadora con buenas probabilidades" |
| Medio | 20-50% | "Combinada con riesgo moderado" |
| Alto | < 20% | "Combinada arriesgada, las probabilidades son bajas" |

### Ejemplo: Combinada de 3 partidos
- Partido 1: Alcaraz 52.5%
- Partido 2: Zverev 55.6%
- Partido 3: Djokovic 60.0%

```
P_total = 0.525 × 0.556 × 0.600 = 0.1752 = 17.5%
Riesgo: Alto (< 20%)
```

## Limitaciones
- Los datos son mock (ficticios pero coherentes)
- No considera lesiones, clima ni motivación
- H2H limitado a pares predefinidos
- La fórmula es simplificada (no usa ELO ni modelos ML)
