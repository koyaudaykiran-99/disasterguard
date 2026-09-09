import uuid
import logging
from typing import Optional
from fastapi import APIRouter, WebSocket, WebSocketDisconnect, Query
import jwt

from app.core.config import settings
from app.services.websocket_manager import ws_manager
from app.schemas.events import DomainEvent, EventType
from datetime import datetime, timezone

logger = logging.getLogger('disasterguard.websocket')

router = APIRouter()

@router.websocket('/ws')
async def websocket_endpoint(
    websocket: WebSocket,
    token: Optional[str] = Query(None)
):
    role = 'OPERATOR'
    user_id = None
    client_id = f'client_{uuid.uuid4().hex[:6]}'

    if token and token != 'demo':
        try:
            payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
            user_id = payload.get('sub')
            role = payload.get('role', 'OPERATOR').upper()
            client_id = f'user_{user_id}_{uuid.uuid4().hex[:4]}'
        except Exception as e:
            logger.warning(f'WebSocket token decode failed: {e}. Falling back to default role.')

    await ws_manager.connect(websocket, client_id=client_id, role=role, user_id=user_id)

    # Send initial connection handshake confirmation
    try:
        welcome_event = DomainEvent(
            event=EventType.SYSTEM_STATUS_CHANGED,
            timestamp=datetime.now(timezone.utc).isoformat(),
            entity_type='system',
            severity='LOW',
            data={
                'status': 'connected',
                'client_id': client_id,
                'role': role,
                'message': 'Real-time WebSocket connection active'
            }
        )
        await websocket.send_json(welcome_event.model_dump())
    except Exception as e:
        logger.warning(f'Could not send welcome message to {client_id}: {e}')

    try:
        while True:
            # Keep connection open and accept ping / client pulses
            data = await websocket.receive_text()
            if data == 'ping':
                await websocket.send_text('pong')
            elif data.startswith('{'):
                # Client-sent message/ping
                pass
    except WebSocketDisconnect:
        ws_manager.disconnect(websocket)
    except Exception as e:
        logger.warning(f'WebSocket connection closed with error for {client_id}: {e}')
        ws_manager.disconnect(websocket)
