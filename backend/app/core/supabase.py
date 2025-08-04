"""
Supabase client configuration and utilities for the Preggo backend.

This module provides a configured Supabase client ONLY for:
- User authentication and JWT validation
- File storage operations

NOTE: Database operations are handled through SQLModel sessions, NOT Supabase client!
"""

from typing import Optional, Dict, Any, List
from supabase import create_client, Client
from gotrue import User
import jwt
from datetime import datetime
import logging
import asyncio
from functools import wraps
import time

from .config import settings

logger = logging.getLogger(__name__)


def handle_supabase_errors(func):
    """
    Decorator to handle common Supabase errors and provide better error messages.
    """
    @wraps(func)
    async def wrapper(*args, **kwargs):
        try:
            return await func(*args, **kwargs)
        except jwt.ExpiredSignatureError:
            logger.warning("JWT token has expired")
            return None
        except jwt.InvalidTokenError as e:
            logger.warning(f"Invalid JWT token: {e}")
            return None
        except Exception as e:
            logger.error(f"Supabase operation failed in {func.__name__}: {e}")
            return None
    return wrapper


def retry_on_failure(max_retries: int = 3, delay: float = 1.0):
    """
    Decorator to retry Supabase operations on failure.
    """
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            last_exception = None
            
            for attempt in range(max_retries):
                try:
                    return await func(*args, **kwargs)
                except Exception as e:
                    last_exception = e
                    if attempt < max_retries - 1:
                        logger.warning(f"Attempt {attempt + 1} failed for {func.__name__}: {e}. Retrying in {delay}s...")
                        await asyncio.sleep(delay * (attempt + 1))  # Exponential backoff
                    else:
                        logger.error(f"All {max_retries} attempts failed for {func.__name__}: {e}")
            
            raise last_exception
        return wrapper
    return decorator

# Initialize Supabase clients with proper error handling
def create_supabase_clients():
    """
    Create Supabase clients with proper error handling and validation.
    """
    try:
        logger.info("Initializing Supabase clients...")
        
        # Initialize client with service role key for backend operations
        service_client = create_client(
            supabase_url=settings.SUPABASE_URL,
            supabase_key=settings.SUPABASE_SERVICE_ROLE_KEY
        )
        
        # Initialize client with anon key for user-context operations  
        anon_client = create_client(
            supabase_url=settings.SUPABASE_URL,
            supabase_key=settings.SUPABASE_ANON_KEY
        )
        
        logger.info("✓ Supabase clients initialized successfully")
        return service_client, anon_client
        
    except Exception as e:
        logger.error(f"Failed to initialize Supabase clients: {e}")
        raise ValueError(f"Supabase client initialization failed: {str(e)}")


# Create clients
supabase, supabase_anon = create_supabase_clients()


