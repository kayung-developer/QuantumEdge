"""
AuraQuant - Collaboration and Social Trading Service
"""
import asyncio
from uuid import UUID
from typing import List, Dict
from fastapi import WebSocket, WebSocketDisconnect
from sqlalchemy.ext.asyncio import AsyncSession

from app.crud.collaboration import crud_trade_room, crud_chat_message  # Assumes these are created
from app.models.user import User

from app.services.order_orchestrator import orchestrator_service


class TradeRoomManager:
    """Manages active WebSocket connections for all trade rooms."""

    def __init__(self):
        self.active_connections: Dict[UUID, List[WebSocket]] = {}

    async def connect(self, room_id: UUID, websocket: WebSocket):
        await websocket.accept()
        if room_id not in self.active_connections:
            self.active_connections[room_id] = []
        self.active_connections[room_id].append(websocket)

    def disconnect(self, room_id: UUID, websocket: WebSocket):
        if room_id in self.active_connections:
            self.active_connections[room_id].remove(websocket)

    async def broadcast_to_room(self, room_id: UUID, message: dict):
        """Sends a JSON message to all clients in a specific room."""
        if room_id in self.active_connections:
            websockets = self.active_connections[room_id]
            for connection in websockets:
                await connection.send_json(message)


room_manager = TradeRoomManager()


class CollaborationService:
    """Handles business logic for trade rooms and copy trading."""

    async def handle_chat_session(self, room_id: UUID, user: User, websocket: WebSocket):
        """Manages a single user's WebSocket session in a room."""
        await room_manager.connect(room_id, websocket)
        try:
            # Announce user has joined
            await room_manager.broadcast_to_room(room_id, {
                "type": "user_join", "user_name": user.full_name or user.email
            })

            while True:
                data = await websocket.receive_json()
                message_content = data['message']

                # Persist the message to the database
                async with AsyncSessionLocal() as db:
                    await crud_chat_message.create_with_sender(
                        db, room_id=room_id, sender_id=user.id, content=message_content
                    )

                # Broadcast the new message to everyone in the room
                await room_manager.broadcast_to_room(room_id, {
                    "type": "new_message",
                    "sender_name": user.full_name or user.email,
                    "content": message_content,
                    "timestamp": datetime.utcnow().isoformat()
                })
        except WebSocketDisconnect:
            # Announce user has left
            await room_manager.broadcast_to_room(room_id, {
                "type": "user_leave", "user_name": user.full_name or user.email
            })
        finally:
            room_manager.disconnect(room_id, websocket)

    async def initiate_copy_trade(self, db: AsyncSession, *, follower: User, leader: User, trade: "OrchestratedOrder"):
        """
        This is the core copy trading logic. It's triggered when a 'leader'
        has a trade successfully executed.
        """
        subscriptions = await crud_copy_trade.get_followers_of_leader(db, leader_id=leader.id)

        for sub in subscriptions:
            if sub.follower_id == follower.id and sub.is_active:
                logger.info(f"Initiating copy trade for follower {sub.follower_id} from leader {leader.id}")

                # --- APPLY FOLLOWER'S RISK RULES ---
                copy_quantity = trade.quantity_requested * sub.trade_size_multiplier
                notional_value = copy_quantity * (trade.average_fill_price or trade.price)

                if notional_value > sub.max_trade_size_usd:
                    logger.warning(f"Copy trade for {sub.follower_id} skipped: Exceeds max trade size.")
                    continue

                # --- Create a new orchestrated order for the follower ---
                copy_order = OrderCreate(
                    exchange=trade.exchange,
                    symbol=trade.symbol,
                    order_type=trade.order_type,
                    side=trade.side,
                    quantity=copy_quantity,
                    price=trade.price,
                    # Paper trade flag can be a user setting
                    is_paper_trade=True
                )

                # The order goes through the follower's own risk engine and orchestrator
                await orchestrator_service.create_order(db, user=sub.follower, order_in=copy_order)

                # TODO: Send a notification to the follower


collaboration_service = CollaborationService()