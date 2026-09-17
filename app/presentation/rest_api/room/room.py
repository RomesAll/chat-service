from uuid import UUID
from fastapi import APIRouter, status, Depends
from starlette.responses import JSONResponse

from app.business_logic.use_cases.room.delete_room_use_case import DeleteRoomUseCase
from app.business_logic.use_cases.room.generate_invite_token_in_room_use_case import GenerateInviteTokenInRoomUseCase
from app.business_logic.use_cases.room.get_user_in_room_use_case import GetUserInRoomUseCase
from app.shared.dtos.jwt import TokenType
from app.shared.dtos.room import GenerateUrlInviteRoomRequest
from bootstrap import get_bootstrap
from app.business_logic.unit_of_work import UnitOfWork
from app.business_logic.use_cases.room.get_pub_key_user_in_room_use_case import GetPubKeyUserInRoomUseCase
from app.business_logic.use_cases.room.save_room_use_case import SaveRoomUseCase
from app.business_logic.use_cases.room.save_user_in_room_use_case import SaveUserInRoomUseCase
from app.shared.dtos import (
    JWTAccessToken,
    RoomDtoPostRequest,
    RequestClientDtoHandle,
    ActionType
)
from app.data_access.database.models.user import RoleEnum
from app.presentation.dependencies.base import RequestClientDepends

route = APIRouter()
bootstrap = get_bootstrap()


@route.post(
    path='/rooms',
    tags=['Room'],
    summary='Создание комнаты',
    operation_id='save_room_operation'
)
def save_new_room(
        room_id: UUID,
        room_name: str,
        request_client_dep: RequestClientDtoHandle = Depends(
            RequestClientDepends[JWTAccessToken](
                token_type=TokenType.ACCESS_TOKEN,
                allowed_roles=[RoleEnum.DEFAULT_USER, RoleEnum.SUPER_ADMIN],
                action_type=ActionType.SAVE_NEW_ROOM
            )
        )
):
    result = SaveRoomUseCase(
        uow=UnitOfWork(bootstrap.database),
        dto_audit=request_client_dep.dto_audit
    ).execute(
        dto_request=RoomDtoPostRequest(
            id=room_id,
            name=room_name,
            owner=request_client_dep.token_info.user_id
        ),
    )
    return JSONResponse(
        status_code=status.HTTP_201_CREATED,
        content={
            'message': 'Комната успешно создана',
            'detail': result.model_dump(mode='json')
        }
    )


@route.post(
    path='/rooms/invite/{url_token}',
    tags=['Room'],
    summary='Добавление нового пользователя в комнату',
    operation_id='add_user_in_room_operation'
)
def add_user_in_room(
        url_token: str,
        request_client_dep: RequestClientDtoHandle = Depends(
            RequestClientDepends[JWTAccessToken](
                token_type=TokenType.ACCESS_TOKEN,
                allowed_roles=[RoleEnum.DEFAULT_USER, RoleEnum.SUPER_ADMIN],
                action_type=ActionType.ADD_USER_IN_ROOM
            )
        )
):
    result = SaveUserInRoomUseCase(
        uow=UnitOfWork(bootstrap.database),
        dto_audit=request_client_dep.dto_audit,
        invite_url_service=get_bootstrap().invite_room_service
    ).execute(
        user_id=request_client_dep.token_info.user_id,
        token=url_token
    )
    return JSONResponse(
        status_code=status.HTTP_201_CREATED,
        content={
            'message': f'Пользователь {result.user_id} успешно добавлен в комнату {result.room_id}',
            'detail': result.model_dump(mode='json')
        }
    )


