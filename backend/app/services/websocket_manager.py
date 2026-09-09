import asyncio
import logging
from typing import Dict, Any, List, Set, Optional, Union
from datetime import datetime, timezone
from fastapi import WebSocket, WebSocketDisconnect

from app.schemas.events import DomainEvent, EventType

logger = logging.getLogger('disasterguard.websocket')

class ConnectionInfo:
    def __init__(self, websocket: WebSocket, client_id: str, role: str = 'OPERATOR', user_id: Optional[int] = None):
        self.websocket = websocket
        self.client_id = client_id
        self.role = role.upper()
        self.user_id = user_id
        self.connected_at = datetime.now(timezone.utc)

class WebSocketManager:
    def __init__(self):
        self.active_connections: Set[WebSocket] = set()
        self.connection_details: Dict[WebSocket, ConnectionInfo] = {}

    async def connect(self, websocket: WebSocket, client_id: str = 'anonymous', role: str = 'OPERATOR', user_id: Optional[int] = None):
        await websocket.accept()
        self.active_connections.add(websocket)
        self.connection_details[websocket] = ConnectionInfo(websocket, client_id, role, user_id)
        logger.info(f'WebSocket client connected: id={client_id}, role={role}, total_active={len(self.active_connections)}')

    def disconnect(self, websocket: WebSocket):
        info = self.connection_details.pop(websocket, None)
        self.active_connections.discard(websocket)
        client_id = info.client_id if info else 'unknown'
        logger.info(f'WebSocket client disconnected: id={client_id}, total_active={len(self.active_connections)}')

    async def broadcast(self, payload: Dict[str, Any], role_filter: Optional[str] = None):
        if not self.active_connections:
            return

        dead_connections: List[WebSocket] = []
        target_role = role_filter.upper() if role_filter else None

        for ws in list(self.active_connections):
            info = self.connection_details.get(ws)
            if target_role and info and info.role != target_role and info.role != 'ADMIN':
                continue

            try:
                await ws.send_json(payload)
            except Exception as e:
                logger.warning(f'Failed to send event to client {getattr(info, "client_id", "unknown")}: {e}')
                dead_connections.append(ws)

        for ws in dead_connections:
            self.disconnect(ws)

    async def send_personal(self, websocket: WebSocket, payload: Dict[str, Any]):
        try:
            await websocket.send_json(payload)
        except Exception as e:
            logger.warning(f'Failed to send personal message: {e}')
            self.disconnect(websocket)

    def broadcast_event(
        self,
        event: Union[DomainEvent, Dict[str, Any]],
        role_filter: Optional[str] = None
    ):
        from fastapi.encoders import jsonable_encoder
        if isinstance(event, DomainEvent):
            payload = jsonable_encoder(event.model_dump(mode='json'))
        elif isinstance(event, dict):
            payload = jsonable_encoder(event)
        else:
            logger.error(f'Invalid event format passed to broadcast_event: {type(event)}')
            return

        try:
            loop = asyncio.get_running_loop()
            loop.create_task(self.broadcast(payload, role_filter=role_filter))
        except RuntimeError:
            try:
                asyncio.run(self.broadcast(payload, role_filter=role_filter))
            except Exception as e:
                logger.error(f'Error broadcasting event in synchronous fallback: {e}')
        except Exception as e:
            logger.error(f'Failed to schedule broadcast: {e}')

ws_manager = WebSocketManager()