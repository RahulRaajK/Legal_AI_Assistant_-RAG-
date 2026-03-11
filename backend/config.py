"""Application configuration using Pydantic Settings."""
import os
from pydantic_settings import BaseSettings
from functools import lru_cache


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""
    
    # App
    APP_NAME: str = "Legal AI Assistant for Indian Law"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = True
    
    # Database
    DATABASE_URL: str = "sqlite+aiosqlite:///./legal_ai.db"
    
    # Ollama LLM
    OLLAMA_BASE_URL: str = "http://localhost:11434"
    OLLAMA_MODEL: str = "mistral"
    
    # Embeddings
    EMBEDDING_MODEL: str = "all-MiniLM-L6-v2"
    
    # ChromaDB
    CHROMA_PERSIST_DIR: str = "./chroma_data"
    CHROMA_COLLECTION_NAME: str = "indian_legal_docs"
    
    # JWT Auth
    SECRET_KEY: str = "legal-ai-secret-key-change-in-production-2024"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 1440
    
    # Crawler
    CRAWL_DELAY_SECONDS: int = 2
    MAX_CRAWL_PAGES: int = 100
    
    # Upload
    UPLOAD_DIR: str = "./uploads"
    MAX_UPLOAD_SIZE_MB: int = 50
    
    class Config:
        env_file = ".env"
        case_sensitive = True


@lru_cache()
def get_settings() -> Settings:
    return Settings()
