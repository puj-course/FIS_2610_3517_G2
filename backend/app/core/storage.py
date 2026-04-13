"""
Almacenamiento en memoria para la sesión activa.

Proporciona persistencia temporal para combinadas de apuestas.
Los datos se pierden al reiniciar el servidor.

Diseñado para ser reemplazado por una base de datos (Oracle, SQLite, etc.)
cuando el alcance del proyecto lo permita.
"""

from typing import Optional

from app.models.combination import Combination


class InMemoryStorage:
    """Almacén en memoria usando diccionarios de Python."""

    def __init__(self):
        self._combinations: dict[str, Combination] = {}

    def save_combination(self, combination: Combination) -> Combination:
        """Guarda o actualiza una combinada."""
        self._combinations[combination.id] = combination
        return combination

    def get_combination(self, combination_id: str) -> Optional[Combination]:
        """Obtiene una combinada por su ID."""
        return self._combinations.get(combination_id)

    def delete_combination(self, combination_id: str) -> bool:
        """Elimina una combinada. Retorna True si existía."""
        if combination_id in self._combinations:
            del self._combinations[combination_id]
            return True
        return False

    def list_combinations(self) -> list[Combination]:
        """Lista todas las combinadas activas."""
        return list(self._combinations.values())

    def clear(self) -> None:
        """Limpia todo el almacenamiento. Útil para tests."""
        self._combinations.clear()


# Singleton global
_storage: Optional[InMemoryStorage] = None


def get_storage() -> InMemoryStorage:
    """Obtiene la instancia global del almacenamiento."""
    global _storage
    if _storage is None:
        _storage = InMemoryStorage()
    return _storage


def reset_storage() -> None:
    """Resetea el almacenamiento. Usar solo en tests."""
    global _storage
    _storage = InMemoryStorage()
