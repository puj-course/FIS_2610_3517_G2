"""
Tests unitarios para app/services/auth_service.py

Cubre: register_user, authenticate_user, get_user_by_email,
get_user_by_id, clear.
"""

import pytest

from app.services.auth_service import AuthService
from app.core.exceptions import DuplicateException


@pytest.fixture
def auth_service():
    """Instancia fresca de AuthService para cada test."""
    return AuthService()


class TestRegisterUser:

    def test_success(self, auth_service):
        user = auth_service.register_user("alice", "alice@test.com", "secret123")
        assert user["username"] == "alice"
        assert user["email"] == "alice@test.com"
        assert user["is_active"] is True
        assert "id" in user
        assert "created_at" in user
        assert "hashed_password" not in user

    def test_duplicate_email_raises(self, auth_service):
        auth_service.register_user("user1", "dup@test.com", "pass123456")
        with pytest.raises(DuplicateException):
            auth_service.register_user("user2", "dup@test.com", "pass123456")

    def test_duplicate_email_case_insensitive(self, auth_service):
        auth_service.register_user("user1", "Test@Example.COM", "pass123456")
        with pytest.raises(DuplicateException):
            auth_service.register_user("user2", "test@example.com", "pass123456")

    def test_duplicate_username_raises(self, auth_service):
        auth_service.register_user("sameuser", "a@test.com", "pass123456")
        with pytest.raises(DuplicateException):
            auth_service.register_user("sameuser", "b@test.com", "pass123456")

    def test_duplicate_username_case_insensitive(self, auth_service):
        auth_service.register_user("Alice", "a@test.com", "pass123456")
        with pytest.raises(DuplicateException):
            auth_service.register_user("alice", "b@test.com", "pass123456")

    def test_multiple_users(self, auth_service):
        u1 = auth_service.register_user("user1", "u1@test.com", "pass123456")
        u2 = auth_service.register_user("user2", "u2@test.com", "pass123456")
        assert u1["id"] != u2["id"]


class TestAuthenticateUser:

    def test_success(self, auth_service):
        auth_service.register_user("bob", "bob@test.com", "mypassword")
        result = auth_service.authenticate_user("bob@test.com", "mypassword")
        assert result is not None
        assert result["username"] == "bob"
        assert result["email"] == "bob@test.com"
        assert "hashed_password" not in result

    def test_wrong_password(self, auth_service):
        auth_service.register_user("bob", "bob@test.com", "mypassword")
        result = auth_service.authenticate_user("bob@test.com", "wrongpass")
        assert result is None

    def test_nonexistent_email(self, auth_service):
        result = auth_service.authenticate_user("nobody@test.com", "anypass")
        assert result is None

    def test_email_case_insensitive(self, auth_service):
        auth_service.register_user("bob", "Bob@Test.COM", "mypassword")
        result = auth_service.authenticate_user("bob@test.com", "mypassword")
        assert result is not None
        assert result["username"] == "bob"


class TestGetUserByEmail:

    def test_found(self, auth_service):
        auth_service.register_user("carol", "carol@test.com", "pass123456")
        user = auth_service.get_user_by_email("carol@test.com")
        assert user is not None
        assert user["username"] == "carol"
        assert "hashed_password" not in user

    def test_not_found(self, auth_service):
        result = auth_service.get_user_by_email("noone@test.com")
        assert result is None

    def test_case_insensitive(self, auth_service):
        auth_service.register_user("carol", "Carol@Test.COM", "pass123456")
        user = auth_service.get_user_by_email("carol@test.com")
        assert user is not None


class TestGetUserById:

    def test_found(self, auth_service):
        registered = auth_service.register_user("dave", "dave@test.com", "pass123456")
        user = auth_service.get_user_by_id(registered["id"])
        assert user is not None
        assert user["username"] == "dave"
        assert "hashed_password" not in user

    def test_not_found(self, auth_service):
        result = auth_service.get_user_by_id("user_nonexistent")
        assert result is None


class TestClear:

    def test_removes_all_users(self, auth_service):
        auth_service.register_user("u1", "u1@test.com", "pass123456")
        auth_service.register_user("u2", "u2@test.com", "pass123456")
        auth_service.clear()
        assert auth_service.get_user_by_email("u1@test.com") is None
        assert auth_service.get_user_by_email("u2@test.com") is None

    def test_allows_reregistration_after_clear(self, auth_service):
        auth_service.register_user("u1", "u1@test.com", "pass123456")
        auth_service.clear()
        user = auth_service.register_user("u1", "u1@test.com", "pass123456")
        assert user["username"] == "u1"
