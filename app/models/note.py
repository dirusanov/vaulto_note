from datetime import datetime

from sqlalchemy import String, Text, ForeignKey, DateTime, Boolean
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.sql import func
import uuid

from app.db.session import Base

class Note(Base):
    __tablename__ = "notes"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, server_default=func.gen_random_uuid())
    user_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("users.id"), index=True)
    
    # Encryption contract:
    # - title: plaintext (for search/indexing) - optional encryption later
    # - encrypted_title: encrypted version (when encryption is enabled)
    # - content: DEPRECATED - use encrypted_content
    # - encrypted_content: always encrypted in DB, decrypted in API layer
    title: Mapped[str | None] = mapped_column(String, index=True, nullable=True)
    encrypted_title: Mapped[str | None] = mapped_column(String, nullable=True)
    
    # Legacy field - will be removed when encryption is fully implemented
    content: Mapped[str | None] = mapped_column(Text, nullable=True)
    
    # New encrypted field - this is the future
    encrypted_content: Mapped[str] = mapped_column(Text, server_default='')
    
    is_archived: Mapped[bool] = mapped_column(Boolean, default=False)
    
    # Voice notes fields
    audio_file_path: Mapped[str | None] = mapped_column(String, nullable=True)
    audio_duration: Mapped[int | None] = mapped_column(nullable=True)  # Duration in seconds
    encrypted_transcription: Mapped[str | None] = mapped_column(Text, nullable=True)
    has_audio: Mapped[bool] = mapped_column(Boolean, default=False, index=True)
    
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), onupdate=func.now(), server_default=func.now())

    owner = relationship("User", back_populates="notes")

