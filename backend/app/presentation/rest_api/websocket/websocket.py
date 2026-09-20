from uuid import uuid4
from fastapi import APIRouter, Depends
from starlette import status
from starlette.responses import JSONResponse
from starlette.websockets import WebSocket, WebSocketDisconnect
from bootstrap import get_bootstrap
from app.business_logic.unit_of_work import UnitOfWork
from app.business_logic.use_cases.encryption.handshake_use_case import HandshakeUseCase
from app.business_logic.use_cases.user.deactivate_user_use_case import DeactivateUseCase
from app.business_logic.use_cases.user.get_one_user_use_case import GetOneUsers
from app.shared.dtos import UserDtoBriefInfo
from app.shared.dtos import AuditPostDto, ActionType
from app.presentation.dependencies import AuditDep

route = APIRouter()
bootstrap = get_bootstrap()


@route.websocket("/ws/{client_id}")
async def realtime_connection_v1(
        websocket: WebSocket,
        client_id: str,
        dto_audit: AuditPostDto = Depends(AuditDep)
):
    dto_audit.user_id = client_id
    dto_audit.action = ActionType.GET_ONE_USER
    user_brief_info: UserDtoBriefInfo | None = GetOneUsers(
        uow=UnitOfWork(bootstrap.database),
        dto_audit=dto_audit
    ).execute(client_id).get_brief_info()
    if not user_brief_info:
        return JSONResponse(
            status_code=status.HTTP_404_NOT_FOUND,
            content=f'Информация о пользователе {client_id} не найдена'
        )
    await websocket.accept()
    session_id = uuid4()
    dto_audit.action = ActionType.HANDSHAKE
    await HandshakeUseCase(
        uow=UnitOfWork(bootstrap.database),
        active_session_manager = bootstrap.active_session_manager,
        user_connection=websocket,
        asymmetric_encrypt=bootstrap.asymmetric_encrypt,
        session_key_storage=bootstrap.redis_cache.session_key_storage,
        dto_audit=dto_audit
    ).execute(session_id, user_brief_info, websocket)
    try:
        while True:
            raw_data: dict = await websocket.receive_json()
            print(raw_data)
    except WebSocketDisconnect:
        dto_audit.action = ActionType.DEACTIVATE
        DeactivateUseCase(
            active_session_manager=bootstrap.active_session_manager,
            session_key_storage=bootstrap.redis_cache.session_key_storage
        ).execute(
            user_id=client_id,
            session_id=session_id
        )
        return JSONResponse(
            status_code=status.HTTP_200_OK,
            content=f'Пользователь {client_id} отключился'
        )