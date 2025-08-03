from typing import List, Optional
from pydantic_settings import BaseSettings
from pydantic import AnyHttpUrl, validator
import os


class Settings(BaseSettings):
    PROJECT_NAME: str = "Preggo API"
    VERSION: str = "0.1.0"
    API_V1_STR: str = "/api/v1"
    ENVIRONMENT: str = "development"
    
    # CORS origins - expanded for Supabase integration
    BACKEND_CORS_ORIGINS: List[str] = [
        "http://localhost:3000",
        "http://localhost:3001", 
        "https://localhost:3000",
        "https://localhost:3001"
    ]
    
    @validator("BACKEND_CORS_ORIGINS", pre=True)
    def assemble_cors_origins(cls, v):
        if isinstance(v, str) and not v.startswith("["):
            return [i.strip() for i in v.split(",")]
        elif isinstance(v, (list, str)):
            return v
        raise ValueError(v)
    
    # Database Configuration - Using Supabase PostgreSQL
    DATABASE_URL: str = os.getenv("DATABASE_URL", "postgresql://postgres:password@localhost:5432/preggo")
    
    # Security
    SECRET_KEY: str = "your-secret-key-here-change-this-in-production"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24 * 8  # 8 days
    
    # Supabase Configuration
    SUPABASE_URL: str = os.getenv("SUPABASE_URL", "https://your-project-id.supabase.co")
    SUPABASE_ANON_KEY: str = os.getenv("SUPABASE_ANON_KEY", "your-anon-key-here")
    SUPABASE_SERVICE_ROLE_KEY: str = os.getenv("SUPABASE_SERVICE_ROLE_KEY", "your-service-role-key-here")
    SUPABASE_JWT_SECRET: str = os.getenv("SUPABASE_JWT_SECRET", "your-jwt-secret-here")
    
    # Supabase Storage Configuration
    SUPABASE_STORAGE_BUCKET: str = "pregnancy-media"
    SUPABASE_STORAGE_BASE_URL: Optional[str] = None
    
    @validator("SUPABASE_STORAGE_BASE_URL", pre=True, always=True)
    def assemble_storage_url(cls, v, values):
        if v is None:
            supabase_url = values.get("SUPABASE_URL")
            if supabase_url:
                return f"{supabase_url}/storage/v1/object/public"
        return v
    
    # File Upload Configuration
    MAX_FILE_SIZE: int = 50 * 1024 * 1024  # 50MB
    ALLOWED_IMAGE_TYPES: List[str] = ["image/jpeg", "image/png", "image/webp", "image/gif"]
    ALLOWED_VIDEO_TYPES: List[str] = ["video/mp4", "video/webm", "video/ogg"]
    
    # Feature Flags
    ENABLE_REAL_TIME_UPDATES: bool = True
    ENABLE_PUSH_NOTIFICATIONS: bool = True
    ENABLE_EMAIL_NOTIFICATIONS: bool = True
    ENABLE_FAMILY_INVITATIONS: bool = True
    ENABLE_MEMORY_BOOK_GENERATION: bool = False  # Future feature
    
    # Rate Limiting
    RATE_LIMIT_PER_MINUTE: int = 60
    RATE_LIMIT_BURST: int = 100
    
    # Logging Configuration
    LOG_LEVEL: str = "INFO"
    LOG_TO_DATABASE: bool = True
    LOG_TO_FILE: bool = True
    
    # Pregnancy Tracking Configuration
    DEFAULT_PREGNANCY_DURATION_WEEKS: int = 40
    MIN_PREGNANCY_WEEK: int = 0
    MAX_PREGNANCY_WEEK: int = 42
    
    # Family Sharing Configuration
    MAX_FAMILY_GROUPS: int = 10
    MAX_MEMBERS_PER_GROUP: int = 50
    INVITATION_EXPIRY_DAYS: int = 7
    
    # Content Configuration
    MAX_POST_LENGTH: int = 2000
    MAX_COMMENT_LENGTH: int = 500
    MAX_IMAGES_PER_POST: int = 10
    
    class Config:
        env_file = ".env"
        case_sensitive = True
        # Allow environment variables to override settings
        env_prefix = ""


settings = Settings()