"""
Tests unitarios para app/core/security.py

Cubre: hash_password, verify_password, create_access_token,
decode_access_token, get_current_user.
"""

import pytest
from datetime import timedelta
from unittest.mock import patch, MagicMock

from app.core.security import (
    hash_password,
    verify_password,
    create_access_token,
    decode_access_token,
    get_current_user,
)


class TestHashPassword:

    def test_returns_string(self):
        result = hash_password("mypassword")
        assert isinstance(result, str)
        assert result != "mypassword"

    def test_different_hash_each_time(self):
        h1 = hash_password("samepassword")
        h2 = hash_password("samepassword")
        assert h1 != h2


class TestVerifyPassword:

    def test_correct_password(self):
        hashed = hash_password("secret123")
        assert verify_password("secret123", hashed) is True

    def test_incorrect_password(self):
        hashed = hash_password("secret123")
        assert verify_password("wrongpassword", hashed) is False


class TestCreateAccessToken:

    def test_returns_string(self):
        token = create_access_token(data={"sub": "user_123"})
        assert isinstance(token, str)
        assert len(token) > 0

    def test_custom_expiry(self):
        token = create_access_token(
            data={"sub": "user_123"},
            expires_delta=timedelta(minutes=5),
        )
        payload = decode_access_token(token)
        assert payload is not None
        assert payload["sub"] == "user_123"

    def test_payload_contains_sub(self):
        token = create_access_token(data={"sub": "user_abc"})
        payload = decode_access_token(token)
        assert payload["sub"] == "user_abc"

    def test_payload_contains_exp(self):
        token = create_access_token(data={"sub": "user_123"})
        payload = decode_access_token(token)
        assert "exp" in payload


class TestDecodeAccessToken:

    def test_valid_token(self):
        token = create_access_token(data={"sub": "user_xyz", "role": "admin"})
        payload = decode_access_token(token)
        assert payload is not None
        assert payload["sub"] == "user_xyz"
        assert payload["role"] == "admin"

    def test_invalid_token(self):
        result = decode_access_token("invalid.token.string")
        assert result is None

    def test_tampered_token(self):
        token = create_access_token(data={"sub": "user_123"})
        tampered = token[:-5] + "XXXXX"
        result = decode_access_token(tampered)
        assert result is None

    def test_expired_token(self):
        token = create_access_token(
            data={"sub": "user_123"},
            expires_delta=timedelta(seconds=-1),
        )
        result = decode_access_token(token)
        assert result is None


class TestGetCurrentUser:

    @pytest.mark.anyio
    async def test_valid_token(self):
        from app.services.auth_service import get_auth_service

        service = get_auth_service()
        user = service.register_user("secuser", "sec@test.com", "password123")

        token = create_access_token(data={"sub": user["id"]})
        credentials = MagicMock()
        credentials.credentials = token

        result = await get_current_user(credentials)
        assert result["id"] == user["id"]
        assert result["username"] == "secuser"

    @pytest.mark.anyio
    async def test_invalid_token_raises_401(self):
        from fastapi import HTTPException

        credentials = MagicMock()
        credentials.credentials = "bad.token.here"

        with pytest.raises(HTTPException) as exc_info:
            await get_current_user(credentials)
        assert exc_info.value.status_code == 401

    @pytest.mark.anyio
    async def test_token_without_sub_raises_401(self):
        from fastapi import HTTPException

        token = create_access_token(data={"role": "admin"})
        credentials = MagicMock()
        credentials.credentials = token

        with pytest.raises(HTTPException) as exc_info:
            await get_current_user(credentials)
        assert exc_info.value.status_code == 401

    @pytest.mark.anyio
    async def test_user_not_found_raises_401(self):
        from fastapi import HTTPException

        token = create_access_token(data={"sub": "nonexistent_user_id"})
        credentials = MagicMock()
        credentials.credentials = token

        with pytest.raises(HTTPException) as exc_info:
            await get_current_user(credentials)
        assert exc_info.value.status_code == 401

    @pytest.mark.anyio
    async def test_inactive_user_raises_403(self):
        from fastapi import HTTPException
        from app.services.auth_service import get_auth_service

        service = get_auth_service()
        user = service.register_user("inactive", "inactive@test.com", "pass123456")

        service._users[service._email_index["inactive@test.com"]]["is_active"] = False

        token = create_access_token(data={"sub": user["id"]})
        credentials = MagicMock()
        credentials.credentials = token

        with pytest.raises(HTTPException) as exc_info:
            await get_current_user(credentials)
        assert exc_info.value.status_code == 403
