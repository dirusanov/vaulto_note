"""
Tests for authentication endpoints (email/password and wallet).
"""
import pytest
from httpx import AsyncClient


@pytest.mark.anyio
async def test_root_endpoint(client: AsyncClient):
    """Test root endpoint returns welcome message."""
    response = await client.get("/")
    assert response.status_code == 200
    data = response.json()
    assert "message" in data
    assert data["message"] == "Welcome to Vaulto Note API"


@pytest.mark.anyio
async def test_register_user(client: AsyncClient):
    """Test user registration with email and password."""
    user_data = {
        "email": "newuser@example.com",
        "password": "SecurePass123!"
    }
    response = await client.post("/api/v1/auth/register", json=user_data)
    assert response.status_code == 200
    
    data = response.json()
    assert data["email"] == user_data["email"]
    assert data["is_active"] is True
    assert "id" in data
    assert "created_at" in data
    assert "hashed_password" not in data  # Should not expose password


@pytest.mark.anyio
async def test_register_duplicate_email(client: AsyncClient, test_user):
    """Test that registering with duplicate email fails."""
    response = await client.post("/api/v1/auth/register", json=test_user)
    assert response.status_code == 400
    data = response.json()
    assert "already exists" in data["detail"].lower()


@pytest.mark.anyio
async def test_login_success(client: AsyncClient, test_user):
    """Test successful login returns JWT token."""
    response = await client.post("/api/v1/auth/login", json=test_user)
    assert response.status_code == 200
    
    data = response.json()
    assert "access_token" in data
    assert "token_type" in data
    assert data["token_type"] == "bearer"
    assert len(data["access_token"]) > 0


@pytest.mark.anyio
async def test_login_wrong_password(client: AsyncClient, test_user):
    """Test login with wrong password fails."""
    wrong_credentials = {
        "email": test_user["email"],
        "password": "WrongPassword123!"
    }
    response = await client.post("/api/v1/auth/login", json=wrong_credentials)
    assert response.status_code == 400
    data = response.json()
    assert "incorrect" in data["detail"].lower()


@pytest.mark.anyio
async def test_login_nonexistent_user(client: AsyncClient):
    """Test login with non-existent email fails."""
    credentials = {
        "email": "nonexistent@example.com",
        "password": "SomePassword123!"
    }
    response = await client.post("/api/v1/auth/login", json=credentials)
    assert response.status_code == 400


@pytest.mark.anyio
async def test_wallet_auth_get_nonce(client: AsyncClient):
    """Test getting nonce for wallet authentication."""
    wallet_data = {"wallet_address": "0x742d35Cc6634C0532925a3b844Bc9e7595f0bEb"}
    response = await client.post("/api/v1/wallet-auth/nonce", json=wallet_data)
    assert response.status_code == 200
    
    data = response.json()
    assert "wallet_address" in data
    assert "nonce" in data
    assert data["wallet_address"].lower() == wallet_data["wallet_address"].lower()
    assert len(data["nonce"]) > 0


@pytest.mark.anyio
async def test_wallet_auth_nonce_creates_user(client: AsyncClient):
    """Test that requesting nonce creates a new user if not exists."""
    wallet_data = {"wallet_address": "0xNewWallet123456789"}
    response = await client.post("/api/v1/wallet-auth/nonce", json=wallet_data)
    assert response.status_code == 200
    
    # Request again - should return different nonce but same wallet
    response2 = await client.post("/api/v1/wallet-auth/nonce", json=wallet_data)
    assert response2.status_code == 200
    
    data1 = response.json()
    data2 = response2.json()
    assert data1["wallet_address"] == data2["wallet_address"]
    assert data1["nonce"] != data2["nonce"]  # Nonce should be rotated
