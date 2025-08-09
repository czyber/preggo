"""
WebSocket connection manager for real-time Instagram-like feed features.

Manages WebSocket connections, message broadcasting, and room management
for pregnancy family feeds with optimized performance for sub-200ms responses.
"""

from typing import Dict, List, Optional, Any, Set
from fastapi import WebSocket, WebSocketDisconnect
import asyncio
import json
import logging
from datetime import datetime
from enum import Enum

logger = logging.getLogger(__name__)


class MessageType(str, Enum):
    """WebSocket message types for Instagram-like feed"""
    # Real-time activity updates
    REACTION_ADDED = "reaction_added"
    REACTION_REMOVED = "reaction_removed"
    COMMENT_ADDED = "comment_added"
    POST_CREATED = "post_created"
    
    # Family engagement
    FAMILY_MEMBER_ONLINE = "family_member_online"
    FAMILY_MEMBER_OFFLINE = "family_member_offline"
    MILESTONE_CELEBRATION = "milestone_celebration"
    
    # Feed updates
    FEED_UPDATE = "feed_update"
    TRENDING_UPDATE = "trending_update"
    
    # System messages
    CONNECTION_ESTABLISHED = "connection_established"
    HEARTBEAT = "heartbeat"
    ERROR = "error"


class ConnectionInfo:
    """Information about an active WebSocket connection"""
    
    def __init__(self, websocket: WebSocket, user_id: str, user_data: Dict[str, Any]):
        self.websocket = websocket
        self.user_id = user_id
        self.user_data = user_data
        self.connected_at = datetime.utcnow()
        self.last_heartbeat = datetime.utcnow()
        self.subscribed_rooms: Set[str] = set()
        self.active = True
        
    @property
    def display_name(self) -> str:
        """Get user display name for broadcasts"""
        from .auth import get_user_display_name
        return get_user_display_name(self.user_data)
    
    @property
    def connection_duration(self) -> float:
        """Get connection duration in seconds"""
        return (datetime.utcnow() - self.connected_at).total_seconds()


