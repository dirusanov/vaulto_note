from pydantic import BaseModel

class WalletNonceRequest(BaseModel):
    wallet_address: str

class WalletNonceResponse(BaseModel):
    wallet_address: str
    nonce: str

class WalletVerifyRequest(BaseModel):
    wallet_address: str
    signature: str
