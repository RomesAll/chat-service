from uuid import UUID
from fastapi import APIRouter
from starlette.websockets import WebSocket, WebSocketDisconnect
from business_logic.active_session.active_session_manager import active_session_manager
from dtos import UserDtoBriefInfo

route = APIRouter()


@route.websocket("/ws/{client_id}")
async def realtime_connection_v1(websocket: WebSocket, client_id: UUID):
    await websocket.accept()
    user_info = UserDtoBriefInfo(
        id=client_id,
        user_name=f'user-{client_id}',
        years_old=18,
        email='test@gmail.com'
    )
    active_session_manager.add_connection(user_info, websocket)
    try:
        while True:
            raw_data: dict = await websocket.receive_json()
            print(raw_data)
    except WebSocketDisconnect:
        print(client_id, 'отключился')
