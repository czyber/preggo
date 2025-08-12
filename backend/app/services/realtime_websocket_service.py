"""
Real-time WebSocket Service for reactions and comments.

This service provides:
- Real-time reaction updates with family warmth changes
- Real-time comment additions and threading
- Typing indicators for comments
- Family activity notifications
- Connection management with pregnancy-based rooms
"""

from typing import Dict, Set, Optional, Any, List
from fastapi import WebSocket, WebSocketDisconnect
from datetime import datetime, timedelta
import json
import asyncio
import logging
from dataclasses import dataclass, asdict
from enum import Enum
import uuid

logger = logging.getLogger(__name__)


class MessageType(str, Enum):
    """WebSocket message types"""
    # Reactions
    REACTION_ADDED = "reaction_added"
    REACTION_REMOVED = "reaction_removed"
    REACTION_UPDATED = "reaction_updated"
    
    # Comments
    COMMENT_ADDED = "comment_added"
    COMMENT_UPDATED = "comment_updated"
    COMMENT_DELETED = "comment_deleted"
    
    # Typing indicators
    TYPING_STARTED = "typing_started"
    TYPING_STOPPED = "typing_stopped"
    
    # Family warmth
    WARMTH_UPDATED = "warmth_updated"
    
    # Connection management
    CONNECTION_ACK = "connection_ack"
    HEARTBEAT = "heartbeat"
    ERROR = "error"
    
    # Family activity
    FAMILY_ACTIVITY = "family_activity"
    MILESTONE_CELEBRATION = "milestone_celebration"


@dataclass
class WebSocketMessage:
    """Structured WebSocket message"""
    type: MessageType
    data: Dict[str, Any]
    timestamp: str = None
    message_id: str = None
    target_users: Optional[List[str]] = None
    
    def __post_init__(self):
        if not self.timestamp:
            self.timestamp = datetime.utcnow().isoformat()
        if not self.message_id:
            self.message_id = str(uuid.uuid4())


@dataclass
class ConnectionInfo:
    """Information about a WebSocket connection"""
    websocket: WebSocket
    user_id: str
    pregnancy_id: str
    connected_at: datetime
    last_heartbeat: datetime
    subscriptions: Set[str]  # What they're subscribed to (posts, comments, etc.)
    
    def is_alive(self, timeout_seconds: int = 120) -> bool:
        """Check if connection is still alive based on last heartbeat."""
        return (datetime.utcnow() - self.last_heartbeat).total_seconds() < timeout_seconds


