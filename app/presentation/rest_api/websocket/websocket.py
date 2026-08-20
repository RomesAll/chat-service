from fastapi import APIRouter, Depends
from starlette import status
from starlette.responses import JSONResponse
from starlette.websockets import WebSocket, WebSocketDisconnect
from business_logic.active_session.active_session_manager import active_session_manager
from business_logic.cache.session_key_storage import session_key_storage
from business_logic.encryption.asymmetric import AsymmetricEncrypt
from business_logic.unit_of_work import UnitOfWork
from business_logic.use_cases.encryption.handshake_use_case import HandshakeUseCase
from business_logic.use_cases.user.deactivate_user import DeactivateUseCase
from business_logic.use_cases.user.get_one_user import GetOneUsers
from database import db
from app.shared.dtos import UserDtoBriefInfo
from dtos import JWTAccessToken
from models.user import RoleEnum
from presentation.dependencies.auth import RoleChecker

route = APIRouter()
asymmetric_encrypt = AsymmetricEncrypt()

@route.websocket("/ws/{client_id}")
async def realtime_connection_v1(
        websocket: WebSocket,
        access_token: JWTAccessToken = Depends(RoleChecker([RoleEnum.DEFAULT_USER, RoleEnum.SUPER_ADMIN]))
):
    user_brief_info: UserDtoBriefInfo | None = GetOneUsers(
        uow=UnitOfWork(db)
    ).execute(access_token.user_id).get_brief_info()
    if not user_brief_info:
        return JSONResponse(
            status_code=status.HTTP_404_NOT_FOUND,
            content=f'Информация о пользователе {access_token.user_id} не найдена'
        )
    await websocket.accept()
    session_id = await HandshakeUseCase(
        uow=UnitOfWork(db),
        user_connection=websocket,
        asymmetric_encrypt=asymmetric_encrypt,
        session_key_storage=session_key_storage
    ).execute(access_token.session_id, user_brief_info)
    active_session_manager.add_connection(
        user_info=user_brief_info,
        session_id=session_id,
        connection=websocket
    )
    try:
        while True:
            raw_data: dict = await websocket.receive_json()
            print(raw_data)
    except WebSocketDisconnect:
        is_delete_session_key, is_delete_websocket_conn = DeactivateUseCase(
            active_session_manager=active_session_manager,
            session_key_storage=session_key_storage
        ).execute(
            user_id=access_token.user_id,
            session_id=access_token.session_id
        )
        return JSONResponse(
            status_code=status.HTTP_200_OK,
            content=f'Пользователь {access_token.user_id} отключился, сессионный '
                    f'ключ удален из кеша: {is_delete_session_key} и удален из активной сессии {is_delete_websocket_conn}'
        )