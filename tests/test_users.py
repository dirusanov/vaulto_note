"""
Tests for user endpoints.
"""
import pytest
from httpx import AsyncClient


@pytest.mark.anyio
async def test_get_current_user(client: AsyncClient, auth_headers):
    """Test getting current user information."""
    response = await client.get("/api/v1/users/me", headers=auth_headers)
    assert response.status_code == 200
    
    data = response.json()
    assert "id" in data
    assert "email" in data
    assert data["email"] == "testuser@example.com"
    assert data["is_active"] is True
    assert "created_at" in data


@pytest.mark.anyio
async def test_get_current_user_unauthorized(client: AsyncClient):
    """Test that accessing /users/me without token fails."""
    response = await client.get("/api/v1/users/me")
    assert response.status_code == 403


@pytest.mark.anyio
async def test_get_current_user_invalid_token(client: AsyncClient):
    """Test that invalid token is rejected."""
    headers = {"Authorization": "Bearer invalid_token_here"}
    response = await client.get("/api/v1/users/me", headers=headers)
    assert response.status_code == 403
