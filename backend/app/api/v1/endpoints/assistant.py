"""
AuraQuant - API Endpoint for the AI Research Assistant
"""
from fastapi import APIRouter, WebSocket, WebSocketDisconnect, Depends

from app.api import deps
from app.models.user import User
from app.services.assistant_service import assistant_service

router = APIRouter()


@router.websocket("/ws")
async def assistant_websocket(
        websocket: WebSocket,
        current_user: User = Depends(deps.get_current_user_from_ws_query)  # New dependency needed
):
    """
    Handles a WebSocket connection for the AI Assistant, streaming responses back.
    """
    await websocket.accept()
    try:
        while True:
            # Receive the user's query from the frontend
            query = await websocket.receive_text()

            # --- This is a simplified stream for the final answer ---
            # A more advanced version would stream the agent's "thoughts" and tool outputs.
            response = await assistant_service.get_response(query, current_user.id)
            await websocket.send_text(response)

    except WebSocketDisconnect:
        print(f"User {current_user.id} disconnected from the assistant.")
    except Exception as e:
        await websocket.send_text(f"An error occurred: {e}")