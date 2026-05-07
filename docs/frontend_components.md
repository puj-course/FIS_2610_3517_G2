# Componentes Frontend — OddsEngine

## Árbol de Componentes

```
App
├── ErrorBoundary
├── NotificationProvider
│   └── CombinationProvider
│       └── Layout
│           ├── Navbar + ThemeToggle
│           ├── Routes
│           │   ├── Home
│           │   │   ├── MatchList
│           │   │   │   ├── MatchCard + ProbabilityBadge
│           │   │   │   └── SkeletonCard
│           │   │   └── CombinationPanel
│           │   │       ├── CombinationSummary + RiskIndicator
│           │   │       └── SelectionCard
│           │   ├── MatchDetail
│           │   │   └── Tabs
│           │   │       ├── StatsComparison + FormRecent
│           │   │       ├── HeadToHead
│           │   │       └── ProbabilityBreakdown
│           │   ├── CombinationPage
│           │   ├── CombinationResult
│           │   │   ├── ResultCard
│           │   │   ├── RiskIndicator
│           │   │   └── ProbabilityChart
│           │   ├── History
│           │   │   └── HistoryCard
│           │   └── NotFound
│           ├── Notification
│           └── ConfirmDialog
```

## Componentes (25 total)

| Componente | Props | Descripción |
|------------|-------|-------------|
| MatchCard | match | Tarjeta de partido con jugadores, torneo, estado, probabilidad |
| MatchList | — | Lista con grid, skeleton, filtros. Usa useMatches |
| CombinationPanel | — | Panel lateral: crear, ver selecciones, eliminar |
| SelectionCard | selection, onRemove | Partido seleccionado en combinada |
| Navbar | — | Logo, links, ThemeToggle |
| Layout | children | Wrapper con Navbar y footer |
| Tabs | tabs, defaultTab | Pestañas genéricas reutilizables |
| StatsComparison | playerHomeStats, playerAwayStats, surface | Barras comparativas |
| HeadToHead | headToHead | Score H2H y lista de encuentros |
| ProbabilityBadge | probability, playerName, loading | Badge % con color |
| ProbabilityBreakdown | probability | Desglose de factores y confianza |
| RiskIndicator | level, message | Indicador bajo/medio/alto |
| CombinationSummary | combinationId, selectionsCount | Prob total y barra |
| ResultCard | probability, selectionsCount | Porcentaje grande |
| ProbabilityChart | matches | Barras por partido |
| FormRecent | form, playerName | Píldoras W/L y racha |
| HistoryCard | combination | Card con badge y resultado |
| EmptyState | icon, title, message, action, onAction | Estado vacío |
| ErrorBoundary | children | Captura errores de render |
| ErrorMessage | message, onRetry | Mensaje de error |
| Notification | — | Toast notifications |
| SkeletonCard | — | Placeholder animado |
| ConfirmDialog | isOpen, title, message, onConfirm, onCancel | Modal confirmación |
| ThemeToggle | — | Switch claro/oscuro |
| NotFound | — | Página 404 |

## Hooks (4)

| Hook | Retorna | Descripción |
|------|---------|-------------|
| useMatches | { matches, loading, error, filterByStatus } | Fetch partidos con filtros |
| useMatchStats | { stats, loading, error } | Fetch estadísticas de un partido |
| useMatchProbability | { probability, loading, error } | Fetch probabilidad individual |
| useCombinationResult | { result, loading, error, refresh } | Fetch resultado combinada |

## Contextos (2)

| Contexto | Estado | Funciones |
|----------|--------|-----------|
| CombinationContext | combination, loading | create, addMatch, removeMatch, delete, isMatchInCombination |
| NotificationContext | notifications | showSuccess, showError, showInfo, dismiss |
