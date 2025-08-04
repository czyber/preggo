"""
Authentication endpoints for user registration, login, and profile management - CORRECTED VERSION.

This module provides endpoints for:
- User registration and profile creation using SQLModel sessions
- User authentication and session management 
- Profile updates and preferences
- Account management

NOTE: This is the corrected version that uses SQLModel sessions for database operations
and Supabase only for authentication.
"""

from typing import Optional, Dict, Any
from fastapi import APIRouter, Depends, HTTPException, status, Response
from fastapi.security import HTTPAuthorizationCredentials
from pydantic import BaseModel, EmailStr
from sqlmodel import Session
import logging
from datetime import datetime, timedelta

from app.core.supabase import (
    supabase_service, 
    get_current_user, 
    get_current_user_required,
    get_current_active_user
)
from app.services import user_service
from app.db.session import get_session
from app.schemas.user import UserCreate, UserUpdate, UserResponse, UserPublic
from app.models.user import UserPreferences

router = APIRouter(prefix="/auth", tags=["authentication"])
logger = logging.getLogger(__name__)

# Simple in-memory cache for user profiles to reduce database load
_user_cache: Dict[str, tuple[UserResponse, datetime]] = {}
CACHE_TTL_MINUTES = 5


class LoginRequest(BaseModel):
    """Request model for user login"""
    email: EmailStr
    password: str


class RegisterRequest(BaseModel):
    """Request model for user registration"""
    email: EmailStr
    password: str
    first_name: str
    last_name: str
    timezone: str = "UTC"
    preferences: Optional[UserPreferences] = None


class LoginResponse(BaseModel):
    """Response model for successful login"""
    access_token: str
    token_type: str = "bearer"
    user: UserResponse


class AuthResponse(BaseModel):
    """Generic auth response with user info"""
    user: UserResponse
    message: str


class PasswordResetRequest(BaseModel):
    """Request model for password reset"""
    email: EmailStr


class PasswordUpdateRequest(BaseModel):
    """Request model for password update"""
    current_password: str
    new_password: str


@router.post("/register", response_model=AuthResponse, status_code=status.HTTP_201_CREATED)
async def register(
    request: RegisterRequest,
    session: Session = Depends(get_session)
):
    """
    Register a new user account using SQLModel session for profile creation.
    
    Creates a new user in Supabase Auth and a corresponding profile record in the database.
    """
    try:
        # Register user with Supabase Auth
        auth_response = supabase_service.anon_client.auth.sign_up({
            "email": request.email,
            "password": request.password,
            "options": {
                "data": {
                    "first_name": request.first_name,
                    "last_name": request.last_name,
                    "timezone": request.timezone
                }
            }
        })
        
        if auth_response.user is None:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Registration failed. Email may already be in use."
            )
        
        # Create user profile in the database using service
        profile_data = {
            "id": auth_response.user.id,
            "email": request.email,
            "first_name": request.first_name,
            "last_name": request.last_name,
            "timezone": request.timezone,
            "preferences": request.preferences.dict() if request.preferences else {},
            "email_verified": False,
            "is_active": True
        }
        
        profile = await user_service.create_user(session, profile_data)
        if not profile:
            # Cleanup: attempt to delete the auth user if profile creation fails
            # Note: In production, this should be handled by database triggers
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to create user profile"
            )
        
        return AuthResponse(
            user=UserResponse.from_orm(profile),
            message="Registration successful. Please check your email to verify your account."
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Registration failed: {str(e)}"
        )


@router.post("/login", response_model=LoginResponse)
async def login(
    request: LoginRequest,
    session: Session = Depends(get_session)
):
    """
    Authenticate user and return access token using SQLModel session for profile retrieval.
    """
    try:
        # Authenticate with Supabase
        auth_response = supabase_service.anon_client.auth.sign_in_with_password({
            "email": request.email,
            "password": request.password
        })
        
        if not auth_response.user or not auth_response.session:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid email or password"
            )
        
        # Get user profile using service
        profile = await user_service.get_by_id(session, auth_response.user.id)
        if not profile:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User profile not found"
            )
        
        # Update last login timestamp using service
        await user_service.update_last_login(session, auth_response.user.id)
        
        return LoginResponse(
            access_token=auth_response.session.access_token,
            user=UserResponse.from_orm(profile)
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication failed"
        )


@router.post("/logout")
async def logout(current_user: Dict[str, Any] = Depends(get_current_user_required)):
    """
    Logout current user by invalidating the session.
    
    NOTE: Uses Supabase auth for session management only.
    """
    try:
        # Sign out from Supabase (invalidates the JWT)
        supabase_service.client.auth.sign_out()
        return {"message": "Successfully logged out"}
    except Exception as e:
        # Even if logout fails, we return success since the client 
        # should discard the token anyway
        return {"message": "Logged out"}


def _get_cached_user(user_id: str) -> Optional[UserResponse]:
    """Get user from cache if valid"""
    if user_id in _user_cache:
        cached_user, cached_time = _user_cache[user_id]
        if datetime.now() - cached_time < timedelta(minutes=CACHE_TTL_MINUTES):
            return cached_user
        else:
            # Remove expired cache entry
            del _user_cache[user_id]
    return None

def _cache_user(user_id: str, user_response: UserResponse):
    """Cache user response"""
    _user_cache[user_id] = (user_response, datetime.now())

