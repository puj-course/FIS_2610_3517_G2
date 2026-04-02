"""
Excepciones personalizadas de OddsEngine.

Cada excepción representa un tipo de error específico del dominio,
permitiendo manejo granular en los handlers globales.
"""


class OddsEngineException(Exception):
    """Excepción base del proyecto."""

    def __init__(self, message: str = "Error interno del sistema", status_code: int = 500):
        self.message = message
        self.status_code = status_code
        super().__init__(self.message)


class ExternalAPIException(OddsEngineException):
    """Error al comunicarse con una API externa (tenis, stats, etc.)."""

    def __init__(self, message: str = "Error al consultar la API externa", source: str = "unknown"):
        self.source = source
        super().__init__(message=message, status_code=502)


class APITimeoutException(OddsEngineException):
    """Timeout al consultar una API externa."""

    def __init__(self, message: str = "La API externa no respondió a tiempo", source: str = "unknown"):
        self.source = source
        super().__init__(message=message, status_code=504)


class NotFoundException(OddsEngineException):
    """Recurso no encontrado."""

    def __init__(self, resource: str = "recurso", resource_id: str = ""):
        message = f"{resource} '{resource_id}' no encontrado" if resource_id else f"{resource} no encontrado"
        self.resource = resource
        self.resource_id = resource_id
        super().__init__(message=message, status_code=404)


class ValidationException(OddsEngineException):
    """Error de validación de datos de entrada."""

    def __init__(self, message: str = "Datos de entrada inválidos"):
        super().__init__(message=message, status_code=422)


class DuplicateException(OddsEngineException):
    """Intento de agregar un recurso duplicado."""

    def __init__(self, message: str = "El recurso ya existe"):
        super().__init__(message=message, status_code=409)
