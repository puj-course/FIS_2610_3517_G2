"""
Rutas de autenticación.

Endpoints:
    POST /api/auth/register  — Registrar nuevo usuario
    POST /api/auth/login     — Iniciar sesión (obtener JWT)
    GET  /api/auth/me        — Obtener usuario actual (requiere token)
"""

import logging
from typing import Annotated

from fastapi import APIRouter, Depends

from app.models.user import UserCreate, UserLogin, UserResponse, TokenResponse
from app.services.auth_service import get_auth_service
from app.core.security import create_access_token, get_current_user
from app.core.exceptions import ValidationException

logger = logging.getLogger("oddsengine")

router = APIRouter(prefix="/auth", tags=["autenticación"])


@router.post("/register", response_model=TokenResponse, status_code=201)
async def register(data: UserCreate):
    """
    Registra un nuevo usuario y retorna un JWT.

    Validaciones:
    - Email no duplicado
    - Username no duplicado
    - Password mínimo 6 caracteres (validado por Pydantic)
    """
    service = get_auth_service()
    user = service.register_user(
        username=data.username,
        email=data.email,
        password=data.password,
    )

    token = create_access_token(data={"sub": user["id"]})
    logger.info("POST /auth/register — usuario registrado")

    return TokenResponse(
        access_token=token,
        user=UserResponse(**user),
    )


@router.post("/login", response_model=TokenResponse)
async def login(data: UserLogin):
    """
    Inicia sesión y retorna un JWT.

    Retorna 401 si las credenciales son inválidas.
    """
    service = get_auth_service()
    user = service.authenticate_user(email=data.email, password=data.password)

    if user is None:
        raise ValidationException(message="Email o contraseña incorrectos")

    token = create_access_token(data={"sub": user["id"]})
    logger.info("POST /auth/login — login exitoso")

    return TokenResponse(
        access_token=token,
        user=UserResponse(**user),
    )


@router.get("/me", response_model=UserResponse)
async def get_me(current_user: Annotated[dict, Depends(get_current_user)]):
    """
    Retorna los datos del usuario autenticado.

    Requiere token Bearer en el header Authorization.
    """
    logger.info("GET /auth/me — consulta de usuario autenticado")
    return UserResponse(**current_user)