class RealtimeWebSocketService:
    """Service for managing real-time WebSocket connections and messaging."""
    
    def __init__(self):
        # Connections grouped by pregnancy_id
        self.pregnancy_connections: Dict[str, Dict[str, ConnectionInfo]] = {}
        
        # User to pregnancy mapping for quick lookup
        self.user_pregnancies: Dict[str, Set[str]] = {}
        
        # Message queue for handling bursts
        self.message_queue: Optional[asyncio.Queue] = None
        
        # Background task references
        self._background_tasks: List[asyncio.Task] = []
        
        # Initialization flag
        self._initialized = False
    
    def _ensure_initialized(self):
        """Ensure service is initialized with event loop."""
        if not self._initialized:
            try:
                loop = asyncio.get_running_loop()
                self.message_queue = asyncio.Queue()
                
                # Start background tasks
                self._background_tasks.append(
                    loop.create_task(self._process_message_queue())
                )
                self._background_tasks.append(
                    loop.create_task(self._cleanup_stale_connections())
                )
                
                self._initialized = True
            except RuntimeError:
                # No event loop running, will initialize later
                pass
    
    async def connect_user(
        self,
        websocket: WebSocket,
        user_id: str,
        pregnancy_id: str,
        subscriptions: Optional[Set[str]] = None
    ) -> bool:
        """Connect a user to real-time updates for a pregnancy."""
        try:
            # Ensure service is initialized
            self._ensure_initialized()
            await websocket.accept()
            
            # Create connection info
            connection = ConnectionInfo(
                websocket=websocket,
                user_id=user_id,
                pregnancy_id=pregnancy_id,
                connected_at=datetime.utcnow(),
                last_heartbeat=datetime.utcnow(),
                subscriptions=subscriptions or {"reactions", "comments", "typing", "warmth"}
            )
            
            # Store connection
            if pregnancy_id not in self.pregnancy_connections:
                self.pregnancy_connections[pregnancy_id] = {}
            
            connection_key = f"{user_id}_{uuid.uuid4().hex[:8]}"  # Allow multiple connections per user
            self.pregnancy_connections[pregnancy_id][connection_key] = connection
            
            # Update user pregnancy mapping
            if user_id not in self.user_pregnancies:
                self.user_pregnancies[user_id] = set()
            self.user_pregnancies[user_id].add(pregnancy_id)
            
            # Send connection acknowledgment
            ack_message = WebSocketMessage(
                type=MessageType.CONNECTION_ACK,
                data={
                    "user_id": user_id,
                    "pregnancy_id": pregnancy_id,
                    "connection_id": connection_key,
                    "subscriptions": list(connection.subscriptions),
                    "server_time": datetime.utcnow().isoformat()
                }
            )
            
            await self._send_to_connection(connection, ack_message)
            
            logger.info(f"User {user_id} connected to pregnancy {pregnancy_id} with subscriptions: {connection.subscriptions}")
            
            # Start heartbeat for this connection
            asyncio.create_task(self._handle_connection_heartbeat(connection_key, pregnancy_id))
            
            return True
            
        except Exception as e:
            logger.error(f"Error connecting user {user_id} to pregnancy {pregnancy_id}: {e}")
            return False
    
    async def disconnect_user(self, user_id: str, pregnancy_id: str, connection_id: Optional[str] = None):
        """Disconnect a user from real-time updates."""
        try:
            if pregnancy_id not in self.pregnancy_connections:
                return
            
            connections_to_remove = []
            
            if connection_id:
                # Disconnect specific connection
                if connection_id in self.pregnancy_connections[pregnancy_id]:
                    connections_to_remove.append(connection_id)
            else:
                # Disconnect all connections for this user/pregnancy combo
                for conn_id, conn_info in self.pregnancy_connections[pregnancy_id].items():
                    if conn_info.user_id == user_id:
                        connections_to_remove.append(conn_id)
            
            # Remove connections
            for conn_id in connections_to_remove:
                connection = self.pregnancy_connections[pregnancy_id].pop(conn_id, None)
                if connection:
                    try:
                        await connection.websocket.close()
                    except Exception:
                        pass  # Connection may already be closed
            
            # Clean up empty pregnancy groups
            if not self.pregnancy_connections[pregnancy_id]:
                del self.pregnancy_connections[pregnancy_id]
            
            # Update user pregnancy mapping
            if user_id in self.user_pregnancies:
                remaining_connections = any(
                    conn_info.user_id == user_id 
                    for pregnancy_conns in self.pregnancy_connections.values()
                    for conn_info in pregnancy_conns.values()
                )
                
                if not remaining_connections:
                    self.user_pregnancies[user_id].discard(pregnancy_id)
                    if not self.user_pregnancies[user_id]:
                        del self.user_pregnancies[user_id]
            
            logger.info(f"User {user_id} disconnected from pregnancy {pregnancy_id}")
            
        except Exception as e:
            logger.error(f"Error disconnecting user {user_id}: {e}")
    
    async def broadcast_reaction_update(
        self,
        pregnancy_id: str,
        reaction_data: Dict[str, Any],
        exclude_user: Optional[str] = None
    ):
        """Broadcast reaction update to all connected users."""
        message = WebSocketMessage(
            type=MessageType.REACTION_ADDED if reaction_data.get("action") == "add" else MessageType.REACTION_UPDATED,
            data=reaction_data
        )
        
        await self._broadcast_to_pregnancy(pregnancy_id, message, exclude_user, subscription="reactions")
    
    async def broadcast_comment_update(
        self,
        pregnancy_id: str,
        comment_data: Dict[str, Any],
        exclude_user: Optional[str] = None
    ):
        """Broadcast comment update to all connected users."""
        message = WebSocketMessage(
            type=MessageType.COMMENT_ADDED if comment_data.get("action") == "add" else MessageType.COMMENT_UPDATED,
            data=comment_data
        )
        
        await self._broadcast_to_pregnancy(pregnancy_id, message, exclude_user, subscription="comments")
    
    async def broadcast_typing_indicator(
        self,
        pregnancy_id: str,
        user_id: str,
        post_id: Optional[str] = None,
        comment_id: Optional[str] = None,
        is_typing: bool = True,
        user_name: Optional[str] = None
    ):
        """Broadcast typing indicator to all connected users."""
        message_type = MessageType.TYPING_STARTED if is_typing else MessageType.TYPING_STOPPED
        
        message = WebSocketMessage(
            type=message_type,
            data={
                "user_id": user_id,
                "user_name": user_name,
                "post_id": post_id,
                "comment_id": comment_id,
                "is_typing": is_typing
            }
        )
        
        await self._broadcast_to_pregnancy(pregnancy_id, message, exclude_user=user_id, subscription="typing")
    
    async def broadcast_family_warmth_update(
        self,
        pregnancy_id: str,
        warmth_data: Dict[str, Any]
    ):
        """Broadcast family warmth score update."""
        message = WebSocketMessage(
            type=MessageType.WARMTH_UPDATED,
            data=warmth_data
        )
        
        await self._broadcast_to_pregnancy(pregnancy_id, message, subscription="warmth")
    
    async def broadcast_family_activity(
        self,
        pregnancy_id: str,
        activity_data: Dict[str, Any],
        priority: int = 1
    ):
        """Broadcast general family activity (likes, comments, etc.)."""
        message = WebSocketMessage(
            type=MessageType.FAMILY_ACTIVITY,
            data={
                **activity_data,
                "priority": priority
            }
        )
        
        await self._broadcast_to_pregnancy(pregnancy_id, message, subscription="activity")
    
    async def broadcast_milestone_celebration(
        self,
        pregnancy_id: str,
        celebration_data: Dict[str, Any],
        target_users: Optional[List[str]] = None
    ):
        """Broadcast milestone celebration with high priority."""
        message = WebSocketMessage(
            type=MessageType.MILESTONE_CELEBRATION,
            data=celebration_data,
            target_users=target_users
        )
        
        await self._broadcast_to_pregnancy(pregnancy_id, message, subscription="celebrations")
    
    async def send_direct_message(
        self,
        user_id: str,
        message: WebSocketMessage
    ):
        """Send a direct message to a specific user across all their connections."""
        user_pregnancies = self.user_pregnancies.get(user_id, set())
        
        for pregnancy_id in user_pregnancies:
            if pregnancy_id in self.pregnancy_connections:
                for connection_info in self.pregnancy_connections[pregnancy_id].values():
                    if connection_info.user_id == user_id:
                        await self._send_to_connection(connection_info, message)
    
    async def get_connection_stats(self) -> Dict[str, Any]:
        """Get real-time connection statistics."""
        total_connections = sum(
            len(connections) for connections in self.pregnancy_connections.values()
        )
        
        pregnancy_stats = {}
        for pregnancy_id, connections in self.pregnancy_connections.items():
            unique_users = len(set(conn.user_id for conn in connections.values()))
            pregnancy_stats[pregnancy_id] = {
                "total_connections": len(connections),
                "unique_users": unique_users,
                "connections_per_user": round(len(connections) / max(unique_users, 1), 2)
            }
        
        return {
            "total_connections": total_connections,
            "total_pregnancies": len(self.pregnancy_connections),
            "total_users": len(self.user_pregnancies),
            "pregnancy_breakdown": pregnancy_stats,
            "message_queue_size": self.message_queue.qsize() if self.message_queue else 0,
            "generated_at": datetime.utcnow().isoformat()
        }
    
    # Private helper methods
    
    async def _broadcast_to_pregnancy(
        self,
        pregnancy_id: str,
        message: WebSocketMessage,
        exclude_user: Optional[str] = None,
        subscription: Optional[str] = None
    ):
        """Broadcast message to all connections for a pregnancy."""
        if pregnancy_id not in self.pregnancy_connections:
            return
        
        connections = self.pregnancy_connections[pregnancy_id].values()
        
        # Filter connections based on criteria
        target_connections = []
        for connection in connections:
            # Skip if excluding this user
            if exclude_user and connection.user_id == exclude_user:
                continue
            
            # Skip if user doesn't subscribe to this type
            if subscription and subscription not in connection.subscriptions:
                continue
            
            # Skip if message has specific target users
            if message.target_users and connection.user_id not in message.target_users:
                continue
            
            # Skip if connection is stale
            if not connection.is_alive():
                continue
            
            target_connections.append(connection)
        
        # Queue the broadcast
        if self.message_queue:
            await self.message_queue.put((target_connections, message))
    
    async def _send_to_connection(self, connection: ConnectionInfo, message: WebSocketMessage):
        """Send message to a specific connection."""
        try:
            message_json = json.dumps(asdict(message), default=str)
            await connection.websocket.send_text(message_json)
            
        except WebSocketDisconnect:
            logger.info(f"Connection for user {connection.user_id} disconnected")
            await self.disconnect_user(connection.user_id, connection.pregnancy_id)
            
        except Exception as e:
            logger.error(f"Error sending message to user {connection.user_id}: {e}")
            await self.disconnect_user(connection.user_id, connection.pregnancy_id)
    
    async def _process_message_queue(self):
        """Process queued messages for efficient broadcasting."""
        while True:
            try:
                target_connections, message = await self.message_queue.get()
                
                # Send to all target connections
                send_tasks = [
                    self._send_to_connection(connection, message)
                    for connection in target_connections
                ]
                
                if send_tasks:
                    await asyncio.gather(*send_tasks, return_exceptions=True)
                
                self.message_queue.task_done()
                
            except Exception as e:
                logger.error(f"Error processing message queue: {e}")
                await asyncio.sleep(0.1)
    
    async def _handle_connection_heartbeat(self, connection_id: str, pregnancy_id: str):
        """Handle heartbeat for a specific connection."""
        while True:
            try:
                await asyncio.sleep(30)  # Heartbeat every 30 seconds
                
                if (pregnancy_id not in self.pregnancy_connections or 
                    connection_id not in self.pregnancy_connections[pregnancy_id]):
                    break  # Connection was removed
                
                connection = self.pregnancy_connections[pregnancy_id][connection_id]
                
                # Send heartbeat
                heartbeat_message = WebSocketMessage(
                    type=MessageType.HEARTBEAT,
                    data={"server_time": datetime.utcnow().isoformat()}
                )
                
                await self._send_to_connection(connection, heartbeat_message)
                connection.last_heartbeat = datetime.utcnow()
                
            except Exception as e:
                logger.error(f"Error in connection heartbeat: {e}")
                break
    
    async def _cleanup_stale_connections(self):
        """Periodically clean up stale connections."""
        while True:
            try:
                await asyncio.sleep(60)  # Cleanup every minute
                
                stale_connections = []
                
                for pregnancy_id, connections in self.pregnancy_connections.items():
                    for connection_id, connection_info in connections.items():
                        if not connection_info.is_alive():
                            stale_connections.append((pregnancy_id, connection_id, connection_info.user_id))
                
                # Remove stale connections
                for pregnancy_id, connection_id, user_id in stale_connections:
                    await self.disconnect_user(user_id, pregnancy_id, connection_id)
                    logger.info(f"Cleaned up stale connection: {connection_id}")
                
                if stale_connections:
                    logger.info(f"Cleaned up {len(stale_connections)} stale connections")
                
            except Exception as e:
                logger.error(f"Error cleaning up stale connections: {e}")


# Global service instance
realtime_websocket_service = RealtimeWebSocketService()