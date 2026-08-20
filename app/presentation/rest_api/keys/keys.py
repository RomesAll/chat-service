from fastapi import APIRouter, Depends
from starlette import status
from starlette.responses import Response, JSONResponse
from business_logic.active_session.active_session_manager import active_session_manager
from business_logic.unit_of_work import UnitOfWork
from business_logic.use_cases.keys.get_private_keys import GetPrivateKeysUseCase
from business_logic.use_cases.keys.sync_private_keys import SyncPrivateKeysUseCase
from database import db
from dtos import JWTAccessToken
from models.user import RoleEnum
from presentation.dependencies.auth import RoleChecker

route = APIRouter()


@route.post(
    path='/keys/devices/sync',
    tags=['Keys'],
    summary='Синхронизация ключей между подключениями (девайсами) пользователя',
    operation_id="sync_devices_user",
)
def sync_devices_user(
        encrypt_private_keys: dict[str, str],
        access_token: JWTAccessToken = Depends(RoleChecker([RoleEnum.DEFAULT_USER, RoleEnum.SUPER_ADMIN]))
):
    SyncPrivateKeysUseCase(
        active_session=active_session_manager
    ).execute(access_token.user_id, encrypt_private_keys)
    return Response(
        status_code=status.HTTP_200_OK,
        content='Новый ключ отправлен на другие подключения для синхронизации'
    )


@route.get(
    path='/keys/encrypt-private-key',
    tags=['Keys'],
    summary='Получение своих зашифрованных приватных ключей',
    operation_id="get_private_key",
)
def get_private_keys(
        access_token: JWTAccessToken = Depends(RoleChecker([RoleEnum.DEFAULT_USER, RoleEnum.SUPER_ADMIN]))
):
    result = GetPrivateKeysUseCase(
        uow=UnitOfWork(db)
    ).execute(access_token.user_id)
    return JSONResponse(
        status_code=status.HTTP_201_CREATED,
        content=result.model_dump(mode='json'),
        media_type = "application/json"
    )
