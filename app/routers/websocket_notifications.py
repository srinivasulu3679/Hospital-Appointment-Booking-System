
from fastapi import APIRouter, WebSocket, WebSocketDisconnect

from app.auth.security import decode_access_token
from app.utils.connection_manager import manager

router = APIRouter(tags=["WebSocket Notifications"])


@router.websocket("/ws/notifications")
async def notification_websocket(websocket: WebSocket, token: str):
    try:
        payload = decode_access_token(token)
        user_id = payload.get("sub")

        if not user_id:
            await websocket.close(code=1008)
            return

        user_id = int(user_id)

    except Exception:
        await websocket.close(code=1008)
        return

    await manager.connect(user_id, websocket)

    try:
        while True:
            # Keep the connection open; client messages are received here.
            await websocket.receive_text()

    except WebSocketDisconnect:
        manager.disconnect(user_id, websocket)

    except Exception:
        manager.disconnect(user_id, websocket)
