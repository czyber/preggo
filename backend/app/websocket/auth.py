"""
WebSocket authentication utilities.

Handles JWT token validation and user authentication for WebSocket connections,
ensuring secure family-based room access and proper authorization.
"""

from typing import Optional, Dict, Any, List
from fastapi import WebSocket, HTTPException, status
from fastapi.security.utils import get_authorization_scheme_param
import logging
import jwt
from datetime import datetime

from app.core.config import settings
from app.core.supabase import supabase_service

logger = logging.getLogger(__name__)


class WebSocketAuthError(Exception):
    """Custom exception for WebSocket authentication errors"""
    def __init__(self, message: str, code: str = "auth_error"):
        self.message = message
        self.code = code
        super().__init__(self.message)


async def authenticate_websocket_connection(websocket: WebSocket) -> Dict[str, Any]:
    """
    Authenticate WebSocket connection using JWT token from query parameters or headers.
    
    Returns user information if authentication is successful, raises WebSocketAuthError if not.
    """
    token = None
    
    try:
        # Try to get token from query parameters first
        token = websocket.query_params.get("token")
        
        # If not in query params, try Authorization header
        if not token:
            auth_header = websocket.headers.get("authorization")
            if auth_header:
                scheme, token = get_authorization_scheme_param(auth_header)
                if scheme.lower() != "bearer":
                    token = None
        
        if not token:
            raise WebSocketAuthError(
                "No authentication token provided. Use ?token=<jwt> or Authorization header.",
                "missing_token"
            )
        
        # Verify JWT token using Supabase service
        try:
            # Decode and verify the JWT token
            payload = jwt.decode(
                token,
                settings.SUPABASE_JWT_SECRET,
                algorithms=['HS256'],
                audience="authenticated"
            )
            
            # Validate token expiration
            if payload.get('exp', 0) < datetime.utcnow().timestamp():
                raise WebSocketAuthError("Token has expired", "token_expired")
            
            # Validate token type and role
            if payload.get('aud') != 'authenticated':
                raise WebSocketAuthError("Invalid token audience", "invalid_token")
            
            if payload.get('role') != 'authenticated':
                raise WebSocketAuthError("Invalid token role", "invalid_token")
            
            # Extract user information
            user_data = {
                'sub': payload.get('sub'),
                'email': payload.get('email'),
                'aud': payload.get('aud'),
                'role': payload.get('role'),
                'iat': payload.get('iat'),
                'exp': payload.get('exp'),
                'user_metadata': payload.get('user_metadata', {}),
                'app_metadata': payload.get('app_metadata', {})
            }
            
            if not user_data['sub']:
                raise WebSocketAuthError("Token missing user ID", "invalid_token")
            
            logger.info(f"WebSocket authentication successful for user {user_data['sub']}")
            return user_data
            
        except jwt.InvalidTokenError as e:
            logger.warning(f"JWT validation failed: {str(e)}")
            raise WebSocketAuthError(f"Invalid token: {str(e)}", "invalid_token")
        
    except WebSocketAuthError:
        raise
    except Exception as e:
        logger.error(f"WebSocket authentication error: {str(e)}")
        raise WebSocketAuthError(f"Authentication failed: {str(e)}", "auth_error")


async def get_user_family_permissions(user_id: str, pregnancy_id: str) -> Dict[str, Any]:
    """
    Get user's permissions for a specific pregnancy's family groups.
    
    Returns permission information including accessible rooms and permission levels.
    """
    from app.services.family_service import family_service
    from app.db.session import get_session
    from app.models.family import MemberPermission
    
    try:
        # Get database session - we'll need to handle this differently in WebSocket context
        # For now, we'll create a session inline - in production, consider dependency injection
        from sqlmodel import Session, create_engine
        engine = create_engine(settings.DATABASE_URL)
        
        permissions_info = {
            'pregnancy_id': pregnancy_id,
            'user_permissions': [],
            'accessible_rooms': [],
            'permission_levels': {},
            'is_family_member': False
        }
        
        async with Session(engine) as session:
            # Check if user is a family member for this pregnancy
            family_member = await family_service.get_family_member_by_user_and_pregnancy(
                session, user_id, pregnancy_id
            )
            
            if not family_member:
                logger.warning(f"User {user_id} is not a family member for pregnancy {pregnancy_id}")
                return permissions_info
            
            permissions_info['is_family_member'] = True
            permissions_info['user_permissions'] = family_member.permissions
            
            # Get family groups this user belongs to
            family_groups = await family_service.get_user_family_groups(
                session, user_id, pregnancy_id
            )
            
            for group in family_groups:
                room_id = f"pregnancy-{pregnancy_id}-{group.id}"
                permissions_info['accessible_rooms'].append(room_id)
                permissions_info['permission_levels'][room_id] = {
                    'role': family_member.role,
                    'permissions': family_member.permissions,
                    'group_type': group.type,
                    'group_permissions': group.permissions.dict() if group.permissions else {}
                }
        
        return permissions_info
        
    except Exception as e:
        logger.error(f"Error getting family permissions for user {user_id}: {str(e)}")
        return {
            'pregnancy_id': pregnancy_id,
            'user_permissions': [],
            'accessible_rooms': [],
            'permission_levels': {},
            'is_family_member': False,
            'error': str(e)
        }


