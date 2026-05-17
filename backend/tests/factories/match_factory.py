"""
Factory para crear objetos MatchDB de prueba con datos completos.
"""

from datetime import datetime, timedelta
from typing import Optional, Dict, Any
from faker import Faker

from app.models.db_models import MatchDB

# Inicializar Faker para datos realistas
fake = Faker()


class MatchFactory:
    """
    Factory para crear instancias de MatchDB con datos válidos.
    
    Ejemplo de uso:
        # Crear un match con datos aleatorios pero válidos
        match = MatchFactory.create()
        
        # Crear un match con datos específicos
        match = MatchFactory.create(
            id="custom_id",
            status="finished",
            tournament_surface="clay"
        )
        
        # Crear múltiples matches
        matches = MatchFactory.create_batch(5)
    """
    
    # Valores por defecto para todos los campos obligatorios
    DEFAULTS = {
        "id": lambda: f"match_{fake.uuid4()[:8]}",
        "player_home_id": lambda: f"player_{fake.random_int(1, 100)}",
        "player_home_name": lambda: fake.name(),
        "player_home_country": lambda: fake.country_code(),
        "player_home_ranking": lambda: fake.random_int(1, 500),
        "player_away_id": lambda: f"player_{fake.random_int(1, 100)}",
        "player_away_name": lambda: fake.name(),
        "player_away_country": lambda: fake.country_code(),
        "player_away_ranking": lambda: fake.random_int(1, 500),
        "tournament_id": lambda: f"tournament_{fake.random_int(1, 50)}",
        "tournament_name": lambda: fake.random_element(elements=[
            "Wimbledon", "Roland Garros", "US Open", "Australian Open",
            "Madrid Open", "Rome Masters", "Indian Wells", "Miami Open"
        ]),
        "tournament_surface": lambda: fake.random_element(elements=[
            "hard", "clay", "grass", "carpet"
        ]),
        "tournament_category": lambda: fake.random_element(elements=[
            "Grand Slam", "ATP 1000", "ATP 500", "ATP 250"
        ]),
        "tournament_location": lambda: fake.city(),
        "date": lambda: datetime.now() - timedelta(days=fake.random_int(-30, 30)),
        "status": lambda: fake.random_element(elements=[
            "upcoming", "live", "finished", "cancelled"
        ]),
        "score": lambda: fake.random_element(elements=[
            None,
            "6-4, 6-3",
            "7-6, 6-2",
            "6-3, 7-5",
            "6-0, 6-1"
        ]),
    }
    
    @classmethod
    def create(cls, **kwargs) -> MatchDB:
        """
        Crear un MatchDB con datos por defecto + sobrescrituras.
        
        Args:
            **kwargs: Valores específicos para sobrescribir los defaults.
            
        Returns:
            MatchDB: Instancia lista para usar en pruebas.
        """
        # Generar los valores por defecto
        data = {}
        for field, value_factory in cls.DEFAULTS.items():
            if field not in kwargs:
                data[field] = value_factory() if callable(value_factory) else value_factory
            else:
                data[field] = kwargs[field]
        
        # Si hay valores en kwargs que no están en DEFAULTS, también los añadimos
        for key, value in kwargs.items():
            if key not in data:
                data[key] = value
        
        return MatchDB(**data)
    
    @classmethod
    def create_batch(cls, count: int, **kwargs) -> list[MatchDB]:
        """
        Crear múltiples MatchDB.
        
        Args:
            count: Número de instancias a crear.
            **kwargs: Valores comunes para todos los matches.
            
        Returns:
            list[MatchDB]: Lista de instancias.
        """
        return [cls.create(**kwargs) for _ in range(count)]
    
    @classmethod
    def create_with_fixed_date(cls, date: datetime, **kwargs) -> MatchDB:
        """Crear match con fecha específica."""
        return cls.create(date=date, **kwargs)
    
    @classmethod
    def create_with_status(cls, status: str, **kwargs) -> MatchDB:
        """Crear match con estado específico."""
        return cls.create(status=status, **kwargs)
    
    @classmethod
    def create_with_surface(cls, surface: str, **kwargs) -> MatchDB:
        """Crear match con superficie específica."""
        return cls.create(tournament_surface=surface, **kwargs)
    
    @classmethod
    def create_upcoming_match(cls, **kwargs) -> MatchDB:
        """Crear match upcoming."""
        return cls.create(
            status="upcoming",
            date=datetime.now() + timedelta(days=fake.random_int(1, 7)),
            **kwargs
        )
    
    @classmethod
    def create_finished_match(cls, **kwargs) -> MatchDB:
        """Crear match finished con score."""
        return cls.create(
            status="finished",
            date=datetime.now() - timedelta(days=fake.random_int(1, 30)),
            score=fake.random_element(elements=["6-4, 6-3", "7-6, 6-2", "6-3, 7-5"]),
            **kwargs
        )
    
    @classmethod
    def create_minimal_match(cls, **kwargs) -> MatchDB:
        """
        Crear match con SOLO campos obligatorios.
        Útil para probar manejo de valores None.
        """
        return cls.create(
            player_home_name=None,
            player_home_country=None,
            player_home_ranking=None,
            player_away_name=None,
            player_away_country=None,
            player_away_ranking=None,
            tournament_name=None,
            tournament_surface=None,
            tournament_category=None,
            tournament_location=None,
            score=None,
            **kwargs
        )
