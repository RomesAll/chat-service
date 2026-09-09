from starlette.responses import Response
from bootstrap import get_bootstrap
from app.business_logic.use_cases import (
    GetPrivateKeysUseCase,
    SavePrivateKeysUseCase,
    SavePublicKeyUseCase,
    SyncPrivateKeysUseCase,
    GetPublicKeyUseCase,
)
from fastapi import APIRouter, status, Depends
from starlette.responses import JSONResponse
from app.business_logic.unit_of_work import UnitOfWork
from app.shared.dtos import (
    JWTAccessToken,
    PublicKeyDtoCreate,
    PrivateKeyDtoCreate,
    PublicKeyRequest,
    PrivateKeyRequest
)
from app.data_access.database.models.user import RoleEnum
from app.presentation.dependencies.base import RequestClientDepends
from dtos import ActionType, RequestClientDtoHandle
from exceptions import RecordNotFound

route = APIRouter()
bootstrap = get_bootstrap()


@route.get(
    path='/users/me/keys/public-key',
    tags=['Keys', 'Users'],
    summary='Получение своего текущего публичного ключа',
    operation_id="get_my_public_key",
)
async def get_my_public_key(
        request_client_dep: RequestClientDtoHandle = Depends(
            RequestClientDepends[JWTAccessToken](
                allowed_roles=[RoleEnum.DEFAULT_USER, RoleEnum.SUPER_ADMIN],
                action_type=ActionType.GET_USER_PUBLIC_KEY
            )
        )
):
    try:
        result = GetPublicKeyUseCase(
            uow=UnitOfWork(bootstrap.database),
            dto_audit=request_client_dep.dto_audit
        ).execute(
            user_id=request_client_dep.token_info.user_id,
        )
        return JSONResponse(
            status_code=status.HTTP_200_OK,
            content=result.model_dump(mode='json'),
            media_type="application/json"
        )
    except RecordNotFound:
        return Response(
            status_code=status.HTTP_404_NOT_FOUND,
            content='Публичный ключ не найден'
        )


@route.get(
    path='/users/{user_id}/keys/public-key',
    tags=['Keys', 'Users'],
    summary='Получение публичного ключа пользователя',
    operation_id="get_user_public_key",
)
async def get_user_public_key(
        user_id: str,
        request_client_dep: RequestClientDtoHandle = Depends(
            RequestClientDepends[JWTAccessToken](
                allowed_roles=[RoleEnum.DEFAULT_USER, RoleEnum.SUPER_ADMIN],
                action_type=ActionType.GET_USER_PUBLIC_KEY
            )
        )
):
    try:
        result = GetPublicKeyUseCase(
            uow=UnitOfWork(bootstrap.database),
            dto_audit=request_client_dep.dto_audit
        ).execute(
            user_id=user_id,
        )
        return JSONResponse(
            status_code=status.HTTP_200_OK,
            content=result.model_dump(mode='json'),
            media_type="application/json"
        )
    except RecordNotFound:
        return Response(
            status_code=status.HTTP_404_NOT_FOUND,
            content='Публичный ключ не найден'
        )


@route.post(
    path='/users/me/keys/devices/sync',
    tags=['Keys', 'Users'],
    summary='Синхронизация ключей между подключениями (девайсами) пользователя',
    operation_id="sync_devices_user",
)
def sync_devices_user(
        encrypt_private_keys: dict[str, str],
        request_client_dep: RequestClientDtoHandle = Depends(
            RequestClientDepends[JWTAccessToken](
                allowed_roles=[RoleEnum.DEFAULT_USER, RoleEnum.SUPER_ADMIN],
                action_type=ActionType.SYNC_DEVICES_USER
            )
        )
):
    SyncPrivateKeysUseCase(
        active_session=bootstrap.active_session_manager,
        dto_audit=request_client_dep.dto_audit
    ).execute(
        user_id=request_client_dep.token_info.user_id,
        encrypt_private_keys=encrypt_private_keys,
    )
    return Response(
        status_code=status.HTTP_200_OK,
        content='Новый ключ отправлен на другие подключения для синхронизации'
    )


@route.get(
    path='/users/me/keys/encrypt-private-key',
    tags=['Keys', 'Users'],
    summary='Получение своих зашифрованных приватных ключей',
    operation_id="get_private_key",
)
def get_private_keys(
        request_client_dep: RequestClientDtoHandle = Depends(
            RequestClientDepends[JWTAccessToken](
                allowed_roles=[RoleEnum.DEFAULT_USER, RoleEnum.SUPER_ADMIN],
                action_type=ActionType.GET_USER_PRIVATE_KEYS
            )
        )
):
    try:
        results = GetPrivateKeysUseCase(
            uow=UnitOfWork(bootstrap.database),
            dto_audit=request_client_dep.dto_audit
        ).execute(
            user_id=request_client_dep.token_info.user_id,
        )
        return JSONResponse(
            status_code=status.HTTP_201_CREATED,
            content=[res.model_dump(mode='json') for res in results],
            media_type = "application/json"
        )
    except RecordNotFound:
        return Response(
            status_code=status.HTTP_404_NOT_FOUND,
            content='Приватный ключи не найдены'
        )


@route.post(
    path='/users/me/keys/save/public-key',
    tags=['Keys', 'Users'],
    summary='Сохранение публичного ключа на сервере',
    operation_id="save_public_key",
)
def save_public_key(
        key_info: PublicKeyRequest,
        request_client_dep: RequestClientDtoHandle = Depends(
            RequestClientDepends[JWTAccessToken](
                allowed_roles=[RoleEnum.DEFAULT_USER, RoleEnum.SUPER_ADMIN],
                action_type=ActionType.SAVE_PUBLIC_KEY
            )
        )
):
    SavePublicKeyUseCase(
        uow=UnitOfWork(bootstrap.database),
        dto_audit=request_client_dep.dto_audit
    ).execute(
        key_info=PublicKeyDtoCreate(
            user_id=request_client_dep.token_info.user_id,
            public_key=key_info.public_key,
            version=key_info.version
        ),
    )
    return JSONResponse(
        status_code=status.HTTP_201_CREATED,
        content=f'Публичный ключ пользователя {request_client_dep.token_info.user_id} сохранен',
        media_type="application/json"
    )


@route.post(
    path='/users/me/keys/save/private-key',
    tags=['Keys', 'Users'],
    summary='Сохранение приватного ключа на сервере',
    operation_id="save_private_key",
)
def save_private_key(
        key_info: PrivateKeyRequest,
        request_client_dep: RequestClientDtoHandle = Depends(
            RequestClientDepends[JWTAccessToken](
                allowed_roles=[RoleEnum.DEFAULT_USER, RoleEnum.SUPER_ADMIN],
                action_type=ActionType.SAVE_PRIVATE_KEY
            )
        )
):
    results = SavePrivateKeysUseCase(
        uow=UnitOfWork(bootstrap.database),
        dto_audit=request_client_dep.dto_audit
    ).execute(
        key_info=PrivateKeyDtoCreate(
            user_id=request_client_dep.token_info.user_id,
            private_key=key_info.private_key,
            version=key_info.version
        ),
    )
    return JSONResponse(
        status_code=status.HTTP_201_CREATED,
        content=[res.model_dump(mode='json') for res in results],
        media_type="application/json"
    )