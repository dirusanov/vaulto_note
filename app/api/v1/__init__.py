from fastapi import APIRouter
from app.api.v1 import routes_auth, routes_wallet_auth, routes_users, routes_notes, routes_ai

api_router = APIRouter()

api_router.include_router(routes_auth.router, prefix="/auth", tags=["auth"])
api_router.include_router(routes_wallet_auth.router, prefix="/wallet-auth", tags=["wallet-auth"])
api_router.include_router(routes_users.router, prefix="/users", tags=["users"])
api_router.include_router(routes_notes.router, prefix="/notes", tags=["notes"])
api_router.include_router(routes_ai.router, prefix="/ai", tags=["ai"])

@api_router.get("/health", tags=["health"])
async def health_check():
    """Health check endpoint for monitoring service status"""
    return {
        "status": "healthy",
        "service": "vaulto-note-backend",
        "version": "1.0.0"
    }
