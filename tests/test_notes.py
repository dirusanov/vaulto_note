"""
Tests for notes CRUD endpoints.
"""
import pytest
from httpx import AsyncClient


@pytest.mark.anyio
async def test_create_note(client: AsyncClient, auth_headers):
    """Test creating a new note."""
    note_data = {
        "title": "Test Note",
        "content": "This is test content",
        "is_archived": False
    }
    response = await client.post("/api/v1/notes/", json=note_data, headers=auth_headers)
    assert response.status_code == 200
    
    data = response.json()
    assert data["title"] == note_data["title"]
    assert data["content"] == note_data["content"]
    assert data["is_archived"] == note_data["is_archived"]
    assert "id" in data
    assert "user_id" in data
    assert "created_at" in data
    assert "updated_at" in data


@pytest.mark.anyio
async def test_create_note_unauthorized(client: AsyncClient):
    """Test that creating note without auth fails."""
    note_data = {"title": "Test", "content": "Content", "is_archived": False}
    response = await client.post("/api/v1/notes/", json=note_data)
    assert response.status_code == 403


@pytest.mark.anyio
async def test_list_notes(client: AsyncClient, auth_headers):
    """Test listing all notes for current user."""
    # Create a note first
    note_data = {"title": "List Test", "content": "Content", "is_archived": False}
    await client.post("/api/v1/notes/", json=note_data, headers=auth_headers)
    
    # List notes
    response = await client.get("/api/v1/notes/", headers=auth_headers)
    assert response.status_code == 200
    
    data = response.json()
    assert isinstance(data, list)
    assert len(data) > 0
    assert any(note["title"] == "List Test" for note in data)


@pytest.mark.anyio
async def test_get_single_note(client: AsyncClient, auth_headers):
    """Test getting a specific note by ID."""
    # Create a note
    note_data = {"title": "Single Note", "content": "Content", "is_archived": False}
    create_response = await client.post("/api/v1/notes/", json=note_data, headers=auth_headers)
    note_id = create_response.json()["id"]
    
    # Get the note
    response = await client.get(f"/api/v1/notes/{note_id}", headers=auth_headers)
    assert response.status_code == 200
    
    data = response.json()
    assert data["id"] == note_id
    assert data["title"] == note_data["title"]
    assert data["content"] == note_data["content"]


@pytest.mark.anyio
async def test_get_nonexistent_note(client: AsyncClient, auth_headers):
    """Test getting a note that doesn't exist."""
    fake_id = "00000000-0000-0000-0000-000000000000"
    response = await client.get(f"/api/v1/notes/{fake_id}", headers=auth_headers)
    assert response.status_code == 404


@pytest.mark.anyio
async def test_update_note(client: AsyncClient, auth_headers):
    """Test updating a note."""
    # Create a note
    note_data = {"title": "Original", "content": "Original content", "is_archived": False}
    create_response = await client.post("/api/v1/notes/", json=note_data, headers=auth_headers)
    note_id = create_response.json()["id"]
    
    # Update the note
    update_data = {"title": "Updated", "content": "Updated content", "is_archived": True}
    response = await client.put(f"/api/v1/notes/{note_id}", json=update_data, headers=auth_headers)
    assert response.status_code == 200
    
    data = response.json()
    assert data["id"] == note_id
    assert data["title"] == update_data["title"]
    assert data["content"] == update_data["content"]
    assert data["is_archived"] == update_data["is_archived"]


@pytest.mark.anyio
async def test_partial_update_note(client: AsyncClient, auth_headers):
    """Test partially updating a note (only some fields)."""
    # Create a note
    note_data = {"title": "Original", "content": "Original content", "is_archived": False}
    create_response = await client.post("/api/v1/notes/", json=note_data, headers=auth_headers)
    note_id = create_response.json()["id"]
    
    # Update only title
    update_data = {"title": "New Title"}
    response = await client.put(f"/api/v1/notes/{note_id}", json=update_data, headers=auth_headers)
    assert response.status_code == 200
    
    data = response.json()
    assert data["title"] == "New Title"
    assert data["content"] == "Original content"  # Should remain unchanged


@pytest.mark.anyio
async def test_delete_note(client: AsyncClient, auth_headers):
    """Test deleting a note."""
    # Create a note
    note_data = {"title": "To Delete", "content": "Will be deleted", "is_archived": False}
    create_response = await client.post("/api/v1/notes/", json=note_data, headers=auth_headers)
    note_id = create_response.json()["id"]
    
    # Delete the note
    response = await client.delete(f"/api/v1/notes/{note_id}", headers=auth_headers)
    assert response.status_code == 200
    
    # Verify it's deleted
    get_response = await client.get(f"/api/v1/notes/{note_id}", headers=auth_headers)
    assert get_response.status_code == 404


@pytest.mark.anyio
async def test_user_cannot_access_other_users_notes(client: AsyncClient):
    """Test that users can only access their own notes."""
    # Create first user and note
    user1_data = {"email": "user1@test.com", "password": "Pass123!"}
    await client.post("/api/v1/auth/register", json=user1_data)
    login1 = await client.post("/api/v1/auth/login", json=user1_data)
    token1 = login1.json()["access_token"]
    headers1 = {"Authorization": f"Bearer {token1}"}
    
    note_response = await client.post("/api/v1/notes/", 
                                      json={"title": "User1 Note", "content": "Private", "is_archived": False},
                                      headers=headers1)
    note_id = note_response.json()["id"]
    
    # Create second user
    user2_data = {"email": "user2@test.com", "password": "Pass123!"}
    await client.post("/api/v1/auth/register", json=user2_data)
    login2 = await client.post("/api/v1/auth/login", json=user2_data)
    token2 = login2.json()["access_token"]
    headers2 = {"Authorization": f"Bearer {token2}"}
    
    # Try to access user1's note as user2
    response = await client.get(f"/api/v1/notes/{note_id}", headers=headers2)
    assert response.status_code == 404  # Should not find note


@pytest.mark.anyio
async def test_list_notes_pagination(client: AsyncClient, auth_headers):
    """Test notes list pagination."""
    # Create multiple notes
    for i in range(5):
        note_data = {"title": f"Note {i}", "content": f"Content {i}", "is_archived": False}
        await client.post("/api/v1/notes/", json=note_data, headers=auth_headers)
    
    # Test with limit
    response = await client.get("/api/v1/notes/?limit=3", headers=auth_headers)
    assert response.status_code == 200
    data = response.json()
    assert len(data) <= 3
    
    # Test with skip
    response = await client.get("/api/v1/notes/?skip=2&limit=2", headers=auth_headers)
    assert response.status_code == 200
    data = response.json()
    assert len(data) <= 2
