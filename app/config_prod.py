"""
Production configuration settings for the AI Interview API
"""
import os
from typing import List

try:
    from pydantic_settings import BaseSettings
except ImportError:
    from pydantic import BaseSettings


class ProductionSettings(BaseSettings):
    """Production application settings"""
    
    # Database - PostgreSQL for production
    database_url: str = os.getenv("DATABASE_URL", "postgresql://user:password@localhost/interview_api")
    
    # Security - Strong production keys
    secret_key: str = os.getenv("SECRET_KEY", "")
    algorithm: str = "HS256"
    access_token_expire_minutes: int = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "30"))
    
    # OpenAI
    openai_api_key: str = os.getenv("OPENAI_API_KEY", "")
    
    # Admin
    admin_email: str = os.getenv("ADMIN_EMAIL", "admin@example.com")
    admin_password: str = os.getenv("ADMIN_PASSWORD", "")
    
    # File Upload
    max_file_size_mb: int = int(os.getenv("MAX_FILE_SIZE_MB", "50"))
    allowed_audio_formats: str = os.getenv("ALLOWED_AUDIO_FORMATS", "mp3,wav,m4a,flac")
    upload_dir: str = os.getenv("UPLOAD_DIR", "uploads")
    
    # Application - Production settings
    debug: bool = os.getenv("DEBUG", "false").lower() == "true"
    host: str = "0.0.0.0"
    port: int = int(os.getenv("PORT", "8000"))
    
    # API Settings
    api_v1_prefix: str = "/api/v1"
    project_name: str = "AI Interview API"
    version: str = "1.0.0"
    
    # CORS Settings for production
    allowed_origins: List[str] = [
        "https://your-frontend-domain.com",
        "https://ai-interview-frontend.vercel.app",
        # Add your frontend domains here
    ]
    
    # Logging
    log_level: str = os.getenv("LOG_LEVEL", "INFO")
    
    # Rate limiting
    rate_limit_requests: int = int(os.getenv("RATE_LIMIT_REQUESTS", "100"))
    rate_limit_window: int = int(os.getenv("RATE_LIMIT_WINDOW", "3600"))  # 1 hour
    
    @property
    def audio_formats_list(self) -> List[str]:
        """Get allowed audio formats as a list"""
        return [fmt.strip() for fmt in self.allowed_audio_formats.split(",")]
    
    @property
    def is_production(self) -> bool:
        """Check if running in production"""
        return not self.debug
    
    def validate_required_settings(self):
        """Validate that all required production settings are provided"""
        required_settings = {
            "SECRET_KEY": self.secret_key,
            "OPENAI_API_KEY": self.openai_api_key,
            "ADMIN_PASSWORD": self.admin_password,
        }
        
        missing = [key for key, value in required_settings.items() if not value]
        if missing:
            raise ValueError(f"Missing required environment variables: {', '.join(missing)}")
    
    class Config:
        env_file = ".env"
        case_sensitive = False


# Global settings instance
settings = ProductionSettings()

# Validate settings in production
if settings.is_production:
    settings.validate_required_settings()

# Ensure upload directory exists
os.makedirs(settings.upload_dir, exist_ok=True)
