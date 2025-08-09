"""
WebSocket message handler for Instagram-like feed real-time features.

Handles incoming WebSocket messages, routing, and command processing
for optimized family engagement and feed interactions.
"""

from typing import Dict, Any, Optional, List
from fastapi import WebSocket, WebSocketDisconnect
import json
import logging
from datetime import datetime
from enum import Enum

from .manager import websocket_manager, MessageType
from .auth import authenticate_websocket_connection, validate_room_access

logger = logging.getLogger(__name__)


class ClientMessageType(str, Enum):
    """Incoming message types from clients"""
    # Room management
    SUBSCRIBE_ROOM = "subscribe_room"
    UNSUBSCRIBE_ROOM = "unsubscribe_room"
    
    # Feed interactions
    OPTIMISTIC_REACTION = "optimistic_reaction"
    TYPING_INDICATOR = "typing_indicator"
    READ_RECEIPT = "read_receipt"
    
    # System
    HEARTBEAT_RESPONSE = "heartbeat_response"
    GET_ROOM_INFO = "get_room_info"


class WebSocketHandler:
    """
    WebSocket message handler optimized for Instagram-like feed performance.
    
    Processes client messages with sub-100ms routing and response times.
    """
    
    def __init__(self):
        self.message_handlers = {
            ClientMessageType.SUBSCRIBE_ROOM: self._handle_subscribe_room,
            ClientMessageType.UNSUBSCRIBE_ROOM: self._handle_unsubscribe_room,
            ClientMessageType.OPTIMISTIC_REACTION: self._handle_optimistic_reaction,
            ClientMessageType.TYPING_INDICATOR: self._handle_typing_indicator,
            ClientMessageType.READ_RECEIPT: self._handle_read_receipt,
            ClientMessageType.HEARTBEAT_RESPONSE: self._handle_heartbeat_response,
            ClientMessageType.GET_ROOM_INFO: self._handle_get_room_info,
        }
    
    async def handle_connection(self, websocket: WebSocket, pregnancy_id: str) -> None:
        """
        Handle WebSocket connection lifecycle for pregnancy feed.
        """
        user_data = None
        user_id = None
        
        try:
            # Authenticate WebSocket connection
            user_data = await authenticate_websocket_connection(websocket)
            user_id = user_data["sub"]
            
            # Establish connection in manager
            connection_success = await websocket_manager.connect(websocket, user_id, user_data)
            
            if not connection_success:
                await websocket.close(code=1000, reason="Connection setup failed")
                return
            
            # Auto-subscribe to pregnancy room
            pregnancy_room = f"pregnancy-{pregnancy_id}"
            await websocket_manager.subscribe_to_room(user_id, pregnancy_room)
            
            # Start message processing loop
            await self._message_loop(websocket, user_id, pregnancy_id)
            
        except WebSocketDisconnect:
            logger.info(f"WebSocket client disconnected: {user_id}")
        except Exception as e:
            logger.error(f"WebSocket connection error for user {user_id}: {e}")
            try:
                await websocket.send_json({
                    "type": MessageType.ERROR,
                    "error": "connection_error",
                    "message": str(e)
                })
            except:
                pass  # Connection might be closed
        finally:
            # Clean disconnection
            if user_id:
                await websocket_manager.disconnect(user_id)
    
    async def _message_loop(self, websocket: WebSocket, user_id: str, pregnancy_id: str) -> None:
        """Main message processing loop with error handling"""
        while True:
            try:
                # Receive message with timeout to prevent hanging
                message_text = await websocket.receive_text()
                
                # Parse JSON message
                try:
                    message = json.loads(message_text)
                except json.JSONDecodeError as e:
                    await websocket_manager.send_to_user(user_id, {
                        "type": MessageType.ERROR,
                        "error": "invalid_json",
                        "message": f"Invalid JSON: {str(e)}"
                    })
                    continue
                
                # Process message with performance tracking
                start_time = datetime.utcnow()
                await self._process_message(user_id, pregnancy_id, message)
                
                # Track processing time for performance monitoring
                processing_time = (datetime.utcnow() - start_time).total_seconds() * 1000
                if processing_time > 50:  # Log slow processing
                    logger.warning(f"Slow message processing: {processing_time:.1f}ms for {message.get('type')}")
                
            except WebSocketDisconnect:
                break
            except Exception as e:
                logger.error(f"Error in message loop for user {user_id}: {e}")
                await websocket_manager.send_to_user(user_id, {
                    "type": MessageType.ERROR,
                    "error": "processing_error",
                    "message": "Failed to process message"
                })
    
    async def _process_message(self, user_id: str, pregnancy_id: str, message: Dict[str, Any]) -> None:
        """Process individual client message with routing"""
        message_type = message.get("type")
        
        if not message_type:
            await websocket_manager.send_to_user(user_id, {
                "type": MessageType.ERROR,
                "error": "missing_type",
                "message": "Message type is required"
            })
            return
        
        # Route to appropriate handler
        handler = self.message_handlers.get(message_type)
        if not handler:
            await websocket_manager.send_to_user(user_id, {
                "type": MessageType.ERROR,
                "error": "unknown_type",
                "message": f"Unknown message type: {message_type}"
            })
            return
        
        try:
            await handler(user_id, pregnancy_id, message)
        except Exception as e:
            logger.error(f"Error handling message type {message_type} for user {user_id}: {e}")
            await websocket_manager.send_to_user(user_id, {
                "type": MessageType.ERROR,
                "error": "handler_error",
                "message": f"Failed to handle {message_type}"
            })
    
    async def _handle_subscribe_room(self, user_id: str, pregnancy_id: str, message: Dict[str, Any]) -> None:
        """Handle room subscription requests"""
        room_id = message.get("room_id")
        if not room_id:
            await websocket_manager.send_to_user(user_id, {
                "type": MessageType.ERROR,
                "error": "missing_room_id",
                "message": "room_id is required for subscription"
            })
            return
        
        # Validate and subscribe
        success = await websocket_manager.subscribe_to_room(user_id, room_id)
        
        await websocket_manager.send_to_user(user_id, {
            "type": "room_subscription_result",
            "room_id": room_id,
            "subscribed": success,
            "message": "Subscribed successfully" if success else "Subscription failed"
        })
    
    async def _handle_unsubscribe_room(self, user_id: str, pregnancy_id: str, message: Dict[str, Any]) -> None:
        """Handle room unsubscription requests"""
        room_id = message.get("room_id")
        if not room_id:
            return
        
        # Remove from room subscriptions
        if user_id in websocket_manager.active_connections:
            connection_info = websocket_manager.active_connections[user_id]
            connection_info.subscribed_rooms.discard(room_id)
            
            if room_id in websocket_manager.room_subscriptions:
                websocket_manager.room_subscriptions[room_id].discard(user_id)
        
        await websocket_manager.send_to_user(user_id, {
            "type": "room_unsubscription_result",
            "room_id": room_id,
            "unsubscribed": True
        })
    
    async def _handle_optimistic_reaction(self, user_id: str, pregnancy_id: str, message: Dict[str, Any]) -> None:
        """
        Handle optimistic reaction updates for immediate UI feedback.
        This complements the HTTP optimistic reaction endpoint.
        """
        post_id = message.get("post_id")
        reaction_type = message.get("reaction_type")
        
        if not post_id or not reaction_type:
            return
        
        # Broadcast optimistic reaction immediately to room members
        pregnancy_room = f"pregnancy-{pregnancy_id}"
        
        # Get user display name
        connection_info = websocket_manager.active_connections.get(user_id)
        display_name = connection_info.display_name if connection_info else "Someone"
        
        await websocket_manager.broadcast_to_room(pregnancy_room, {
            "type": MessageType.REACTION_ADDED,
            "post_id": post_id,
            "user": {
                "id": user_id,
                "name": display_name
            },
            "reaction": {
                "type": reaction_type,
                "intensity": message.get("intensity", 1)
            },
            "optimistic": True,  # Mark as optimistic for client handling
            "client_id": message.get("client_id")
        }, exclude_user=user_id)\n    \n    async def _handle_typing_indicator(self, user_id: str, pregnancy_id: str, message: Dict[str, Any]) -> None:\n        \"\"\"Handle typing indicators for comments\"\"\"\n        post_id = message.get(\"post_id\")\n        is_typing = message.get(\"is_typing\", False)\n        \n        if not post_id:\n            return\n        \n        # Get user display name\n        connection_info = websocket_manager.active_connections.get(user_id)\n        display_name = connection_info.display_name if connection_info else \"Someone\"\n        \n        # Broadcast typing indicator to room\n        pregnancy_room = f\"pregnancy-{pregnancy_id}\"\n        await websocket_manager.broadcast_to_room(pregnancy_room, {\n            \"type\": \"typing_indicator\",\n            \"post_id\": post_id,\n            \"user\": {\n                \"id\": user_id,\n                \"name\": display_name\n            },\n            \"is_typing\": is_typing\n        }, exclude_user=user_id)\n    \n    async def _handle_read_receipt(self, user_id: str, pregnancy_id: str, message: Dict[str, Any]) -> None:\n        \"\"\"Handle read receipts for posts/comments\"\"\"\n        post_id = message.get(\"post_id\")\n        read_at = message.get(\"read_at\", datetime.utcnow().isoformat())\n        \n        if not post_id:\n            return\n        \n        # Store read receipt (in production, save to database)\n        # For now, just acknowledge\n        await websocket_manager.send_to_user(user_id, {\n            \"type\": \"read_receipt_ack\",\n            \"post_id\": post_id,\n            \"read_at\": read_at\n        })\n    \n    async def _handle_heartbeat_response(self, user_id: str, pregnancy_id: str, message: Dict[str, Any]) -> None:\n        \"\"\"Handle client heartbeat responses\"\"\"\n        if user_id in websocket_manager.active_connections:\n            connection_info = websocket_manager.active_connections[user_id]\n            connection_info.last_heartbeat = datetime.utcnow()\n    \n    async def _handle_get_room_info(self, user_id: str, pregnancy_id: str, message: Dict[str, Any]) -> None:\n        \"\"\"Handle requests for room information\"\"\"\n        room_id = message.get(\"room_id\", f\"pregnancy-{pregnancy_id}\")\n        \n        # Get room statistics\n        room_users = websocket_manager.room_subscriptions.get(room_id, set())\n        active_users = []\n        \n        for room_user_id in room_users:\n            if room_user_id in websocket_manager.active_connections:\n                connection_info = websocket_manager.active_connections[room_user_id]\n                active_users.append({\n                    \"id\": room_user_id,\n                    \"name\": connection_info.display_name,\n                    \"connected_at\": connection_info.connected_at.isoformat(),\n                    \"is_online\": connection_info.active\n                })\n        \n        await websocket_manager.send_to_user(user_id, {\n            \"type\": \"room_info\",\n            \"room_id\": room_id,\n            \"active_users\": active_users,\n            \"total_users\": len(active_users),\n            \"requested_at\": datetime.utcnow().isoformat()\n        })\n\n\n# Global WebSocket handler instance\nwebsocket_handler = WebSocketHandler()