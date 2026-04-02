"""
Manejadores globales de excepciones para FastAPI.

Captura todas las excepciones del dominio (OddsEngineException y subclases)
y las convierte en respuestas HTTP consistentes con formato JSON estandarizado.
"""

import logging
from datetime import datetime

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError

from app.core.exceptions import (
    OddsEngineException,
    ExternalAPIException,
    APITimeoutException,
    NotFoundException,
)

logger = logging.getLogger("oddsengine")


def create_error_response(status_code: int, message: str, error_type: str, details: dict = None) -> dict:
    """Crea una respuesta de error con formato estandarizado."""
    response = {
        "error": {
            "type": error_type,
            "message": message,
            "status_code": status_code,
            "timestamp": datetime.now().isoformat(),
        }
    }
    if details:
        response["error"]["details"] = details
    return response


def register_error_handlers(app: FastAPI) -> None:
    """Registra todos los handlers de excepciones en la app FastAPI."""

    @app.exception_handler(OddsEngineException)
    async def oddsengine_exception_handler(request: Request, exc: OddsEngineException):
        """Maneja todas las excepciones del dominio OddsEngine."""
        logger.error(
            f"OddsEngineException: {exc.message} | "
            f"Status: {exc.status_code} | "
            f"Path: {request.url.path} | "
            f"Method: {request.method}"
        )
        return JSONResponse(
            status_code=exc.status_code,
            content=create_error_response(
                status_code=exc.status_code,
                message=exc.message,
                error_type=type(exc).__name__,
            ),
        )

    @app.exception_handler(ExternalAPIException)
    async def external_api_exception_handler(request: Request, exc: ExternalAPIException):
        """Maneja errores de comunicación con APIs externas."""
        logger.error(
            f"ExternalAPIException: {exc.message} | "
            f"Source: {exc.source} | "
            f"Path: {request.url.path}"
        )
        return JSONResponse(
            status_code=exc.status_code,
            content=create_error_response(
                status_code=exc.status_code,
                message="No se pudo obtener información del proveedor externo. Intente nuevamente.",
                error_type="ExternalAPIException",
                details={"source": exc.source},
            ),
        )

    @app.exception_handler(APITimeoutException)
    async def api_timeout_exception_handler(request: Request, exc: APITimeoutException):
        """Maneja timeouts de APIs externas."""
        logger.warning(
            f"APITimeoutException: {exc.message} | "
            f"Source: {exc.source} | "
            f"Path: {request.url.path}"
        )
        return JSONResponse(
            status_code=exc.status_code,
            content=create_error_response(
                status_code=exc.status_code,
                message="El servicio externo tardó demasiado en responder. Intente nuevamente.",
                error_type="APITimeoutException",
                details={"source": exc.source},
            ),
        )

    @app.exception_handler(RequestValidationError)
    async def validation_exception_handler(request: Request, exc: RequestValidationError):
        """Maneja errores de validación de FastAPI/Pydantic."""
        logger.warning(
            f"ValidationError: {exc.errors()} | "
            f"Path: {request.url.path}"
        )
        return JSONResponse(
            status_code=422,
            content=create_error_response(
                status_code=422,
                message="Los datos enviados no son válidos.",
                error_type="ValidationError",
                details={"errors": exc.errors()},
            ),
        )

    @app.exception_handler(Exception)
    async def generic_exception_handler(request: Request, exc: Exception):
        """Captura cualquier excepción no manejada para evitar fallos críticos."""
        logger.critical(
            f"Unhandled Exception: {type(exc).__name__}: {str(exc)} | "
            f"Path: {request.url.path} | "
            f"Method: {request.method}",
            exc_info=True,
        )
        return JSONResponse(
            status_code=500,
            content=create_error_response(
                status_code=500,
                message="Ocurrió un error interno. El equipo ha sido notificado.",
                error_type="InternalServerError",
            ),
        )
