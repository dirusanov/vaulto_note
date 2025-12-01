from typing import Optional
from pydantic import BaseModel, ConfigDict, Field
from datetime import datetime
import uuid

# Encryption Contract:
# - API accepts encrypted fields: 'encrypted_title' and 'encrypted_content'.
# - Backend stores these encrypted values. Decryption is performed on the client.

class NoteBase(BaseModel):
    encrypted_title: Optional[str] = Field(None, description="Encrypted title (AES-GCM base64)")
    encrypted_content: str = Field(..., description="Encrypted content (AES-GCM base64)")
    is_archived: bool = False
    audio_file_path: Optional[str] = Field(None, description="Path to encrypted audio file")
    audio_duration: Optional[int] = Field(None, description="Audio duration in seconds")
    encrypted_transcription: Optional[str] = Field(None, description="Encrypted transcription text")
    has_audio: bool = False

class NoteCreate(NoteBase):
    """Create note with encrypted data."""
    pass

class NoteUpdate(BaseModel):
    """Update note with encrypted data."""
    encrypted_title: Optional[str] = Field(None, description="New encrypted title")
    encrypted_content: Optional[str] = Field(None, description="New encrypted content")
    is_archived: Optional[bool] = None
    audio_file_path: Optional[str] = Field(None, description="Path to encrypted audio file")
    audio_duration: Optional[int] = Field(None, description="Audio duration in seconds")
    encrypted_transcription: Optional[str] = Field(None, description="Encrypted transcription text")
    has_audio: Optional[bool] = None

class NoteInDBBase(NoteBase):
    """Note as stored in DB (encrypted)."""
    id: uuid.UUID
    user_id: uuid.UUID
    created_at: datetime
    updated_at: datetime
    
    model_config = ConfigDict(from_attributes=True)

class Note(NoteInDBBase):
    """Public note schema (encrypted)."""
    pass

class NoteInDB(BaseModel):
    """Internal DB representation (encrypted fields)."""
    id: uuid.UUID
    user_id: uuid.UUID
    encrypted_title: Optional[str]
    encrypted_content: str
    is_archived: bool
    audio_file_path: Optional[str]
    audio_duration: Optional[int]
    encrypted_transcription: Optional[str]
    has_audio: bool
    created_at: datetime
    updated_at: datetime
    
    model_config = ConfigDict(from_attributes=True)
