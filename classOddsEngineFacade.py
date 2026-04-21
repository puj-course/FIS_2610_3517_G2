class OddsEngineFacade:
    def __init__(self, stats_service, probability_service, combination_service):
        self._stats = stats_service
        self._prob = probability_service
        self._combo = combination_service

    def get_combination_result(self, combination_id: str):
        # 1. Obtener la combinada
        combination = self._combo.get(combination_id)

        results = []

        # 2. Procesar cada partido de la combinada
        for match in combination.matches:
            # Obtener estadísticas
            stats = self._stats.get_stats(match.match_id)

            # Calcular probabilidad
            probability = self._prob.calculate(stats, match.h2h)

            results.append({
                "match_id": match.match_id,
                "probability": probability
            })

        # 3. Retornar resultado final
        return {
            "combination_id": combination_id,
            "results": results
        }