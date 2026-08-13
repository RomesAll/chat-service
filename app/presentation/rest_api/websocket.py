from fastapi import APIRouter, Depends
from starlette.websockets import WebSocket, WebSocketDisconnect
from business_logic.active_session.active_session_manager import active_session_manager
from business_logic.unit_of_work import UnitOfWork
from business_logic.use_cases.user.get_one_user import GetOneUsers
from database import db
from dtos import UserDtoBriefInfo, UserDtoGetResponse
from presentation.dependencies.auth import AuthChecker

route = APIRouter()


@route.websocket("/ws/{client_id}")
async def realtime_connection_v1(
        websocket: WebSocket,
        user_info: dict = Depends(AuthChecker())
):
    await websocket.accept()
    user_full_info: UserDtoGetResponse = GetOneUsers(
        uow=UnitOfWork(db)
    ).execute(user_info['user_id'])
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
        print(user_info['user_id'], 'отключился')
