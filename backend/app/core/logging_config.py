"""
Configuración centralizada de logging para OddsEngine.

Usa el módulo estándar de Python (logging) para mantener simplicidad.
Los logs se escriben a consola con formato legible y a archivo para persistencia.
"""

import logging
import sys
from pathlib import Path


def setup_logging(log_level: str = "INFO", log_file: str = "oddsengine.log") -> None:
    """
    Configura el sistema de logging del proyecto.

    Args:
        log_level: Nivel mínimo de log (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        log_file: Nombre del archivo de log
    """
    # Formato para consola (legible)
    console_format = logging.Formatter(
        fmt="%(asctime)s | %(levelname)-8s | %(name)s | %(message)s",
        datefmt="%H:%M:%S",
    )

    # Formato para archivo (más detallado)
    file_format = logging.Formatter(
        fmt="%(asctime)s | %(levelname)-8s | %(name)s | %(filename)s:%(lineno)d | %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )

    # Handler de consola
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(console_format)

    # Handler de archivo
    log_path = Path("logs")
    log_path.mkdir(exist_ok=True)
    file_handler = logging.FileHandler(log_path / log_file, encoding="utf-8")
    file_handler.setFormatter(file_format)

    # Logger principal del proyecto
    logger = logging.getLogger("oddsengine")
    logger.setLevel(getattr(logging, log_level.upper(), logging.INFO))
    logger.addHandler(console_handler)
    logger.addHandler(file_handler)

    # Reducir ruido de librerías externas
    logging.getLogger("uvicorn.access").setLevel(logging.WARNING)
    logging.getLogger("httpx").setLevel(logging.WARNING)

    logger.info(f"Logging configurado — nivel: {log_level}")
