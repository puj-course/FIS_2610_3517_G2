"""
Modelos Pydantic para autenticación y gestión de usuarios.

Esquemas:
    UserCreate      — Datos para registrar un nuevo usuario
    UserLogin       — Datos para iniciar sesión
    UserResponse    — Datos públicos del usuario (sin contraseña)
    TokenResponse   — Token JWT retornado tras login/registro
"""

from pydantic import BaseModel, Field, EmailStr
from datetime import datetime
from typing import Optional


class UserCreate(BaseModel):
    """Datos requeridos para registrar un nuevo usuario."""
    username: str = Field(min_length=3, max_length=50, description="Nombre de usuario")
    email: EmailStr = Field(description="Email del usuario")
    password: str = Field(min_length=6, max_length=128, description="Contraseña")


class UserLogin(BaseModel):
    """Datos requeridos para iniciar sesión."""
    email: EmailStr = Field(description="Email del usuario")
    password: str = Field(description="Contraseña")


class UserResponse(BaseModel):
    """Datos públicos del usuario (sin contraseña)."""
    id: str
    username: str
    email: str
    is_active: bool = True
    created_at: datetime


class TokenResponse(BaseModel):
    """Token JWT retornado tras login o registro exitoso."""
    access_token: str
    token_type: str = "bearer"
    user: UserResponse
