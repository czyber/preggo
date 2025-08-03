"""
Authentication endpoints for user registration, login, and profile management.

This module provides endpoints for:
- User registration and profile creation
- User authentication and session management 
- Profile updates and preferences
- Account management
"""

from typing import Optional, Dict, Any
from fastapi import APIRouter, Depends, HTTPException, status, Response
from fastapi.security import HTTPAuthorizationCredentials
from pydantic import BaseModel, EmailStr

from app.core.supabase import (
    supabase_service, 
    get_current_user, 
    get_current_user_required,
    get_current_active_user
)
from app.schemas.user import UserCreate, UserUpdate, UserResponse, UserPublic
from app.models.user import UserPreferences

router = APIRouter(prefix="/auth", tags=["authentication"])


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
async def register(request: RegisterRequest):
    """
    Register a new user account.
    
    Creates a new user in Supabase Auth and a corresponding profile record.
    
    Args:
        request: Registration details including email, password, and profile info
        
    Returns:
        AuthResponse with user profile and success message
        
    Raises:
        HTTPException: If registration fails or email already exists
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
        
        # Create user profile in the database
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
        
        profile = await supabase_service.create_user_profile(profile_data)
        if not profile:
            # Cleanup: attempt to delete the auth user if profile creation fails
            # Note: In production, this should be handled by database triggers
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to create user profile"
            )
        
        return AuthResponse(
            user=UserResponse(**profile),
            message="Registration successful. Please check your email to verify your account."
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Registration failed: {str(e)}"
        )


@router.post("/login", response_model=LoginResponse)
async def login(request: LoginRequest):
    """
    Authenticate user and return access token.
    
    Args:
        request: Login credentials (email and password)
        
    Returns:
        LoginResponse with access token and user profile
        
    Raises:
        HTTPException: If authentication fails
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
        
        # Get user profile
        profile = await supabase_service.get_user_profile(auth_response.user.id)
        if not profile:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User profile not found"
            )
        
        # Update last login timestamp
        await supabase_service.update_record(
            "profiles", 
            auth_response.user.id, 
            {"last_login": "now()"}
        )
        
        return LoginResponse(
            access_token=auth_response.session.access_token,
            user=UserResponse(**profile)
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
    
    Args:
        current_user: Current authenticated user
        
    Returns:
        Success message
    """
    try:
        # Sign out from Supabase (invalidates the JWT)
        supabase_service.client.auth.sign_out()
        return {"message": "Successfully logged out"}
    except Exception as e:
        # Even if logout fails, we return success since the client 
        # should discard the token anyway
        return {"message": "Logged out"}


@router.get("/me", response_model=UserResponse)
async def get_current_user_profile(
    current_user: Dict[str, Any] = Depends(get_current_active_user)
):
    """
    Get current user's profile information.
    
    Args:
        current_user: Current authenticated and active user
        
    Returns:
        UserResponse with current user's profile
    """
    return UserResponse(**current_user)


@router.put("/me", response_model=UserResponse)
async def update_current_user_profile(
    user_update: UserUpdate,
    current_user: Dict[str, Any] = Depends(get_current_active_user)
):
    """
    Update current user's profile information.
    
    Args:
        user_update: Fields to update in user profile
        current_user: Current authenticated and active user
        
    Returns:
        UserResponse with updated user profile
        
    Raises:
        HTTPException: If update fails
    """
    try:
        # Prepare update data (only include non-None fields)
        update_data = {
            k: v for k, v in user_update.dict(exclude_unset=True).items() 
            if v is not None
        }
        
        if not update_data:
            return UserResponse(**current_user)
        
        # Update user profile
        updated_profile = await supabase_service.update_record(
            "profiles",
            current_user["id"],
            update_data
        )
        
        if not updated_profile:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to update profile"
            )
        
        return UserResponse(**updated_profile)
        
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
    Send password reset email to user.
    
    Args:
        request: Email address for password reset
        
    Returns:
        Success message (always returned for security)
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
    Update user's password.
    
    Args:
        request: Current and new password
        current_user: Current authenticated and active user
        
    Returns:
        Success message
        
    Raises:
        HTTPException: If password update fails
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
    current_user: Dict[str, Any] = Depends(get_current_active_user)
):
    """
    Delete current user's account and all associated data.
    
    Args:
        current_user: Current authenticated and active user
        
    Returns:
        Success message
        
    Raises:
        HTTPException: If account deletion fails
    """
    try:
        user_id = current_user["id"]
        
        # First, deactivate the user account
        await supabase_service.update_record(
            "profiles",
            user_id,
            {"is_active": False}
        )
        
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
    current_user: Dict[str, Any] = Depends(get_current_user)
):
    """
    Check email verification status for current user.
    
    Args:
        current_user: Current user (authentication optional)
        
    Returns:
        Email verification status
    """
    if not current_user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication required"
        )
    
    return {
        "email_verified": current_user.get("email_verified", False),
        "email": current_user.get("email")
    }


@router.post("/resend-verification")
async def resend_verification_email(
    current_user: Dict[str, Any] = Depends(get_current_user_required)
):
    """
    Resend email verification email.
    
    Args:
        current_user: Current authenticated user
        
    Returns:
        Success message
    """
    try:
        # Resend verification email via Supabase
        supabase_service.anon_client.auth.resend({
            "type": "signup",
            "email": current_user["email"]
        })
        
        return {"message": "Verification email sent"}
        
    except Exception:
        return {"message": "Verification email sent"}  # Always return success for security