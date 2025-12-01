from typing import Optional
from datetime import datetime
from sqlalchemy import String, Boolean, DateTime
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.sql import func
import uuid

from app.db.session import Base

class User(Base):
    __tablename__ = "users"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, server_default=func.gen_random_uuid())
    email: Mapped[Optional[str]] = mapped_column(String, unique=True, index=True, nullable=True)
    hashed_password: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    
    wallet_address: Mapped[Optional[str]] = mapped_column(String, unique=True, index=True, nullable=True)
    wallet_nonce: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), onupdate=func.now(), server_default=func.now())

    notes = relationship("Note", back_populates="owner", cascade="all, delete-orphan")
