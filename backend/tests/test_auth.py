"""
Tests de autenticación — registro, login y protección de rutas.
"""

import pytest
from httpx import AsyncClient


# --- Helpers ---

async def register_user(client: AsyncClient, username="testuser", email="test@example.com", password="secret123") -> dict:
    """Helper para registrar un usuario y retornar la respuesta."""
    response = await client.post("/api/auth/register", json={
        "username": username,
        "email": email,
        "password": password,
    })
    return response


async def login_user(client: AsyncClient, email="test@example.com", password="secret123") -> dict:
    """Helper para hacer login y retornar la respuesta."""
    response = await client.post("/api/auth/login", json={
        "email": email,
        "password": password,
    })
    return response


# --- Tests de registro ---

@pytest.mark.anyio
async def test_register_success(client: AsyncClient):
    """Registro exitoso retorna 201 con token y datos del usuario."""
    response = await register_user(client)
    assert response.status_code == 201
    data = response.json()
    assert "access_token" in data
    assert data["token_type"] == "bearer"
    assert data["user"]["username"] == "testuser"
    assert data["user"]["email"] == "test@example.com"
    assert data["user"]["is_active"] is True
    assert "id" in data["user"]
    assert "created_at" in data["user"]


@pytest.mark.anyio
async def test_register_duplicate_email(client: AsyncClient):
    """Registrar con email duplicado retorna 409."""
    await register_user(client, username="user1", email="dup@test.com")
    response = await register_user(client, username="user2", email="dup@test.com")
    assert response.status_code == 409
    data = response.json()
    assert data["error"]["type"] == "DuplicateException"


@pytest.mark.anyio
async def test_register_duplicate_username(client: AsyncClient):
    """Registrar con username duplicado retorna 409."""
    await register_user(client, username="sameuser", email="a@test.com")
    response = await register_user(client, username="sameuser", email="b@test.com")
    assert response.status_code == 409


@pytest.mark.anyio
async def test_register_short_password(client: AsyncClient):
    """Contraseña menor a 6 caracteres retorna 422."""
    response = await client.post("/api/auth/register", json={
        "username": "testuser",
        "email": "test@example.com",
        "password": "abc",
    })
    assert response.status_code == 422


@pytest.mark.anyio
async def test_register_invalid_email(client: AsyncClient):
    """Email inválido retorna 422."""
    response = await client.post("/api/auth/register", json={
        "username": "testuser",
        "email": "not-an-email",
        "password": "secret123",
    })
    assert response.status_code == 422


# --- Tests de login ---

@pytest.mark.anyio
async def test_login_success(client: AsyncClient):
    """Login exitoso retorna 200 con token y datos del usuario."""
    await register_user(client)
    response = await login_user(client)
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert data["token_type"] == "bearer"
    assert data["user"]["email"] == "test@example.com"


@pytest.mark.anyio
async def test_login_wrong_password(client: AsyncClient):
    """Login con contraseña incorrecta retorna 422."""
    await register_user(client)
    response = await login_user(client, password="wrongpassword")
    assert response.status_code == 422
    data = response.json()
    assert "error" in data


@pytest.mark.anyio
async def test_login_nonexistent_email(client: AsyncClient):
    """Login con email no registrado retorna 422."""
    response = await login_user(client, email="noexist@test.com")
    assert response.status_code == 422


# --- Tests de /me ---

@pytest.mark.anyio
async def test_me_with_valid_token(client: AsyncClient):
    """GET /auth/me con token válido retorna datos del usuario."""
    reg_response = await register_user(client)
    token = reg_response.json()["access_token"]

    response = await client.get("/api/auth/me", headers={
        "Authorization": f"Bearer {token}",
    })
    assert response.status_code == 200
    data = response.json()
    assert data["username"] == "testuser"
    assert data["email"] == "test@example.com"
    assert data["is_active"] is True


@pytest.mark.anyio
async def test_me_without_token(client: AsyncClient):
    """GET /auth/me sin token retorna 403."""
    response = await client.get("/api/auth/me")
    assert response.status_code == 403


@pytest.mark.anyio
async def test_me_with_invalid_token(client: AsyncClient):
    """GET /auth/me con token inválido retorna 401."""
    response = await client.get("/api/auth/me", headers={
        "Authorization": "Bearer invalid.token.here",
    })
    assert response.status_code == 401


# --- Tests de flujo completo ---

@pytest.mark.anyio
async def test_register_then_login_then_me(client: AsyncClient):
    """Flujo completo: registro → login → obtener perfil."""
    # Registrar
    reg = await register_user(client, username="flowuser", email="flow@test.com", password="mypassword")
    assert reg.status_code == 201

    # Login
    login = await login_user(client, email="flow@test.com", password="mypassword")
    assert login.status_code == 200
    token = login.json()["access_token"]

    # Me
    me = await client.get("/api/auth/me", headers={
        "Authorization": f"Bearer {token}",
    })
    assert me.status_code == 200
    assert me.json()["username"] == "flowuser"
    assert me.json()["email"] == "flow@test.com"


@pytest.mark.anyio
async def test_existing_routes_still_work(client: AsyncClient):
    """Las rutas existentes siguen funcionando sin autenticación."""
    # Health
    r = await client.get("/health")
    assert r.status_code == 200

    # Matches
    r = await client.get("/api/matches")
    assert r.status_code == 200
    assert isinstance(r.json(), list)

    # Match by ID
    r = await client.get("/api/matches/match_001")
    assert r.status_code == 200
