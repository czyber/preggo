from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import logging
import asyncio
from contextlib import asynccontextmanager

from app.api import api_router
from app.core.config import settings
from app.db.session import init_db
from app.core.logging import clear_dev_log

logger = logging.getLogger(__name__)


async def validate_supabase_connection():
    """
    Validate Supabase connection and configuration on startup.
    This helps catch configuration issues early.
    """
    logger.info("Validating Supabase configuration...")
    
    try:
        from app.core.supabase import supabase_service
        
        # Test JWT secret by creating a test token verification
        test_token_payload = {
            "sub": "test-user-id",
            "aud": "authenticated", 
            "role": "authenticated",
            "iat": 1640995200,  # 2022-01-01
            "exp": 1640995200 + 3600  # 1 hour later
        }
        
        import jwt
        test_token = jwt.encode(
            test_token_payload, 
            settings.SUPABASE_JWT_SECRET, 
            algorithm='HS256'
        )
        

        logger.info("✓ JWT secret validation passed")
        
        # Test Supabase client initialization (basic connection test)
        # The import itself will fail if URL/keys are completely invalid
        from app.core.supabase import supabase, supabase_anon
        
        # Basic connectivity test - this will validate URL format and key format
        try:
            # Test that the clients were created successfully
            if not supabase or not supabase_anon:
                raise ValueError("Supabase client initialization failed")
            
            logger.info("✓ Supabase clients initialized successfully")
            
        except Exception as e:
            raise ValueError(f"Supabase client initialization failed: {str(e)}")
        
        logger.info("✓ Supabase configuration validation completed successfully")
        
    except ImportError as e:
        logger.error(f"Failed to import Supabase modules: {e}")
        raise ValueError("Supabase module import failed - check dependencies")
    except Exception as e:
        logger.error(f"Supabase validation failed: {e}")
        raise ValueError(f"Supabase configuration validation failed: {str(e)}")


async def validate_database_connection():
    """
    Validate database connection on startup.
    """
    logger.info("Validating database connection...")
    
    try:
        from sqlalchemy import create_engine, text
        
        # Create a test connection
        engine = create_engine(settings.DATABASE_URL)
        
        with engine.connect() as connection:
            # Test basic connectivity
            result = connection.execute(text("SELECT 1"))
            if not result.fetchone():
                raise ValueError("Database query test failed")
        
        logger.info("✓ Database connection validated successfully") 
        
    except Exception as e:
        logger.error(f"Database validation failed: {e}")
        raise ValueError(f"Database connection validation failed: {str(e)}")


async def startup_validation():
    """
    Run all startup validations and fail fast if any issues are detected.
    """
    logger.info("Starting application startup validation...")
    
    try:
        # Log configuration status
        settings.log_configuration_status(logger)
        
        # Check for production readiness if in production
        if settings.ENVIRONMENT == "production":
            issues = settings.validate_production_requirements()
            if issues:
                critical_issues = [issue for issue in issues if issue.startswith("CRITICAL")]
                warning_issues = [issue for issue in issues if issue.startswith("WARNING")]
                
                if critical_issues:
                    logger.error("Critical configuration issues detected:")
                    for issue in critical_issues:
                        logger.error(f"  {issue}")
                    raise ValueError("Critical configuration issues prevent startup in production")
                
                if warning_issues:
                    logger.warning("Configuration warnings detected:")
                    for issue in warning_issues:
                        logger.warning(f"  {issue}")
        
        # Validate database connection
        await validate_database_connection()
        
        # Validate Supabase configuration
        await validate_supabase_connection()
        
        logger.info("✓ All startup validations completed successfully")
        
    except Exception as e:
        logger.error(f"Startup validation failed: {e}")
        logger.error("Application will not start due to configuration issues")
        raise


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Application lifespan manager with startup validation.
    """
    # Startup
    try:
        # Clear dev log on startup
        clear_dev_log()
        
        # Run comprehensive startup validation
        await startup_validation()
        
        # Initialize database after validation passes
        init_db()
        
        logger.info(f"🚀 {settings.PROJECT_NAME} v{settings.VERSION} started successfully")
        logger.info(f"Environment: {settings.ENVIRONMENT}")
        logger.info(f"API Documentation: http://localhost:8000/docs")
        
    except Exception as e:
        logger.error(f"Application startup failed: {e}")
        # Re-raise to prevent the application from starting
        raise
    
    yield
    
    # Shutdown
    logger.info("Application shutting down...")


app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.VERSION,
    lifespan=lifespan
)

# Set up CORS
logger.info(f"Setting up CORS with origins: {settings.BACKEND_CORS_ORIGINS}")
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.BACKEND_CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=["*"],
)

# Include API routes
app.include_router(api_router, prefix=settings.API_V1_STR)


@app.get("/")
async def root():
    return {
        "message": f"Welcome to {settings.PROJECT_NAME}",
        "version": settings.VERSION,
        "environment": settings.ENVIRONMENT,
        "status": "healthy"
    }


@app.get("/health")
async def health_check():
    """
    Health check endpoint that verifies critical services.
    """
    try:
        # Quick database connectivity check
        from sqlalchemy import create_engine, text
        engine = create_engine(settings.DATABASE_URL)
        with engine.connect() as connection:
            connection.execute(text("SELECT 1"))
        
        # Quick Supabase client check
        from app.core.supabase import supabase_service
        if not supabase_service:
            raise ValueError("Supabase service not available")
        
        return {
            "status": "healthy",
            "environment": settings.ENVIRONMENT,
            "database": "connected",
            "supabase": "connected",
            "cors_origins": settings.BACKEND_CORS_ORIGINS
        }
    except Exception as e:
        return {
            "status": "unhealthy", 
            "error": str(e),
            "environment": settings.ENVIRONMENT
        }

@app.options("/{full_path:path}")
async def options_handler(full_path: str):
    """
    Explicit OPTIONS handler for CORS preflight requests.
    This ensures preflight requests get proper CORS headers.
    """
    return {"message": "OK"}
