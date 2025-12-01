from typing import AsyncGenerator, Optional
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import jwt, JWTError
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.core.config import settings
from app.db.session import AsyncSessionLocal
from app.models.user import User
from app.schemas.auth import TokenPayload

reusable_oauth2 = OAuth2PasswordBearer(
    tokenUrl=f"/api/v1/auth/login"
)

async def get_db() -> AsyncGenerator[AsyncSession, None]:
    async with AsyncSessionLocal() as session:
        yield session

async def get_current_user(
    db: AsyncSession = Depends(get_db),
    token: str = Depends(reusable_oauth2)
) -> User:
    # Check if API_SECRET_KEY is configured and matches the provided token
    if settings.API_SECRET_KEY and token == settings.API_SECRET_KEY:
        # Return a system user for API key authentication
        # This bypasses user authentication for self-hosted deployments
        # Create a mock user object (not persisted to DB)
        from uuid import UUID
        system_user = type('SystemUser', (), {
            'id': UUID('00000000-0000-0000-0000-000000000000'),
            'email': 'system@api',
            'is_active': True,
            'hashed_password': '',
            'wallet_address': None,
            'wallet_nonce': None
        })()
        return system_user
    
    # Otherwise, proceed with JWT validation
    try:
        payload = jwt.decode(
            token, settings.JWT_SECRET_KEY, algorithms=[settings.JWT_ALGORITHM]
        )
        token_data = TokenPayload(**payload)
    except (JWTError, ValueError):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Could not validate credentials",
        )
    
    result = await db.execute(select(User).where(User.id == token_data.sub))
    user = result.scalars().first()
    
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    if not user.is_active:
        raise HTTPException(status_code=400, detail="Inactive user")
    return user
