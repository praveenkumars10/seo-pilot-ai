import os
from pathlib import Path
from typing import Optional
from pydantic_settings import BaseSettings, SettingsConfigDict

BASE_DIR = Path(__file__).resolve().parent.parent
ROOT_DIR = BASE_DIR.parent
DATA_DIR = BASE_DIR / "data"
DATA_DIR.mkdir(parents=True, exist_ok=True)

class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=str(ROOT_DIR / ".env"),
        env_file_encoding="utf-8",
        extra="ignore"
    )

    APP_NAME: str = "SEO Pilot AI"
    APP_ENV: str = "development"
    PORT: int = 8000
    FRONTEND_PORT: int = 5173
    DATABASE_URL: str = f"sqlite+aiosqlite:///{DATA_DIR / 'seopilot.db'}"
    APP_SECRET_KEY: str = "seopilot-secure-local-secret-key-32ch"

    # Google OAuth2 Credentials
    GOOGLE_CLIENT_ID: Optional[str] = None
    GOOGLE_CLIENT_SECRET: Optional[str] = None
    GOOGLE_REDIRECT_URI: str = "http://localhost:8000/api/google/oauth2callback"
    GOOGLE_TOKEN_FILE: str = str(DATA_DIR / "google_tokens.json")

    # AI Provider Keys
    GEMINI_API_KEY: Optional[str] = None
    ANTHROPIC_API_KEY: Optional[str] = None
    OPENAI_API_KEY: Optional[str] = None

    # Meta / Ollama / Local Models
    META_AI_BASE_URL: str = "http://localhost:11434/v1"
    META_AI_MODEL: str = "llama3.2"
    META_AI_API_KEY: Optional[str] = None

    # GitHub
    GITHUB_TOKEN: Optional[str] = None
    GITHUB_DEFAULT_BRANCH: str = "main"

    # Safety & Audit Limits
    MAX_CRAWL_PAGES: int = 50
    CRAWL_TIMEOUT_SECONDS: int = 15
    REQUIRE_CONSOLIDATED_APPROVAL: bool = True
    AUTO_ROLLBACK_ON_TEST_FAILURE: bool = True

settings = Settings()
