"""
Módulo de seguridad — hashing de contraseñas y gestión de JWT.

Funciones:
    hash_password       — Hashear contraseña con bcrypt
    verify_password     — Verificar contraseña contra hash
    create_access_token — Generar JWT con expiración configurable
    decode_access_token — Decodificar y validar JWT
    get_current_user    — Dependencia FastAPI para extraer usuario del token
"""

import logging
from datetime import datetime, timedelta, timezone
from typing import Annotated, Optional

from jose import JWTError, jwt
from passlib.context import CryptContext
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

from app.core.config import get_settings

logger = logging.getLogger("oddsengine")

# Contexto de hashing con bcrypt
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# Esquema de autenticación Bearer
bearer_scheme = HTTPBearer()


def hash_password(password: str) -> str:
    """Hashea una contraseña en texto plano con bcrypt."""
    return pwd_context.hash(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verifica una contraseña en texto plano contra su hash."""
    return pwd_context.verify(plain_password, hashed_password)


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    """
    Genera un JWT firmado con los datos proporcionados.

    Args:
        data: Payload del token (debe incluir 'sub' con el user_id)
        expires_delta: Tiempo de expiración personalizado
    """
    settings = get_settings()
    to_encode = data.copy()

    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(minutes=settings.jwt_expire_minutes)

    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(
        to_encode,
        settings.jwt_secret_key,
        algorithm=settings.jwt_algorithm,
    )
    return encoded_jwt


def decode_access_token(token: str) -> Optional[dict]:
    """
    Decodifica y valida un JWT.

    Retorna el payload si es válido, None si no lo es.
    """
    settings = get_settings()
    try:
        payload = jwt.decode(
            token,
            settings.jwt_secret_key,
            algorithms=[settings.jwt_algorithm],
        )
        return payload
    except JWTError:
        return None


def get_current_user(
    credentials: Annotated[HTTPAuthorizationCredentials, Depends(bearer_scheme)],
):
    """
    Dependencia de FastAPI — extrae y valida el usuario del token Bearer.

    Uso en endpoints:
        @router.get("/me")
        async def me(user = Depends(get_current_user)):
            return user
    """
    token = credentials.credentials
    payload = decode_access_token(token)

    if payload is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token inválido o expirado",
            headers={"WWW-Authenticate": "Bearer"},
        )

    user_id = payload.get("sub")
    if user_id is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token no contiene identificador de usuario",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # Obtener usuario del servicio
    from app.services.auth_service import get_auth_service
    auth_service = get_auth_service()
    user = auth_service.get_user_by_id(user_id)

    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Usuario no encontrado",
            headers={"WWW-Authenticate": "Bearer"},
        )

    if not user["is_active"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Usuario desactivado",
        )

    return user
