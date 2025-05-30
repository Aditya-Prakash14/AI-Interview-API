"""
Configuration settings for the AI Interview API
"""
import os
from typing import List
try:
    from pydantic_settings import BaseSettings
except ImportError:
    from pydantic import BaseSettings


class Settings(BaseSettings):
    """Application settings"""

    # Database - Use PostgreSQL in production
    database_url: str = os.getenv("DATABASE_URL", "sqlite:///./interview_api.db")

    # Security
    secret_key: str = os.getenv("SECRET_KEY", "your-secret-key-here-change-in-production")
    algorithm: str = "HS256"
    access_token_expire_minutes: int = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "30"))

    # OpenAI
    openai_api_key: str = os.getenv("OPENAI_API_KEY", "")

    # Admin
    admin_email: str = os.getenv("ADMIN_EMAIL", "admin@example.com")
    admin_password: str = os.getenv("ADMIN_PASSWORD", "admin123")

    # File Upload
    max_file_size_mb: int = 50
    allowed_audio_formats: str = "mp3,wav,m4a,flac"
    upload_dir: str = "uploads"

    @property
    def audio_formats_list(self) -> List[str]:
        """Get allowed audio formats as a list"""
        return [fmt.strip() for fmt in self.allowed_audio_formats.split(",")]

    # Application
    debug: bool = os.getenv("DEBUG", "true").lower() == "true"
    host: str = "0.0.0.0"
    port: int = int(os.getenv("PORT", "8000"))

    # API Settings
    api_v1_prefix: str = "/api/v1"
    project_name: str = "AI Interview API"
    version: str = "1.0.0"

    class Config:
        env_file = ".env"
        case_sensitive = False


# Global settings instance
settings = Settings()

# Ensure upload directory exists
os.makedirs(settings.upload_dir, exist_ok=True)
