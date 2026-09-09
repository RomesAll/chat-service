from uuid import UUID
from fastapi import APIRouter, status, Depends
from starlette.responses import JSONResponse
from bootstrap import get_bootstrap
from app.business_logic.unit_of_work import UnitOfWork
from app.business_logic.use_cases.room.get_pub_key_user_in_room_use_case import GetPubKeyUserInRoomUseCase
from app.business_logic.use_cases.room.save_room_use_case import SaveRoomUseCase
from app.business_logic.use_cases.room.save_user_in_room_use_case import SaveUserInRoomUseCase
from app.shared.dtos import (
    JWTAccessToken,
    RoomDtoPostRequest,
    UserInRoomPostRequest,
    RequestClientDtoHandle,
    ActionType
)
from app.data_access.database.models.user import RoleEnum
from app.presentation.dependencies.base import RequestClientDepends

route = APIRouter()
bootstrap = get_bootstrap()

@route.post(
    path='/rooms/new-room',
    tags=['Room'],
    summary='Создание комнаты',
    operation_id='save_room_operation'
)
def save_new_room(
        dto_request: RoomDtoPostRequest,
        request_client_dep: RequestClientDtoHandle = Depends(
            RequestClientDepends[JWTAccessToken](
                allowed_roles=[RoleEnum.DEFAULT_USER, RoleEnum.SUPER_ADMIN],
                action_type=ActionType.SAVE_NEW_ROOM
            )
        )
):
    result = SaveRoomUseCase(
        uow=UnitOfWork(bootstrap.database),
        dto_audit=request_client_dep.dto_audit
    ).execute(
        dto_request=dto_request,
    )
    return JSONResponse(
        status_code=status.HTTP_201_CREATED,
        content=result.model_dump(mode='json')
    )


@route.post(
    path='/rooms/{room_id}/users/{user_id}/add',
    tags=['Room'],
    summary='Добавление нового пользователя в комнату',
    operation_id='add_user_in_room_operation'
)
def add_user_in_room(
        user_id: str,
        room_id: UUID,
        request_client_dep: RequestClientDtoHandle = Depends(
            RequestClientDepends[JWTAccessToken](
                allowed_roles=[RoleEnum.DEFAULT_USER, RoleEnum.SUPER_ADMIN],
                action_type=ActionType.ADD_USER_IN_ROOM
            )
        )
):
    result = SaveUserInRoomUseCase(
        uow=UnitOfWork(bootstrap.database),
        dto_audit=request_client_dep.dto_audit
    ).execute(
        dto_request=UserInRoomPostRequest(
            room_id=room_id,
            user_id=user_id
        ),
    )
    return JSONResponse(
        status_code=status.HTTP_201_CREATED,
        content=result.model_dump(mode='json')
    )


@route.get(
    path='/room/{room_id}/user-public-key',
    tags=['Room'],
    summary='Получение всех публичных ключей пользователей в комнате',
    operation_id='get_pub_key_operation'
)
def get_pub_key_users_in_room(
        room_id: UUID,
        request_client_dep: RequestClientDtoHandle = Depends(
            RequestClientDepends[JWTAccessToken](
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
        content=results
    )