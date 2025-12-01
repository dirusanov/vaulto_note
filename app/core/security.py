from datetime import datetime, timedelta
from typing import Optional, Any, Union
from jose import jwt
from passlib.context import CryptContext
from eth_account.messages import encode_defunct
from eth_account import Account
import uuid

from app.core.config import settings

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def create_access_token(subject: Union[str, Any], expires_delta: Optional[timedelta] = None) -> str:
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    
    to_encode = {"exp": expire, "sub": str(subject)}
    encoded_jwt = jwt.encode(to_encode, settings.JWT_SECRET_KEY, algorithm=settings.JWT_ALGORITHM)
    return encoded_jwt

def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password: str) -> str:
    return pwd_context.hash(password)

def generate_nonce() -> str:
    """Generate a random nonce for wallet authentication."""
    return str(uuid.uuid4())

def verify_wallet_signature(wallet_address: str, nonce: str, signature: str) -> bool:
    """
    Verify that the signature was created by wallet_address signing the nonce.
    """
    try:
        # Construct the message that was signed. 
        # In a real app, you might want a specific message format like:
        # "Sign this message to login to Vaulto Note: <nonce>"
        # For now, we assume the user signed the raw nonce string.
        message = encode_defunct(text=nonce)
        
        # Recover the address from the signature
        recovered_address = Account.recover_message(message, signature=signature)
        
        return recovered_address.lower() == wallet_address.lower()
    except Exception:
        return False