async def validate_room_access(
    user_id: str, 
    room_id: str, 
    required_permission: Optional[str] = None
) -> bool:
    """
    Validate if user has access to a specific room and optional permission.
    
    Room ID format: "pregnancy-{pregnancy_id}" or "pregnancy-{pregnancy_id}-{group_id}"
    """
    try:
        # Parse room ID to extract pregnancy ID
        parts = room_id.split('-')
        if len(parts) < 2 or parts[0] != 'pregnancy':
            logger.warning(f"Invalid room ID format: {room_id}")
            return False
        
        pregnancy_id = parts[1]
        
        # Get user's family permissions for this pregnancy
        permissions_info = await get_user_family_permissions(user_id, pregnancy_id)
        
        if not permissions_info['is_family_member']:
            logger.warning(f"User {user_id} not authorized for pregnancy {pregnancy_id}")
            return False
        
        # Check if user has access to this specific room
        if room_id not in permissions_info['accessible_rooms']:
            logger.warning(f"User {user_id} not authorized for room {room_id}")
            return False
        
        # Check specific permission if required
        if required_permission:
            user_permissions = permissions_info['user_permissions']
            if required_permission not in user_permissions:
                logger.warning(f"User {user_id} missing permission {required_permission} for room {room_id}")
                return False
        
        logger.debug(f"User {user_id} authorized for room {room_id}")
        return True
        
    except Exception as e:
        logger.error(f"Error validating room access for user {user_id}, room {room_id}: {str(e)}")
        return False


def get_user_display_name(user_data: Dict[str, Any]) -> str:
    """Extract user display name from authentication data"""
    metadata = user_data.get('user_metadata', {})
    
    # Try different name fields
    if metadata.get('first_name') and metadata.get('last_name'):
        return f"{metadata['first_name']} {metadata['last_name']}"
    elif metadata.get('full_name'):
        return metadata['full_name']
    elif metadata.get('name'):
        return metadata['name']
    elif metadata.get('first_name'):
        return metadata['first_name']
    else:
        # Fallback to email prefix
        email = user_data.get('email', '')
        return email.split('@')[0] if email else 'Unknown User'


def get_pregnancy_room_id(pregnancy_id: str, group_id: Optional[str] = None) -> str:
    """Generate room ID for a pregnancy and optional family group"""
    if group_id:
        return f"pregnancy-{pregnancy_id}-{group_id}"
    else:
        return f"pregnancy-{pregnancy_id}"


async def get_user_authorized_rooms(user_id: str) -> List[str]:
    """
    Get all rooms a user is authorized to access across all their pregnancies.
    """
    from app.services.family_service import family_service
    from app.db.session import get_session
    from sqlmodel import Session, create_engine
    
    try:
        engine = create_engine(settings.DATABASE_URL)
        authorized_rooms = []
        
        async with Session(engine) as session:
            # Get all pregnancies where user is a family member
            user_memberships = await family_service.get_user_family_memberships(session, user_id)
            
            for membership in user_memberships:
                pregnancy_id = membership.pregnancy_id
                group_id = membership.group_id
                
                # Add general pregnancy room
                pregnancy_room = get_pregnancy_room_id(pregnancy_id)
                if pregnancy_room not in authorized_rooms:
                    authorized_rooms.append(pregnancy_room)
                
                # Add specific group room
                group_room = get_pregnancy_room_id(pregnancy_id, group_id)
                authorized_rooms.append(group_room)
        
        return authorized_rooms
        
    except Exception as e:
        logger.error(f"Error getting authorized rooms for user {user_id}: {str(e)}")
        return []