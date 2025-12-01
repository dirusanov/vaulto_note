import pytest
import pytest_asyncio
from httpx import AsyncClient

@pytest.mark.asyncio
async def test_create_encrypted_note_only(client: AsyncClient, auth_headers: dict):
    """
    Test creating a note with ONLY encrypted fields.
    This verifies that the backend no longer requires plaintext 'title' and 'content'.
    """
    note_data = {
        "encrypted_title": "encrypted_title_string",
        "encrypted_content": "encrypted_content_string",
        "is_archived": False
    }
    
    response = await client.post("/api/v1/notes/", json=note_data, headers=auth_headers)
    
    if response.status_code != 200:
        print(f"Error response: {response.status_code}")
        print(f"Error body: {response.text}")
    
    assert response.status_code == 200
    data = response.json()
    assert data["encrypted_title"] == "encrypted_title_string"
    assert data["encrypted_content"] == "encrypted_content_string"
    assert "id" in data
