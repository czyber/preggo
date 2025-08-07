from typing import List, Optional
try:
    from pydantic_settings import BaseSettings
except ImportError:
    from pydantic import BaseSettings
from pydantic import AnyHttpUrl, validator, ValidationError
import os
import re
import base64
import logging


# Placeholder values that should never be used in production
INSECURE_PLACEHOLDERS = {
    "your-secret-key-here-change-this-in-production",
    "your-project-id.supabase.co", 
    "https://your-project-id.supabase.co",
    "your-anon-key-here",
    "your-service-role-key-here", 
    "your-jwt-secret-here",
    "your-supabase-url.supabase.co",
    "https://your-supabase-url.supabase.co"
}


class Settings(BaseSettings):
    PROJECT_NAME: str = "Preggo API"
    VERSION: str = "0.1.0"
    API_V1_STR: str = "/api/v1"
    ENVIRONMENT: str = "development"
    
    # CORS origins - allowing all origins for development
    # In production, set BACKEND_CORS_ORIGINS env var to your frontend URL
    # Accepts: ["*"], "*", or comma-separated list like "url1,url2"
    BACKEND_CORS_ORIGINS: List[str] = ["*"]
    
    @validator("BACKEND_CORS_ORIGINS", pre=True)
    def assemble_cors_origins(cls, v):
        # Handle environment variable string
        if isinstance(v, str):
            # Handle JSON array format like ["*"] or ["url1","url2"]
            if v.startswith("[") and v.endswith("]"):
                import json
                try:
                    return json.loads(v)
                except json.JSONDecodeError:
                    pass
            # Handle single wildcard
            if v == "*":
                return ["*"]
            # Handle comma-separated list
            return [i.strip() for i in v.split(",")]
        elif isinstance(v, list):
            return v
        raise ValueError(v)
    
    # Database Configuration - Railway PostgreSQL
    DATABASE_URL: str = os.getenv("DATABASE_URL", "")
    
    @validator("DATABASE_URL")
    def validate_database_url(cls, v, values):
        """Validate database URL format and security"""
        if not v or v.strip() == "":
            raise ValueError("DATABASE_URL environment variable is required. Please add a PostgreSQL database in Railway.")
        
        # Basic URL format validation
        if not v.startswith(("postgresql://", "postgres://")):
            raise ValueError("DATABASE_URL must be a PostgreSQL connection string")
        
        # Check for localhost in production
        environment = values.get("ENVIRONMENT", "development")
        if environment == "production" and "localhost" in v:
            raise ValueError("DATABASE_URL cannot use localhost in production environment")
        
        return v
    
    # Security
    SECRET_KEY: str = os.getenv("SECRET_KEY", "your-secret-key-here-change-this-in-production")
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24 * 8  # 8 days
    
    @validator("SECRET_KEY")
    def validate_secret_key(cls, v, values):
        """Validate SECRET_KEY strength and security"""
        if not v or v.strip() == "":
            raise ValueError("SECRET_KEY cannot be empty")
        
        # Check minimum length
        if len(v) < 32:
            raise ValueError("SECRET_KEY must be at least 32 characters long")
        
        # Production environment requires stronger keys
        environment = values.get("ENVIRONMENT", "development")
        if environment == "production":
            if len(v) < 64:
                raise ValueError("SECRET_KEY must be at least 64 characters long in production")
            
            # Check for common weak patterns
            if v.lower() in ["password", "secret", "key"] or v.isdigit() or v.isalpha():
                raise ValueError("SECRET_KEY is too weak for production use")
        
        return v
    
    # Supabase Configuration
    SUPABASE_URL: str = os.getenv("SUPABASE_URL", "https://your-project-id.supabase.co")
    SUPABASE_ANON_KEY: str = os.getenv("SUPABASE_ANON_KEY", "your-anon-key-here")
    SUPABASE_SERVICE_ROLE_KEY: str = os.getenv("SUPABASE_SERVICE_ROLE_KEY", "your-service-role-key-here")
    SUPABASE_JWT_SECRET: str = os.getenv("SUPABASE_JWT_SECRET", "your-jwt-secret-here")
    
    @validator("SUPABASE_URL")
    def validate_supabase_url(cls, v, values):
        """Validate Supabase URL format and security"""
        if not v or v.strip() == "":
            raise ValueError("SUPABASE_URL cannot be empty")
        
        if v in INSECURE_PLACEHOLDERS:
            raise ValueError(
                "SUPABASE_URL is using a placeholder value. "
                "Please set your actual Supabase project URL."
            )
        
        # Must be HTTPS
        if not v.startswith("https://"):
            raise ValueError("SUPABASE_URL must use HTTPS")
        
        # Must be a valid Supabase URL format
        supabase_pattern = r"^https://[a-z0-9]{20}\.supabase\.co$"
        if not re.match(supabase_pattern, v):
            raise ValueError(
                "SUPABASE_URL must be in the format: https://your-project-id.supabase.co "
                "(20 character project ID)"
            )
        
        return v
    
    @validator("SUPABASE_ANON_KEY")
    def validate_supabase_anon_key(cls, v, values):
        """Validate Supabase anonymous key format"""
        if not v or v.strip() == "":
            raise ValueError("SUPABASE_ANON_KEY cannot be empty")
        
        if v in INSECURE_PLACEHOLDERS:
            raise ValueError(
                "SUPABASE_ANON_KEY is using a placeholder value. "
                "Please set your actual Supabase anonymous key."
            )
        
        # Verify it's an anon key by checking the role in the payload
        try:
            payload = cls._decode_jwt_payload(v)
            if payload.get("role") != "anon":
                raise ValueError("SUPABASE_ANON_KEY must have 'anon' role")
        except Exception:
            raise ValueError("SUPABASE_ANON_KEY is not a valid JWT token")
        
        return v
    
    @validator("SUPABASE_SERVICE_ROLE_KEY")
    def validate_supabase_service_role_key(cls, v, values):
        """Validate Supabase service role key format"""
        if not v or v.strip() == "":
            raise ValueError("SUPABASE_SERVICE_ROLE_KEY cannot be empty")
        
        if v in INSECURE_PLACEHOLDERS:
            raise ValueError(
                "SUPABASE_SERVICE_ROLE_KEY is using a placeholder value. "
                "Please set your actual Supabase service role key."
            )
        
        # Must be a valid JWT format
        if not cls._is_valid_jwt_format(v):
            raise ValueError("SUPABASE_SERVICE_ROLE_KEY must be a valid JWT token")
        
        # Verify it's a service_role key by checking the role in the payload
        try:
            payload = cls._decode_jwt_payload(v)
            if payload.get("role") != "service_role":
                raise ValueError("SUPABASE_SERVICE_ROLE_KEY must have 'service_role' role")
        except Exception:
            raise ValueError("SUPABASE_SERVICE_ROLE_KEY is not a valid JWT token")
        
        # Service role key should never be used in frontend
        environment = values.get("ENVIRONMENT", "development")
        if environment == "production":
            logging.getLogger(__name__).warning(
                "Service role key detected in production. Ensure this is never exposed to frontend."
            )
        
        return v
    
    @validator("SUPABASE_JWT_SECRET")
    def validate_supabase_jwt_secret(cls, v, values):
        """Validate Supabase JWT secret format and strength"""
        if not v or v.strip() == "":
            raise ValueError("SUPABASE_JWT_SECRET cannot be empty")
        
        if v in INSECURE_PLACEHOLDERS:
            raise ValueError(
                "SUPABASE_JWT_SECRET is using a placeholder value. "
                "Please set your actual Supabase JWT secret."
            )
        
        return v
    
    @staticmethod
    def _is_valid_jwt_format(token: str) -> bool:
        """Check if a string has valid JWT format (3 base64 parts separated by dots)"""
        parts = token.split('.')
        if len(parts) != 3:
            return False
        
        try:
            for part in parts:
                # Add padding if needed
                padded = part + '=' * (4 - len(part) % 4)
                base64.b64decode(padded)
            return True
        except Exception:
            return False
    
    @staticmethod
    def _decode_jwt_payload(token: str) -> dict:
        """Decode JWT payload without verification (for validation purposes only)"""
        parts = token.split('.')
        if len(parts) != 3:
            raise ValueError("Invalid JWT format")
        
        # Add padding if needed
        payload_part = parts[1]
        padded = payload_part + '=' * (4 - len(payload_part) % 4)
        
        import json
        decoded_bytes = base64.b64decode(padded)
        return json.loads(decoded_bytes)
    
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
    
    @validator("ENVIRONMENT")
    def validate_environment(cls, v):
        """Validate environment setting"""
        allowed_environments = {"development", "staging", "production", "test"}
        if v not in allowed_environments:
            raise ValueError(f"ENVIRONMENT must be one of: {', '.join(allowed_environments)}")
        return v
    
    def validate_production_requirements(self) -> List[str]:
        """
        Validate all production-specific requirements and return list of warnings/errors.
        Called during startup to ensure production readiness.
        """
        issues = []
        
        if self.ENVIRONMENT == "production":
            # Check for any remaining placeholder values
            sensitive_fields = {
                "SECRET_KEY": self.SECRET_KEY,
                "SUPABASE_URL": self.SUPABASE_URL,
                "SUPABASE_ANON_KEY": self.SUPABASE_ANON_KEY,
                "SUPABASE_SERVICE_ROLE_KEY": self.SUPABASE_SERVICE_ROLE_KEY,
                "SUPABASE_JWT_SECRET": self.SUPABASE_JWT_SECRET,
            }
            
            for field_name, field_value in sensitive_fields.items():
                if field_value in INSECURE_PLACEHOLDERS:
                    issues.append(f"CRITICAL: {field_name} is using a placeholder value in production")
            
            # Check for localhost configurations
            if "localhost" in self.DATABASE_URL:
                issues.append("CRITICAL: DATABASE_URL uses localhost in production")
            
            # Check CORS origins for production
            for origin in self.BACKEND_CORS_ORIGINS:
                if "localhost" in origin and self.ENVIRONMENT == "production":
                    issues.append(f"WARNING: CORS origin '{origin}' includes localhost in production")
            
            # Check for development-only settings
            if self.LOG_LEVEL == "DEBUG":
                issues.append("WARNING: LOG_LEVEL is set to DEBUG in production")
        
        return issues
    
    def log_configuration_status(self, logger: logging.Logger):
        """
        Log configuration status without exposing sensitive information.
        """
        logger.info(f"Configuration loaded for environment: {self.ENVIRONMENT}")
        logger.info(f"Project: {self.PROJECT_NAME} v{self.VERSION}")
        logger.info(f"API prefix: {self.API_V1_STR}")
        
        # Log configuration status without exposing values
        config_status = {
            "DATABASE_URL": "✓ Configured" if self.DATABASE_URL else "✗ Missing",
            "SECRET_KEY": "✓ Configured" if self.SECRET_KEY else "✗ Missing",
            "SUPABASE_URL": "✓ Configured" if self.SUPABASE_URL else "✗ Missing", 
            "SUPABASE_ANON_KEY": "✓ Configured" if self.SUPABASE_ANON_KEY else "✗ Missing",
            "SUPABASE_SERVICE_ROLE_KEY": "✓ Configured" if self.SUPABASE_SERVICE_ROLE_KEY else "✗ Missing",
            "SUPABASE_JWT_SECRET": "✓ Configured" if self.SUPABASE_JWT_SECRET else "✗ Missing",
        }
        
        for key, status in config_status.items():
            logger.info(f"{key}: {status}")
        
        # Check for placeholder values without exposing them
        placeholder_warnings = []
        if self.SECRET_KEY in INSECURE_PLACEHOLDERS:
            placeholder_warnings.append("SECRET_KEY")
        if self.SUPABASE_URL in INSECURE_PLACEHOLDERS:
            placeholder_warnings.append("SUPABASE_URL") 
        if self.SUPABASE_ANON_KEY in INSECURE_PLACEHOLDERS:
            placeholder_warnings.append("SUPABASE_ANON_KEY")
        if self.SUPABASE_SERVICE_ROLE_KEY in INSECURE_PLACEHOLDERS:
            placeholder_warnings.append("SUPABASE_SERVICE_ROLE_KEY")
        if self.SUPABASE_JWT_SECRET in INSECURE_PLACEHOLDERS:
            placeholder_warnings.append("SUPABASE_JWT_SECRET")
        
        if placeholder_warnings:
            logger.warning(f"The following fields are using placeholder values: {', '.join(placeholder_warnings)}")
    
    class Config:
        env_file = ".env"
        case_sensitive = True
        # Allow environment variables to override settings
        env_prefix = ""


def create_settings() -> Settings:
    """
    Create and validate settings instance with comprehensive error handling.
    """
    try:
        settings = Settings()
        
        # Run production validation if in production
        if settings.ENVIRONMENT == "production":
            issues = settings.validate_production_requirements()
            critical_issues = [issue for issue in issues if issue.startswith("CRITICAL")]
            
            if critical_issues:
                raise ValueError(
                    "Critical configuration issues detected:\n" + 
                    "\n".join(critical_issues)
                )
        
        return settings
    except ValidationError as e:
        # Enhanced error message for validation failures
        error_details = []
        for error in e.errors():
            field = " -> ".join(str(x) for x in error["loc"])
            message = error["msg"]
            error_details.append(f"  {field}: {message}")
        
        raise ValueError(
            "Configuration validation failed:\n" + 
            "\n".join(error_details) +
            "\n\nPlease check your environment variables and .env file."
        ) from e


settings = create_settings()