class WebSocketManager:
    """
    WebSocket connection manager optimized for Instagram-like feed performance.
    
    Features:
    - Connection pooling by pregnancy/family rooms
    - Message broadcasting with < 100ms latency
    - Automatic heartbeat and connection management
    - Family presence tracking
    """
    
    def __init__(self):
        # Active connections: user_id -> ConnectionInfo
        self.active_connections: Dict[str, ConnectionInfo] = {}
        
        # Room subscriptions: room_id -> set of user_ids
        self.room_subscriptions: Dict[str, Set[str]] = {}
        
        # Performance tracking
        self.message_stats = {
            "total_sent": 0,
            "total_failed": 0,
            "avg_latency_ms": 0.0
        }
        
        # Background tasks
        self._heartbeat_task: Optional[asyncio.Task] = None
        self._cleanup_task: Optional[asyncio.Task] = None
    
    async def connect(self, websocket: WebSocket, user_id: str, user_data: Dict[str, Any]) -> bool:
        """
        Establish WebSocket connection with authentication and room setup.
        """
        try:
            await websocket.accept()
            
            # Store connection info
            connection_info = ConnectionInfo(websocket, user_id, user_data)
            self.active_connections[user_id] = connection_info
            
            # Start background tasks if this is the first connection
            if len(self.active_connections) == 1:
                await self._start_background_tasks()
            
            # Send connection established message
            await self.send_to_user(user_id, {
                "type": MessageType.CONNECTION_ESTABLISHED,
                "user_id": user_id,
                "display_name": connection_info.display_name,
                "server_time": datetime.utcnow().isoformat(),
                "features": {
                    "optimistic_reactions": True,
                    "real_time_comments": True,
                    "family_presence": True,
                    "milestone_celebrations": True
                }
            })
            
            logger.info(f"WebSocket connection established for user {user_id} ({connection_info.display_name})")
            return True
            
        except Exception as e:
            logger.error(f"Failed to establish WebSocket connection for user {user_id}: {e}")
            return False
    
    async def disconnect(self, user_id: str) -> None:
        """Clean disconnect for a user"""
        if user_id in self.active_connections:
            connection_info = self.active_connections[user_id]
            
            # Notify subscribed rooms about user going offline
            for room_id in connection_info.subscribed_rooms:
                await self.broadcast_to_room(room_id, {
                    "type": MessageType.FAMILY_MEMBER_OFFLINE,
                    "user_id": user_id,
                    "display_name": connection_info.display_name,
                    "connection_duration": connection_info.connection_duration
                }, exclude_user=user_id)
                
                # Remove from room subscriptions
                if room_id in self.room_subscriptions:
                    self.room_subscriptions[room_id].discard(user_id)
                    
                    # Clean up empty rooms
                    if not self.room_subscriptions[room_id]:
                        del self.room_subscriptions[room_id]
            
            # Close WebSocket connection
            try:
                await connection_info.websocket.close()
            except:
                pass  # Connection might already be closed
            
            del self.active_connections[user_id]
            logger.info(f"WebSocket disconnected for user {user_id} ({connection_info.display_name})")
            
            # Stop background tasks if no connections remain
            if not self.active_connections:
                await self._stop_background_tasks()
    
    async def subscribe_to_room(self, user_id: str, room_id: str) -> bool:
        """Subscribe user to a pregnancy/family room"""
        if user_id not in self.active_connections:
            return False
        
        connection_info = self.active_connections[user_id]
        
        # Validate room access
        from .auth import validate_room_access
        if not await validate_room_access(user_id, room_id):
            await self.send_to_user(user_id, {
                "type": MessageType.ERROR,
                "error": "unauthorized",
                "message": f"Access denied to room {room_id}"
            })
            return False
        
        # Add to room subscriptions
        if room_id not in self.room_subscriptions:
            self.room_subscriptions[room_id] = set()
        
        self.room_subscriptions[room_id].add(user_id)
        connection_info.subscribed_rooms.add(room_id)
        
        # Notify room about new family member online
        await self.broadcast_to_room(room_id, {
            "type": MessageType.FAMILY_MEMBER_ONLINE,
            "user_id": user_id,
            "display_name": connection_info.display_name,
            "joined_room": room_id
        }, exclude_user=user_id)
        
        logger.debug(f"User {user_id} subscribed to room {room_id}")
        return True
    
    async def send_to_user(self, user_id: str, message: Dict[str, Any]) -> bool:
        """Send message to specific user with performance tracking"""
        if user_id not in self.active_connections:
            return False
        
        connection_info = self.active_connections[user_id]
        start_time = datetime.utcnow()
        
        try:
            message_json = json.dumps({
                **message,
                "timestamp": datetime.utcnow().isoformat(),
                "server_id": "feed-ws-1"  # For load balancing identification
            })
            
            await connection_info.websocket.send_text(message_json)
            
            # Track performance
            latency_ms = (datetime.utcnow() - start_time).total_seconds() * 1000
            self.message_stats["total_sent"] += 1
            self.message_stats["avg_latency_ms"] = (
                (self.message_stats["avg_latency_ms"] * (self.message_stats["total_sent"] - 1) + latency_ms) /
                self.message_stats["total_sent"]
            )
            
            return True
            
        except WebSocketDisconnect:
            # Handle graceful disconnection
            await self.disconnect(user_id)
            return False
        except Exception as e:
            logger.error(f"Failed to send message to user {user_id}: {e}")
            self.message_stats["total_failed"] += 1
            
            # Mark connection as inactive but don't disconnect immediately
            connection_info.active = False
            return False
    
    async def broadcast_to_room(self, room_id: str, message: Dict[str, Any], exclude_user: Optional[str] = None) -> int:
        """
        Broadcast message to all users in a room with optimized performance.
        Returns number of successful sends.
        """
        if room_id not in self.room_subscriptions:
            return 0
        
        users_in_room = self.room_subscriptions[room_id].copy()
        if exclude_user:
            users_in_room.discard(exclude_user)
        
        if not users_in_room:
            return 0
        
        # Parallel sending for best performance
        send_tasks = []
        for user_id in users_in_room:
            task = asyncio.create_task(self.send_to_user(user_id, message))
            send_tasks.append(task)
        
        # Wait for all sends to complete
        results = await asyncio.gather(*send_tasks, return_exceptions=True)
        successful_sends = sum(1 for result in results if result is True)
        
        logger.debug(f"Broadcast to room {room_id}: {successful_sends}/{len(users_in_room)} successful")
        return successful_sends
    
    async def handle_feed_activity(self, activity_data: Dict[str, Any]) -> None:
        """
        Handle real-time feed activity broadcasting.
        Optimized for Instagram-like immediate updates.
        """
        activity_type = activity_data.get("activity_type")
        pregnancy_id = activity_data.get("pregnancy_id")
        
        if not pregnancy_id:
            return
        
        # Determine target room
        room_id = f"pregnancy-{pregnancy_id}"
        
        # Build broadcast message based on activity type
        if activity_type == "reaction":
            message = {
                "type": MessageType.REACTION_ADDED,
                "post_id": activity_data.get("target_id"),
                "user": {
                    "id": activity_data.get("user_id"),
                    "name": activity_data.get("user_name", "Someone")
                },
                "reaction": {
                    "type": activity_data.get("activity_data", {}).get("reaction_type", "love"),
                    "intensity": activity_data.get("activity_data", {}).get("intensity", 1)
                },
                "updated_counts": activity_data.get("updated_counts", {}),
                "family_warmth_delta": activity_data.get("family_warmth_delta", 0.0)
            }
        
        elif activity_type == "comment":
            message = {
                "type": MessageType.COMMENT_ADDED,
                "post_id": activity_data.get("target_id"),
                "comment": {
                    "id": activity_data.get("comment_id"),
                    "content": activity_data.get("activity_data", {}).get("comment_text", ""),
                    "author": {
                        "id": activity_data.get("user_id"),
                        "name": activity_data.get("user_name", "Someone")
                    }
                }
            }
        
        elif activity_type == "post_create":
            message = {
                "type": MessageType.POST_CREATED,
                "post": {
                    "id": activity_data.get("target_id"),
                    "type": activity_data.get("activity_data", {}).get("post_type", "update"),
                    "author": {
                        "id": activity_data.get("user_id"),
                        "name": activity_data.get("user_name", "Someone")
                    }
                }
            }
        
        else:
            # Generic feed update
            message = {
                "type": MessageType.FEED_UPDATE,
                "activity": activity_data
            }
        
        # Broadcast to family room
        await self.broadcast_to_room(room_id, message)
    
    async def _start_background_tasks(self) -> None:
        """Start background maintenance tasks"""
        self._heartbeat_task = asyncio.create_task(self._heartbeat_loop())
        self._cleanup_task = asyncio.create_task(self._cleanup_loop())
        logger.info("WebSocket background tasks started")
    
    async def _stop_background_tasks(self) -> None:
        """Stop background maintenance tasks"""
        if self._heartbeat_task:
            self._heartbeat_task.cancel()
            self._heartbeat_task = None
        
        if self._cleanup_task:
            self._cleanup_task.cancel()
            self._cleanup_task = None
        
        logger.info("WebSocket background tasks stopped")
    
    async def _heartbeat_loop(self) -> None:
        """Send periodic heartbeat messages to maintain connections"""
        while True:
            try:
                await asyncio.sleep(30)  # Heartbeat every 30 seconds
                
                current_time = datetime.utcnow()
                heartbeat_message = {
                    "type": MessageType.HEARTBEAT,
                    "server_time": current_time.isoformat(),
                    "active_connections": len(self.active_connections)
                }
                
                # Send heartbeat to all active connections
                for user_id in list(self.active_connections.keys()):
                    await self.send_to_user(user_id, heartbeat_message)
                
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Error in heartbeat loop: {e}")
    
    async def _cleanup_loop(self) -> None:
        """Clean up stale connections and rooms"""
        while True:
            try:
                await asyncio.sleep(300)  # Cleanup every 5 minutes
                
                current_time = datetime.utcnow()
                stale_users = []
                
                # Find stale connections (no heartbeat for > 2 minutes)
                for user_id, connection_info in self.active_connections.items():
                    if (current_time - connection_info.last_heartbeat).total_seconds() > 120:
                        stale_users.append(user_id)
                
                # Disconnect stale connections
                for user_id in stale_users:
                    logger.warning(f"Disconnecting stale WebSocket connection for user {user_id}")
                    await self.disconnect(user_id)
                
                # Clean up empty rooms
                empty_rooms = [room_id for room_id, users in self.room_subscriptions.items() if not users]
                for room_id in empty_rooms:
                    del self.room_subscriptions[room_id]
                
                if stale_users or empty_rooms:
                    logger.info(f"Cleanup completed: {len(stale_users)} stale connections, {len(empty_rooms)} empty rooms")
                
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Error in cleanup loop: {e}")
    
    def get_stats(self) -> Dict[str, Any]:
        """Get WebSocket manager statistics"""
        return {
            "active_connections": len(self.active_connections),
            "active_rooms": len(self.room_subscriptions),
            "total_subscriptions": sum(len(users) for users in self.room_subscriptions.values()),
            "message_stats": self.message_stats.copy(),
            "uptime_seconds": getattr(self, '_start_time', datetime.utcnow()).timestamp()
        }


# Global WebSocket manager instance
websocket_manager = WebSocketManager()