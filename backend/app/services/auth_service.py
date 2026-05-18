"""
Servicio de autenticación — registro y login de usuarios.

Usa almacenamiento en memoria (dict) para mantener consistencia
con el patrón del proyecto (InMemoryStorage para combinadas).
Diseñado para ser reemplazado por PostgreSQL cuando sea necesario.
"""

import logging
from datetime import datetime, timezone
from typing import Optional
from uuid import uuid4

from app.core.security import hash_password, verify_password
from app.core.exceptions import DuplicateException, ValidationException

logger = logging.getLogger("oddsengine")


class AuthService:
    """Servicio de autenticación con almacenamiento en memoria."""

    def __init__(self):
        self._users: dict[str, dict] = {}
        self._email_index: dict[str, str] = {}  # email -> user_id

    def register_user(self, username: str, email: str, password: str) -> dict:
        """
        Registra un nuevo usuario.

        Validaciones:
        - Email no debe estar duplicado
        - Username no debe estar duplicado

        Retorna el dict del usuario creado (sin hashed_password).
        """
        # Validar email duplicado
        email_lower = email.lower()
        if email_lower in self._email_index:
            raise DuplicateException(
                message=f"El email '{email}' ya está registrado"
            )

        # Validar username duplicado
        for user in self._users.values():
            if user["username"].lower() == username.lower():
                raise DuplicateException(
                    message=f"El username '{username}' ya está en uso"
                )

        # Crear usuario
        user_id = f"user_{uuid4().hex[:12]}"
        user = {
            "id": user_id,
            "username": username,
            "email": email_lower,
            "hashed_password": hash_password(password),
            "created_at": datetime.now(timezone.utc),
            "is_active": True,
        }

        self._users[user_id] = user
        self._email_index[email_lower] = user_id

        logger.info("Usuario registrado correctamente")
        return self._to_public(user)

    def authenticate_user(self, email: str, password: str) -> Optional[dict]:
        """
        Autentica un usuario con email y contraseña.

        Retorna el dict público del usuario si las credenciales son válidas,
        None si no lo son.
        """
        email_lower = email.lower()
        user_id = self._email_index.get(email_lower)
        if user_id is None:
            return None

        user = self._users.get(user_id)
        if user is None:
            return None

        if not verify_password(password, user["hashed_password"]):
            return None

        logger.info("Login exitoso")
        return self._to_public(user)

    def get_user_by_email(self, email: str) -> Optional[dict]:
        """Obtiene un usuario por su email (datos públicos)."""
        email_lower = email.lower()
        user_id = self._email_index.get(email_lower)
        if user_id is None:
            return None
        return self._to_public(self._users[user_id])

    def get_user_by_id(self, user_id: str) -> Optional[dict]:
        """Obtiene un usuario por su ID (datos públicos)."""
        user = self._users.get(user_id)
        if user is None:
            return None
        return self._to_public(user)

    def _to_public(self, user: dict) -> dict:
        """Retorna datos públicos del usuario (sin hashed_password)."""
        return {
            "id": user["id"],
            "username": user["username"],
            "email": user["email"],
            "is_active": user["is_active"],
            "created_at": user["created_at"],
        }

    def clear(self) -> None:
        """Limpia todos los usuarios. Usar solo en tests."""
        self._users.clear()
        self._email_index.clear()


# Singleton
_auth_service: Optional[AuthService] = None


def get_auth_service() -> AuthService:
    global _auth_service
    if _auth_service is None:
        _auth_service = AuthService()
    return _auth_service


def reset_auth_service() -> None:
    """Resetea el servicio de auth. Usar solo en tests."""
    global _auth_service
    _auth_service = AuthService()