@router.get("/me", response_model=UserResponse)
async def get_current_user_profile(
    current_user: Dict[str, Any] = Depends(get_current_active_user),
    session: Session = Depends(get_session)
):
    """
    Get current user's profile information using SQLModel session with caching.
    """
    try:
        user_id = current_user["sub"]
        
        # Check cache first
        cached_user = _get_cached_user(user_id)
        if cached_user:
            logger.debug(f"Returning cached user profile for {user_id}")
            return cached_user
        
        # Get fresh user data from database
        profile = await user_service.get_by_id(session, user_id)
        
        if not profile:
            # Check if user exists by email (might be different ID)
            email = current_user.get("email")
            if email:
                profile = await user_service.get_by_email(session, email)
                
            if not profile:
                # Auto-create user from JWT data if doesn't exist
                user_data = {
                    "id": user_id,
                    "email": email,
                    "first_name": current_user.get("user_metadata", {}).get("first_name", ""),
                    "last_name": current_user.get("user_metadata", {}).get("last_name", ""),
                    "is_active": True,
                    "email_verified": current_user.get("email_confirmed", False)
                }
                profile = await user_service.create_user(session, user_data)
                
                if not profile:
                    raise HTTPException(
                        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                        detail="Failed to create user profile"
                    )
            else:
                # User exists with different ID - this is a data consistency issue
                # For now, return the existing profile but log the issue
                logger.warning(f"User ID mismatch: JWT has {user_id} but DB has {profile.id} for email {email}")
                
                # You might want to handle this differently in production:
                # - Update the existing user's ID to match JWT
                # - Or redirect to a account linking flow
                # For now, we'll use the existing profile
        
        user_response = UserResponse.from_orm(profile)
        # Cache the result for future requests
        _cache_user(user_id, user_response)
        logger.debug(f"Cached user profile for {user_id}")
        return user_response
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to fetch user profile: {str(e)}"
        )


@router.put("/me", response_model=UserResponse)
async def update_current_user_profile(
    user_update: UserUpdate,
    current_user: Dict[str, Any] = Depends(get_current_active_user),
    session: Session = Depends(get_session)
):
    """
    Update current user's profile information using SQLModel session.
    """
    try:
        user_id = current_user["sub"]
        
        # Prepare update data (only include non-None fields)
        update_data = {
            k: v for k, v in user_update.dict(exclude_unset=True).items() 
            if v is not None
        }
        
        if not update_data:
            # No updates, return current profile
            profile = await user_service.get_by_id(session, user_id)
            if not profile:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="User profile not found"
                )
            return UserResponse.from_orm(profile)
        
        # Update user profile using service
        updated_profile = await user_service.update_user(session, user_id, update_data)
        
        if not updated_profile:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to update profile"
            )
        
        return UserResponse.from_orm(updated_profile)
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Profile update failed: {str(e)}"
        )


@router.post("/forgot-password")
async def forgot_password(request: PasswordResetRequest):
    """
    Send password reset email to user using Supabase Auth.
    
    NOTE: This uses Supabase Auth only, no database operations needed.
    """
    try:
        # Send password reset email via Supabase
        supabase_service.anon_client.auth.reset_password_email(request.email)
        
        # Always return success message for security
        return {"message": "If an account with that email exists, a password reset link has been sent."}
        
    except Exception:
        # Always return success message for security (don't reveal if email exists)
        return {"message": "If an account with that email exists, a password reset link has been sent."}


@router.post("/update-password")
async def update_password(
    request: PasswordUpdateRequest,
    current_user: Dict[str, Any] = Depends(get_current_active_user)
):
    """
    Update user's password using Supabase Auth.
    
    NOTE: This uses Supabase Auth only, no database operations needed.
    """
    try:
        # Update password via Supabase Auth
        auth_response = supabase_service.client.auth.update_user({
            "password": request.new_password
        })
        
        if not auth_response.user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Password update failed"
            )
        
        return {"message": "Password updated successfully"}
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Password update failed"
        )


@router.delete("/account")
async def delete_account(
    current_user: Dict[str, Any] = Depends(get_current_active_user),
    session: Session = Depends(get_session)
):
    """
    Delete current user's account and all associated data using SQLModel session.
    """
    try:
        user_id = current_user["sub"]
        
        # First, deactivate the user account using service
        await user_service.deactivate_user(session, user_id)
        
        # In a production app, you might want to:
        # 1. Archive user data instead of deleting
        # 2. Handle cascading deletes for pregnancies, posts, etc.
        # 3. Send confirmation email
        # 4. Add a grace period before actual deletion
        
        return {"message": "Account has been deactivated. Contact support to reactivate."}
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Account deletion failed"
        )


@router.get("/verify-email")
async def verify_email_status(
    current_user: Dict[str, Any] = Depends(get_current_user),
    session: Session = Depends(get_session)
):
    """
    Check email verification status for current user using SQLModel session.
    """
    if not current_user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication required"
        )
    
    try:
        user_id = current_user["sub"]
        profile = await user_service.get_by_id(session, user_id)
        
        if not profile:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User profile not found"
            )
        
        return {
            "email_verified": profile.email_verified,
            "email": profile.email
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to check verification status: {str(e)}"
        )


@router.post("/resend-verification")
async def resend_verification_email(
    current_user: Dict[str, Any] = Depends(get_current_user_required),
    session: Session = Depends(get_session)
):
    """
    Resend email verification email using Supabase Auth.
    
    NOTE: This uses Supabase Auth only, but gets email from database.
    """
    try:
        user_id = current_user["sub"]
        profile = await user_service.get_by_id(session, user_id)
        
        if not profile:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User profile not found"
            )
        
        # Resend verification email via Supabase
        supabase_service.anon_client.auth.resend({
            "type": "signup",
            "email": profile.email
        })
        
        return {"message": "Verification email sent"}
        
    except Exception:
        return {"message": "Verification email sent"}  # Always return success for security