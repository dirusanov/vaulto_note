import pytest
from httpx import AsyncClient, ASGITransport
from app.main import app

@pytest.fixture
def anyio_backend():
    return "asyncio"

@pytest.fixture
async def client():
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        yield ac

@pytest.fixture
async def test_user(client):
    """Create a test user and return credentials."""
    user_data = {
        "email": "testuser@example.com",
        "password": "TestPassword123!"
    }
    response = await client.post("/api/v1/auth/register", json=user_data)
    assert response.status_code == 200
    return user_data

@pytest.fixture
async def auth_token(client, test_user):
    """Get authentication token for test user."""
    response = await client.post("/api/v1/auth/login", json=test_user)
    assert response.status_code == 200
    data = response.json()
    return data["access_token"]

@pytest.fixture
async def auth_headers(auth_token):
    """Get authorization headers with token."""
    return {"Authorization": f"Bearer {auth_token}"}
