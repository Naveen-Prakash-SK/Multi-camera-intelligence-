from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import Optional

class Settings(BaseSettings):
    # App Settings
    PROJECT_NAME: str = "Multi-Camera Intelligence Backend"
    VERSION: str = "0.1.0"
    ENVIRONMENT: str = "development"
    
    # Gateway
    GATEWAY_URL: Optional[str] = None
    
    # Database
    DATABASE_URL: str = "postgresql://postgres:postgres@localhost:5432/multicam"
    
    # Redis / Celery
    REDIS_URL: str = "redis://localhost:6379/0"
    
    # Qdrant
    QDRANT_URL: str = "http://localhost:6333"
    
    # Ollama
    OLLAMA_BASE_URL: str = "http://localhost:11434"
    OLLAMA_REASONING_MODEL: str = "qwen2.5:14b" # Fallback if specific version not provided
    OLLAMA_VISION_MODEL: str = "llava:13b"
    OLLAMA_TIMEOUT: float = 30.0
    # Optional basic auth when Ollama is exposed through an authenticated tunnel
    OLLAMA_AUTH_USER: Optional[str] = None
    OLLAMA_AUTH_PASSWORD: Optional[str] = None
    
    # Storage
    STORAGE_PATH: str = "./storage"
    
    model_config = SettingsConfigDict(env_file=".env", case_sensitive=True, extra='ignore')

settings = Settings()
