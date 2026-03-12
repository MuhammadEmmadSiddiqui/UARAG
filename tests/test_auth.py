"""Tests for authentication endpoints."""
import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_register_user(test_client: AsyncClient):
    """Test user registration."""
    response = await test_client.post(
        "/auth/register",
        json={
            "username": "newuser",
            "email": "newuser@example.com",
            "password": "newpassword123"
        }
    )
    assert response.status_code == 201
    data = response.json()
    assert data["username"] == "newuser"
    assert data["email"] == "newuser@example.com"
    assert "id" in data
    assert "created_at" in data


@pytest.mark.asyncio
async def test_register_duplicate_username(test_client: AsyncClient, test_user):
    """Test registration with duplicate username."""
    response = await test_client.post(
        "/auth/register",
        json={
            "username": "testuser",
            "email": "another@example.com",
            "password": "password123"
        }
    )
    assert response.status_code == 400
    assert "already registered" in response.json()["detail"].lower()


@pytest.mark.asyncio
async def test_register_duplicate_email(test_client: AsyncClient, test_user):
    """Test registration with duplicate email."""
    response = await test_client.post(
        "/auth/register",
        json={
            "username": "anotheruser",
            "email": "test@example.com",
            "password": "password123"
        }
    )
    assert response.status_code == 400
    assert "already registered" in response.json()["detail"].lower()


@pytest.mark.asyncio
async def test_register_invalid_email(test_client: AsyncClient):
    """Test registration with invalid email."""
    response = await test_client.post(
        "/auth/register",
        json={
            "username": "newuser",
            "email": "invalid-email",
            "password": "password123"
        }
    )
    assert response.status_code == 422  # Validation error


@pytest.mark.asyncio
async def test_register_short_password(test_client: AsyncClient):
    """Test registration with short password."""
    response = await test_client.post(
        "/auth/register",
        json={
            "username": "newuser",
            "email": "newuser@example.com",
            "password": "short"
        }
    )
    assert response.status_code == 422  # Validation error


@pytest.mark.asyncio
async def test_login_success(test_client: AsyncClient, test_user):
    """Test successful login."""
    response = await test_client.post(
        "/auth/token",
        data={
            "username": "testuser",
            "password": "testpassword123"
        }
    )
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert data["token_type"] == "bearer"


@pytest.mark.asyncio
async def test_login_wrong_password(test_client: AsyncClient, test_user):
    """Test login with wrong password."""
    response = await test_client.post(
        "/auth/token",
        data={
            "username": "testuser",
            "password": "wrongpassword"
        }
    )
    assert response.status_code == 401
    assert "incorrect" in response.json()["detail"].lower()


@pytest.mark.asyncio
async def test_login_nonexistent_user(test_client: AsyncClient):
    """Test login with nonexistent user."""
    response = await test_client.post(
        "/auth/token",
        data={
            "username": "nonexistent",
            "password": "password123"
        }
    )
    assert response.status_code == 401
    assert "incorrect" in response.json()["detail"].lower()


@pytest.mark.asyncio
async def test_access_protected_endpoint_without_token(test_client: AsyncClient):
    """Test accessing protected endpoint without token."""
    response = await test_client.get("/chat/history")
    assert response.status_code == 401


@pytest.mark.asyncio
async def test_access_protected_endpoint_with_invalid_token(test_client: AsyncClient):
    """Test accessing protected endpoint with invalid token."""
    test_client.headers = {"Authorization": "Bearer invalid_token"}
    response = await test_client.get("/chat/history")
    assert response.status_code == 401
