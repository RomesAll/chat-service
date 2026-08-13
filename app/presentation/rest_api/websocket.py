from fastapi import APIRouter
from starlette.websockets import WebSocket, WebSocketDisconnect
from business_logic.active_session.active_session_manager import active_session_manager
from business_logic.unit_of_work import UnitOfWork
from business_logic.use_cases.user.get_one_user import GetOneUsers
from database import db
from app.shared.dtos import UserDtoBriefInfo, UserDtoGetResponse

route = APIRouter()


@route.websocket("/ws/{client_id}")
async def realtime_connection_v1(
        websocket: WebSocket,
        client_id: str
        #user_info: dict = Depends(AuthChecker())
):
    await websocket.accept()
    user_full_info: UserDtoGetResponse = GetOneUsers(
        uow=UnitOfWork(db)
    ).execute(client_id)
    user_brief_info = UserDtoBriefInfo(
        id=user_full_info.id,
        user_name=user_full_info.user_name,
        years_old=user_full_info.years_old,
        email=user_full_info.email,
        phone=user_full_info.phone
    )
    active_session_manager.add_connection(user_brief_info, websocket)
    try:
        while True:
            raw_data: dict = await websocket.receive_json()
            print(raw_data)
    except WebSocketDisconnect:
        print(client_id, 'отключился')
