from fastapi import APIRouter, WebSocket, WebSocketDisconnect

from app.api.ws import active_connections


router = APIRouter(prefix="/api/v1", tags=["websocket-v1"])


@router.websocket("/ws/officer/{officer_id}")
async def officer_ws(websocket: WebSocket, officer_id: str):
    await websocket.accept()
    active_connections[officer_id] = websocket
    try:
        while True:
            await websocket.receive_text()
    except WebSocketDisconnect:
        if officer_id in active_connections:
            del active_connections[officer_id]