from prometheus_fastapi_instrumentator import Instrumentator
from fastapi import FastAPI


def setup_metrics(app: FastAPI):
    """Configura métricas con la configuración por defecto"""
    # La versión más simple posible
    Instrumentator().instrument(app).expose(app, endpoint="/metrics")
