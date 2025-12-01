from typing import Optional
from pydantic import BaseModel, EmailStr, ConfigDict
from datetime import datetime
import uuid

class UserBase(BaseModel):
    email: Optional[EmailStr] = None
    is_active: Optional[bool] = True
    wallet_address: Optional[str] = None

class UserCreate(UserBase):
    password: Optional[str] = None

class UserUpdate(UserBase):
    password: Optional[str] = None

class UserInDBBase(UserBase):
    id: uuid.UUID
    created_at: datetime
    updated_at: datetime
    
    model_config = ConfigDict(from_attributes=True)

class User(UserInDBBase):
    pass

class UserInDB(UserInDBBase):
    hashed_password: Optional[str] = None
