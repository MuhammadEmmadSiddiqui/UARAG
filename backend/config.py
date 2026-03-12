"""Application configuration settings."""
from pydantic_settings import BaseSettings, SettingsConfigDict
from functools import lru_cache


class Settings(BaseSettings):
    """Application settings."""
    model_config = SettingsConfigDict(env_file=".env", case_sensitive=False)
    
    # API Keys
    groq_api_key: str = ""
    
    # JWT Settings
    secret_key: str = "your-secret-key-change-in-production"
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 30
    
    # Database
    database_url: str = "sqlite+aiosqlite:///./chatbot.db"
    
    # FastAPI
    api_host: str = "0.0.0.0"
    api_port: int = 8000
    
    # Streamlit (optional, not used by backend)
    streamlit_port: int = 8501
    api_base_url: str = "http://localhost:8000"
    
    # App settings
    app_name: str = "UARAG - Uncertainty Aware Retrieval Augmented Generation"
    debug: bool = False


@lru_cache()
def get_settings() -> Settings:
    """Get cached settings instance."""
    return Settings()
