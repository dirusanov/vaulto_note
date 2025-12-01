from pydantic_settings import BaseSettings
from pydantic import PostgresDsn, computed_field
from typing import Optional

class Settings(BaseSettings):
    PROJECT_NAME: str = "Vaulto Note"
    
    # Database
    DATABASE_URL: str
    
    # JWT
    JWT_SECRET_KEY: str
    JWT_ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60
    
    # API Secret Key for self-hosted deployments (optional)
    API_SECRET_KEY: Optional[str] = None

    # AI / LLM
    WHISPER_API_URL: str = "http://whisper:9000/inference"
    WHISPER_API_TIMEOUT: int = 120
    LLM_API_URL: str = "http://ollama:11434/v1/chat/completions"
    LLM_MODEL: str = "llama3"
    LLM_SYSTEM_PROMPT: str = (
        "You are a careful writing assistant. "
        "Return ONLY the improved user text without any preamble or explanations."
    )
    LLM_TEMPERATURE: float = 0.4
    LLM_TIMEOUT: int = 120
    
    class Config:
        env_file = ".env"
        case_sensitive = True

settings = Settings()