class SupabaseService:
    """
    Service class for Supabase operations - AUTHENTICATION AND STORAGE ONLY.
    
    NOTE: This class should NOT perform any database operations.
    All database operations must use SQLModel sessions through proper service layers.
    """
    
    def __init__(self):
        self.client = supabase
        self.anon_client = supabase_anon
        self._last_health_check = 0
        self._health_check_interval = 300  # 5 minutes
        self._is_healthy = True
    
    async def health_check(self, force: bool = False) -> Dict[str, Any]:
        """
        Perform a comprehensive health check of Supabase services.
        
        Args:
            force: Force a new health check even if recently performed
            
        Returns:
            Health status dictionary
        """
        current_time = time.time()
        
        # Use cached result if recent and not forced
        if not force and (current_time - self._last_health_check) < self._health_check_interval:
            return {
                "status": "healthy" if self._is_healthy else "unhealthy",
                "cached": True,
                "last_check": self._last_health_check
            }
        
        logger.info("Performing Supabase health check...")
        health_status = {
            "status": "healthy",
            "timestamp": current_time,
            "checks": {}
        }
        
        try:
            # Test JWT secret validation
            test_payload = {
                "sub": "health-check-user",
                "aud": "authenticated",
                "role": "authenticated", 
                "iat": int(current_time),
                "exp": int(current_time) + 3600
            }
            
            test_token = jwt.encode(
                test_payload,
                settings.SUPABASE_JWT_SECRET,
                algorithm='HS256'
            )
            
            decoded = self.verify_jwt_token(test_token)
            if decoded and decoded.get("sub") == "health-check-user":
                health_status["checks"]["jwt_validation"] = "✓ passed"
            else:
                health_status["checks"]["jwt_validation"] = "✗ failed"
                health_status["status"] = "unhealthy"
            
            # Test client initialization
            if self.client and self.anon_client:
                health_status["checks"]["client_initialization"] = "✓ passed"
            else:
                health_status["checks"]["client_initialization"] = "✗ failed"
                health_status["status"] = "unhealthy"
            
            # Update health status
            self._is_healthy = health_status["status"] == "healthy"
            self._last_health_check = current_time
            
            if self._is_healthy:
                logger.info("✓ Supabase health check passed")
            else:
                logger.warning("✗ Supabase health check failed")
            
        except Exception as e:
            logger.error(f"Supabase health check failed: {e}")
            health_status["status"] = "unhealthy"
            health_status["error"] = str(e)
            self._is_healthy = False
            self._last_health_check = current_time
        
        return health_status
    
    def verify_jwt_token(self, token: str) -> Optional[Dict[str, Any]]:
        """
        Verify a JWT token from the frontend and extract user information.
        
        Args:
            token: JWT token from Authorization header
            
        Returns:
            User information dict or None if invalid
        """
        if not token or token.strip() == "":
            logger.debug("Empty token provided for verification")
            return None
            
        try:
            # Remove 'Bearer ' prefix if present
            if token.startswith('Bearer '):
                token = token[7:]
            
            # Basic format validation
            if len(token.split('.')) != 3:
                logger.warning("Invalid JWT format - token must have 3 parts")
                return None
            
            # Decode and verify the JWT token
            payload = jwt.decode(
                token, 
                settings.SUPABASE_JWT_SECRET, 
                algorithms=['HS256'],
                audience='authenticated'
            )
            
            # Additional validation
            if not payload.get('sub'):
                logger.warning("JWT token missing required 'sub' claim")
                return None
            
            # Check token expiration more explicitly
            exp = payload.get('exp')
            if exp and exp < time.time():
                logger.warning("JWT token has expired")
                return None
            
            return payload
            
        except jwt.ExpiredSignatureError:
            logger.warning("JWT token has expired")
            return None
        except jwt.InvalidTokenError as e:
            logger.warning(f"Invalid JWT token: {e}")
            return None
        except Exception as e:
            logger.error(f"Unexpected error verifying JWT token: {e}")
            return None
    
    @retry_on_failure(max_retries=3, delay=1.0)
    async def upload_file(self, bucket: str, file_path: str, file_data: bytes, content_type: str = None) -> Optional[str]:
        """
        Upload a file to Supabase Storage with retry logic.
        
        Args:
            bucket: Storage bucket name
            file_path: Path within the bucket
            file_data: File content as bytes
            content_type: MIME type of the file
            
        Returns:
            Public URL of the uploaded file or None if failed
        """
        if not bucket or not file_path or not file_data:
            logger.error("Invalid parameters for file upload")
            return None
        
        if len(file_data) > settings.MAX_FILE_SIZE:
            logger.error(f"File size {len(file_data)} exceeds maximum allowed size {settings.MAX_FILE_SIZE}")
            return None
        
        try:
            logger.info(f"Uploading file to {bucket}/{file_path} ({len(file_data)} bytes)")
            
            response = self.client.storage.from_(bucket).upload(
                path=file_path,
                file=file_data,
                file_options={"content-type": content_type} if content_type else None
            )
            
            if response:
                # Get public URL
                public_url = self.client.storage.from_(bucket).get_public_url(file_path)
                logger.info(f"File uploaded successfully: {public_url}")
                return public_url
            
            logger.error("Upload response was empty or invalid")
            return None
            
        except Exception as e:
            logger.error(f"Error uploading file to storage: {e}")
            raise  # Let retry decorator handle this
    
    @retry_on_failure(max_retries=3, delay=1.0)
    async def delete_file(self, bucket: str, file_path: str) -> bool:
        """
        Delete a file from Supabase Storage with retry logic.
        
        Args:
            bucket: Storage bucket name
            file_path: Path within the bucket
            
        Returns:
            True if successful, False otherwise
        """
        if not bucket or not file_path:
            logger.error("Invalid parameters for file deletion")
            return False
        
        try:
            logger.info(f"Deleting file from {bucket}/{file_path}")
            response = self.client.storage.from_(bucket).remove([file_path])
            
            if response:
                logger.info(f"File deleted successfully: {bucket}/{file_path}")
                return True
            
            logger.error("Delete response was empty or invalid")
            return False
            
        except Exception as e:
            logger.error(f"Error deleting file from storage: {e}")
            raise  # Let retry decorator handle this
    
    @retry_on_failure(max_retries=3, delay=1.0)
    async def get_file_url(self, bucket: str, file_path: str, expires_in: int = 3600) -> Optional[str]:
        """
        Get a signed URL for a private file with retry logic.
        
        Args:
            bucket: Storage bucket name
            file_path: Path within the bucket
            expires_in: URL expiration time in seconds (max 7 days)
            
        Returns:
            Signed URL or None if failed
        """
        if not bucket or not file_path:
            logger.error("Invalid parameters for signed URL generation")
            return None
        
        # Validate expiration time (Supabase has limits)
        max_expires_in = 7 * 24 * 3600  # 7 days
        if expires_in > max_expires_in:
            logger.warning(f"Expires_in {expires_in} exceeds maximum, using {max_expires_in}")
            expires_in = max_expires_in
        
        try:
            logger.debug(f"Creating signed URL for {bucket}/{file_path} (expires in {expires_in}s)")
            
            response = self.client.storage.from_(bucket).create_signed_url(
                path=file_path,
                expires_in=expires_in
            )
            
            signed_url = response.get('signedURL') if response else None
            if signed_url:
                logger.debug(f"Signed URL created successfully")
                return signed_url
            
            logger.error("Signed URL response was empty or invalid")
            return None
            
        except Exception as e:
            logger.error(f"Error creating signed URL: {e}")
            raise  # Let retry decorator handle this