@route.post(
    path='/rooms/{room_id}/invite-token',
    tags=['Room'],
    summary='Получение ссылки для вступления в комнату',
    operation_id='generate_invite_token_room_operation'
)
def generate_invite_token_room(
        room_id: UUID,
        max_uses: int | None = None,
        hours: int = 24,
        request_client_dep: RequestClientDtoHandle = Depends(
            RequestClientDepends[JWTAccessToken](
                token_type=TokenType.ACCESS_TOKEN,
                allowed_roles=[RoleEnum.DEFAULT_USER, RoleEnum.SUPER_ADMIN],
                action_type=ActionType.ADD_USER_IN_ROOM
            )
        )
):
    token, exp = GenerateInviteTokenInRoomUseCase(
        uow=UnitOfWork(bootstrap.database),
        dto_audit=request_client_dep.dto_audit,
        invite_url_service=get_bootstrap().invite_room_service
    ).execute(
        dto_request=GenerateUrlInviteRoomRequest(
            room_id=room_id,
            max_uses=max_uses,
            hours=hours,
            created_by=request_client_dep.token_info.user_id
        )
    )
    return JSONResponse(
        status_code=status.HTTP_201_CREATED,
        content={
            'message': f'Токен для вступления в комнату {room_id} успешно создана',
            'detail': {
                'token': token,
                'expires': exp
            }
        }
    )


@route.get(
    path='/rooms/{room_id}/user-public-key',
    tags=['Room'],
    summary='Получение всех публичных ключей пользователей в комнате',
    operation_id='get_pub_key_operation'
)
def get_pub_key_users_in_room(
        room_id: UUID,
        request_client_dep: RequestClientDtoHandle = Depends(
            RequestClientDepends[JWTAccessToken](
                token_type=TokenType.ACCESS_TOKEN,
                allowed_roles=[RoleEnum.DEFAULT_USER, RoleEnum.SUPER_ADMIN],
                action_type=ActionType.GET_PUBLIC_KEY_USER_IN_ROOM
            )
        )
):
    results = GetPubKeyUserInRoomUseCase(
        uow=UnitOfWork(bootstrap.database),
        dto_audit=request_client_dep.dto_audit
    ).execute(room_id=room_id)
    return JSONResponse(
        status_code=status.HTTP_201_CREATED,
        content={
            'message': 'Публичные ключи пользователей в комнате получены',
            'detail': results
        }
    )


@route.get(
    path='/rooms/{room_id}/users',
    tags=['Room'],
    summary='Получение всех пользователей в комнат',
    operation_id='get_user_in_room_operation'
)
def get_user_in_room(
        room_id: UUID,
        request_client_dep: RequestClientDtoHandle = Depends(
            RequestClientDepends[JWTAccessToken](
                token_type=TokenType.ACCESS_TOKEN,
                allowed_roles=[RoleEnum.DEFAULT_USER, RoleEnum.SUPER_ADMIN],
                action_type=ActionType.GET_PUBLIC_KEY_USER_IN_ROOM
            )
        )
):
    results = GetUserInRoomUseCase(
        uow=UnitOfWork(get_bootstrap().database),
        dto_audit=request_client_dep.dto_audit
    ).execute(
        room_id=room_id,
        user_token_info=request_client_dep.token_info,
    )
    return JSONResponse(
        status_code=status.HTTP_201_CREATED,
        content={
            'message': f'Список пользователей в комнате {room_id} успешно получен',
            'detail': {
                'users_in_room': results
            }
        }
    )


@route.delete(
    path='/rooms/{room_id}',
    tags=['Room'],
    summary='Удаление комнаты',
    operation_id='delete_room_operation'
)
def delete_room(
        room_id: UUID,
        request_client_dep: RequestClientDtoHandle = Depends(
            RequestClientDepends[JWTAccessToken](
                token_type=TokenType.ACCESS_TOKEN,
                allowed_roles=[RoleEnum.DEFAULT_USER, RoleEnum.SUPER_ADMIN],
                action_type=ActionType.GET_PUBLIC_KEY_USER_IN_ROOM
            )
        )
):
    DeleteRoomUseCase(
        uow=UnitOfWork(get_bootstrap().database),
        dto_audit=request_client_dep.dto_audit
    ).execute(
        room_id=room_id,
        user_token_info=request_client_dep.token_info
    )
    return JSONResponse(
        status_code=status.HTTP_200_OK,
        content={
            'message': f'Комната {room_id} успешно удалена',
            'detail': str(room_id)
        }
    )