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

from .config import settings

logger = logging.getLogger(__name__)

# Initialize Supabase client with service role key for backend operations
supabase: Client = create_client(
    supabase_url=settings.SUPABASE_URL,
    supabase_key=settings.SUPABASE_SERVICE_ROLE_KEY  # Using service role for backend
)

# Initialize client with anon key for user-context operations
supabase_anon: Client = create_client(
    supabase_url=settings.SUPABASE_URL,
    supabase_key=settings.SUPABASE_ANON_KEY
)


class SupabaseService:
    """
    Service class for Supabase operations - AUTHENTICATION AND STORAGE ONLY.
    
    NOTE: This class should NOT perform any database operations.
    All database operations must use SQLModel sessions through proper service layers.
    """
    
    def __init__(self):
        self.client = supabase
        self.anon_client = supabase_anon
    
    def verify_jwt_token(self, token: str) -> Optional[Dict[str, Any]]:
        """
        Verify a JWT token from the frontend and extract user information.
        
        Args:
            token: JWT token from Authorization header
            
        Returns:
            User information dict or None if invalid
        """
        try:
            # Remove 'Bearer ' prefix if present
            if token.startswith('Bearer '):
                token = token[7:]
            
            # Decode and verify the JWT token
            payload = jwt.decode(
                token, 
                settings.SUPABASE_JWT_SECRET, 
                algorithms=['HS256'],
                audience='authenticated'
            )
            
            return payload
        except jwt.ExpiredSignatureError:
            logger.warning("JWT token has expired")
            return None
        except jwt.InvalidTokenError as e:
            logger.warning(f"Invalid JWT token: {e}")
            return None
        except Exception as e:
            logger.error(f"Error verifying JWT token: {e}")
            return None
    
    async def upload_file(self, bucket: str, file_path: str, file_data: bytes, content_type: str = None) -> Optional[str]:
        """
        Upload a file to Supabase Storage.
        
        Args:
            bucket: Storage bucket name
            file_path: Path within the bucket
            file_data: File content as bytes
            content_type: MIME type of the file
            
        Returns:
            Public URL of the uploaded file or None if failed
        """
        try:
            response = self.client.storage.from_(bucket).upload(
                path=file_path,
                file=file_data,
                file_options={"content-type": content_type} if content_type else None
            )
            
            if response:
                # Get public URL
                public_url = self.client.storage.from_(bucket).get_public_url(file_path)
                return public_url
            return None
        except Exception as e:
            logger.error(f"Error uploading file to storage: {e}")
            return None
    
    async def delete_file(self, bucket: str, file_path: str) -> bool:
        """
        Delete a file from Supabase Storage.
        
        Args:
            bucket: Storage bucket name
            file_path: Path within the bucket
            
        Returns:
            True if successful, False otherwise
        """
        try:
            response = self.client.storage.from_(bucket).remove([file_path])
            return True
        except Exception as e:
            logger.error(f"Error deleting file from storage: {e}")
            return False
    
    async def get_file_url(self, bucket: str, file_path: str, expires_in: int = 3600) -> Optional[str]:
        """
        Get a signed URL for a private file.
        
        Args:
            bucket: Storage bucket name
            file_path: Path within the bucket
            expires_in: URL expiration time in seconds
            
        Returns:
            Signed URL or None if failed
        """
        try:
            response = self.client.storage.from_(bucket).create_signed_url(
                path=file_path,
                expires_in=expires_in
            )
            return response.get('signedURL')
        except Exception as e:
            logger.error(f"Error creating signed URL: {e}")
            return None


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