# Create a global instance of the service
supabase_service = SupabaseService()


# FastAPI Dependencies for authentication
from fastapi import Depends, HTTPException, status, Header
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

security = HTTPBearer(auto_error=False)

async def get_current_user(
    authorization: Optional[str] = Header(None),
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(security)
) -> Optional[Dict[str, Any]]:
    """
    FastAPI dependency to get the current authenticated user.
    Supports both Authorization header and HTTPBearer security scheme.
    
    NOTE: This only verifies the JWT token. Additional user data should be
    fetched from the database using SQLModel sessions in service layers.
    
    Args:
        authorization: Authorization header with Bearer token
        credentials: HTTPBearer credentials
        
    Returns:
        User information dict from JWT or None if not authenticated
    """
    token = None
    
    # Try to get token from credentials first, then from header
    if credentials:
        token = credentials.credentials
    elif authorization:
        token = authorization
    
    if not token:
        return None
    
    user_data = supabase_service.verify_jwt_token(token)
    return user_data


async def get_current_user_required(
    current_user: Optional[Dict[str, Any]] = Depends(get_current_user)
) -> Dict[str, Any]:
    """
    FastAPI dependency that requires authentication.
    Raises HTTPException if user is not authenticated.
    
    Args:
        current_user: Current user from get_current_user dependency
        
    Returns:
        User information dict
        
    Raises:
        HTTPException: If user is not authenticated
    """
    if not current_user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication required",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return current_user


async def get_current_active_user(
    current_user: Dict[str, Any] = Depends(get_current_user_required)
) -> Dict[str, Any]:
    """
    FastAPI dependency that requires an active user.
    
    Args:
        current_user: Current user from get_current_user_required dependency
        
    Returns:
        Active user information dict
        
    Raises:
        HTTPException: If user is not active
    """
    if not current_user.get("is_active", True):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Inactive user"
        )
    return current_user


# NOTE: Ownership checks and other database operations should be implemented
# in proper service layers using SQLModel sessions, not here.