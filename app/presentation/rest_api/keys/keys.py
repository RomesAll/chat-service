from starlette.responses import Response
from bootstrap import get_bootstrap
from app.business_logic.use_cases.keys.get_private_keys_use_case import GetPrivateKeysUseCase
from app.business_logic.use_cases.keys.save_private_keys_use_case import SavePrivateKeysUseCase
from app.business_logic.use_cases.keys.save_public_key_use_case import SavePublicKeyUseCase
from app.business_logic.use_cases.keys.sync_private_keys_use_case import SyncPrivateKeysUseCase
from fastapi import APIRouter, status, Depends
from starlette.responses import JSONResponse
from app.business_logic.unit_of_work import UnitOfWork
from app.business_logic.use_cases.keys.get_public_key_use_case import GetPublicKeyUseCase
from app.shared.dtos import JWTAccessToken
from app.shared.dtos.keys import PublicKeyDtoCreate, PrivateKeyDtoCreate, PublicKeyRequest, PrivateKeyRequest
from app.data_access.database.models.user import RoleEnum
from app.presentation.dependencies.auth import RoleChecker

route = APIRouter()
bootstrap = get_bootstrap()

@route.get(
    path='/users/me/keys/public-key',
    tags=['Keys', 'Users'],
    summary='Получение своего текущего публичного ключа',
    operation_id="get_my_public_key",
)
async def get_my_public_key(
        access_token: JWTAccessToken = Depends(RoleChecker([RoleEnum.DEFAULT_USER, RoleEnum.SUPER_ADMIN]))
):
    result = GetPublicKeyUseCase(
        uow=UnitOfWork(bootstrap.database)
    ).execute(access_token.user_id)
    return JSONResponse(
        status_code=status.HTTP_200_OK,
        content=result.model_dump(mode='json'),
        media_type="application/json"
    )


@route.get(
    path='/users/{user_id}/keys/public-key',
    tags=['Keys', 'Users'],
    summary='Получение публичного ключа пользователя',
    operation_id="get_user_public_key",
)
async def get_user_public_key(
        user_id: str,
        access_token: JWTAccessToken = Depends(RoleChecker([RoleEnum.DEFAULT_USER, RoleEnum.SUPER_ADMIN]))
):
    result = GetPublicKeyUseCase(
        uow=UnitOfWork(bootstrap.database)
    ).execute(user_id)
    return JSONResponse(
        status_code=status.HTTP_200_OK,
        content=result.model_dump(mode='json'),
        media_type="application/json"
    )


@route.post(
    path='/users/me/keys/devices/sync',
    tags=['Keys', 'Users'],
    summary='Синхронизация ключей между подключениями (девайсами) пользователя',
    operation_id="sync_devices_user",
)
def sync_devices_user(
        encrypt_private_keys: dict[str, str],
        access_token: JWTAccessToken = Depends(RoleChecker([RoleEnum.DEFAULT_USER, RoleEnum.SUPER_ADMIN]))
):
    SyncPrivateKeysUseCase(
        active_session=bootstrap.active_session_manager
    ).execute(access_token.user_id, encrypt_private_keys)
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
        access_token: JWTAccessToken = Depends(RoleChecker([RoleEnum.DEFAULT_USER, RoleEnum.SUPER_ADMIN]))
):
    try:
        results = GetPrivateKeysUseCase(
            uow=UnitOfWork(bootstrap.database)
        ).execute(access_token.user_id)
        return JSONResponse(
            status_code=status.HTTP_201_CREATED,
            content=[res.model_dump(mode='json') for res in results],
            media_type = "application/json"
        )
    except Exception:
        return JSONResponse(
            status_code=status.HTTP_404_NOT_FOUND,
            content='Приватных ключей нет',
            media_type="application/json"
        )


@route.post(
    path='/users/me/keys/save/public-key',
    tags=['Keys', 'Users'],
    summary='Сохранение публичного ключа на сервере',
    operation_id="save_public_key",
)
def save_public_key(
        key_info: PublicKeyRequest,
        access_token: JWTAccessToken = Depends(RoleChecker([RoleEnum.DEFAULT_USER, RoleEnum.SUPER_ADMIN]))
):
    SavePublicKeyUseCase(
        uow=UnitOfWork(bootstrap.database)
    ).execute(PublicKeyDtoCreate(
        user_id=access_token.user_id,
        public_key=key_info.public_key,
        version=key_info.version
    ))
    return JSONResponse(
        status_code=status.HTTP_201_CREATED,
        content=f'Публичный ключ пользователя {access_token.user_id} сохранен',
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
        access_token: JWTAccessToken = Depends(RoleChecker([RoleEnum.DEFAULT_USER, RoleEnum.SUPER_ADMIN]))
):
    results = SavePrivateKeysUseCase(
        uow=UnitOfWork(bootstrap.database)
    ).execute(PrivateKeyDtoCreate(
        user_id=access_token.user_id,
        private_key=key_info.private_key,
        version=key_info.version
    ))
    return JSONResponse(
        status_code=status.HTTP_201_CREATED,
        content=[res.model_dump(mode='json') for res in results],
        media_type="application/json"
    )