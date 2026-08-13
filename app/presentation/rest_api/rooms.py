from fastapi import APIRouter, Response, status, Depends
from business_logic.active_session.active_session_manager import active_session_manager
from business_logic.unit_of_work import UnitOfWork
from business_logic.use_cases.room.create_room import CreateRoom
from business_logic.use_cases.room.invitation_user_in_room import InvitationUserInRoom
from database import db
from dtos import (
    RoomDtoPostRequest,
    InvitationUserInRoomDtoRequest, RoomDtoGetResponse
)
from models.user import RoleEnum
from presentation.dependencies.auth import AuthChecker, RoleChecker

route = APIRouter()


@route.post(
    path='/room',
    tags=['Rooms'],
    summary='Добавление комнаты',
    description='Добавление новой комнаты',
    operation_id="create_room_operation",
)
def create_room(
        new_room: RoomDtoPostRequest,
        return_record: bool = True,
        user_info: dict = Depends(RoleChecker([RoleEnum.DEFAULT_USER, RoleEnum.SUPER_ADMIN])),
):
    result: RoomDtoGetResponse = CreateRoom(
        uow=UnitOfWork(db),
    ).execute(new_room)
    if not return_record:
        return Response(
            status_code=status.HTTP_204_NO_CONTENT
        )
    return Response(
        status_code=status.HTTP_201_CREATED,
        content=result.model_dump_json(exclude_none=True),
        media_type="application/json"
    )


@route.post(
    path='/room/{room_id}/invitation/users/{user_id}',
    tags=['Rooms'],
    summary='Добавление в комнату',
    description='Добавление нового пользователя в комнату',
    operation_id="invitation_room_operation",
)
def invitation_user_in_room(
        invitation_user: InvitationUserInRoomDtoRequest,
        user_info: dict = Depends(RoleChecker([RoleEnum.DEFAULT_USER, RoleEnum.SUPER_ADMIN])),
):
    InvitationUserInRoom(
        uow=UnitOfWork(db),
        active_session_manager=active_session_manager
    ).execute(invitation_user)
    return Response(
        status_code=status.HTTP_201_CREATED,
        content=f'{invitation_user.user_id} добавил {user_info['user_id']} в комнату {invitation_user.room_id}'
    )