from typing import Any
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.api import deps
from app.core import security
from app.models.user import User
from app.schemas.wallet import WalletNonceRequest, WalletNonceResponse, WalletVerifyRequest
from app.schemas.auth import Token

router = APIRouter()

@router.post("/nonce", response_model=WalletNonceResponse)
async def get_nonce(
    request: WalletNonceRequest,
    db: AsyncSession = Depends(deps.get_db)
) -> Any:
    """
    Get a nonce for wallet signature. Creates user if not exists.
    """
    wallet_address = request.wallet_address.lower()
    
    result = await db.execute(select(User).where(User.wallet_address == wallet_address))
    user = result.scalars().first()
    
    nonce = security.generate_nonce()
    
    if not user:
        user = User(
            wallet_address=wallet_address,
            wallet_nonce=nonce,
            is_active=True
        )
        db.add(user)
    else:
        user.wallet_nonce = nonce
    
    await db.commit()
    await db.refresh(user)
    
    return {"wallet_address": wallet_address, "nonce": nonce}

@router.post("/verify", response_model=Token)
async def verify_signature(
    request: WalletVerifyRequest,
    db: AsyncSession = Depends(deps.get_db)
) -> Any:
    """
    Verify wallet signature and return access token.
    """
    wallet_address = request.wallet_address.lower()
    
    result = await db.execute(select(User).where(User.wallet_address == wallet_address))
    user = result.scalars().first()
    
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
        
    if not user.wallet_nonce:
        raise HTTPException(status_code=400, detail="No nonce generated for this user")
        
    is_valid = security.verify_wallet_signature(
        wallet_address=wallet_address,
        nonce=user.wallet_nonce,
        signature=request.signature
    )
    
    if not is_valid:
        raise HTTPException(status_code=400, detail="Invalid signature")
        
    # Rotate nonce to prevent replay attacks
    user.wallet_nonce = security.generate_nonce()
    await db.commit()
    
    access_token = security.create_access_token(subject=user.id)
    return {
        "access_token": access_token,
        "token_type": "bearer",
    }
