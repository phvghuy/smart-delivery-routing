from fastapi import APIRouter, Depends, WebSocket, WebSocketDisconnect

from smart_delivery_routing.infrastructure.supabase.repositories.auth import get_user_role
from smart_delivery_routing.infrastructure.websocket import ConnectionManager
from ..dependencies import get_ws_manager

router = APIRouter(tags=["websocket"])


@router.websocket("/ws")
async def websocket_endpoint(
    ws: WebSocket,
    token: str,
    manager: ConnectionManager = Depends(get_ws_manager),
) -> None:
    if get_user_role(token) != "admin":
        await ws.close(code=4403)
        return

    await manager.connect(ws)
    try:
        while True:
            await ws.receive_text()
    except WebSocketDisconnect:
        manager.disconnect(ws)
