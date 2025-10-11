"""
AuraQuant - API Endpoints for Collaboration and Social Trading
"""
from uuid import UUID
from fastapi import APIRouter, Depends, WebSocket, HTTPException

from app.api import deps
from app.models.user import User
from app.services.collaboration_service import collaboration_service

router = APIRouter()


# --- Standard REST Endpoints for Room Management ---
@router.post("/rooms", status_code=201)
async def create_trade_room():
    # ... Logic for creating a new room, adding owner as member
    pass


@router.get("/rooms")
async def list_public_trade_rooms():
    # ... Logic for listing all public rooms
    pass


# --- Real-Time WebSocket Endpoint ---
@router.websocket("/rooms/{room_id}/ws")
async def trade_room_websocket(
        websocket: WebSocket,
        room_id: UUID,
        current_user: User = Depends(deps.get_current_user_from_ws_query)
):
    """
    Handles the real-time WebSocket connection for a specific trade room.
    """
    # First, verify the user has permission to join this room
    # (check if they are a member in the DB)
    is_member = await crud_trade_room.is_user_member(db, room_id=room_id, user_id=current_user.id)
    if not is_member:
        await websocket.close(code=403)
        return

    await collaboration_service.handle_chat_session(
        room_id=room_id, user=current_user, websocket=websocket
    )