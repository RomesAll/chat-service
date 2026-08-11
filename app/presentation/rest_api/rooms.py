from uuid import UUID
from fastapi import APIRouter
from business_logic.use_cases.registry.use_case_registry import UseCaseRegistry
from dtos import (
    RoomDtoGetResponse,
    ActionType,
    RoomDtoPostRequest,
    InvitationUserInRoomDtoRequest
)

route = APIRouter()


@route.post(
    path='/room',
    tags=['Rooms'],
    summary='Добавление комнаты',
    description='Добавление новой комнаты',
    response_model_exclude_unset=True,
    response_model=RoomDtoGetResponse,
    operation_id="create_room_operation",
)
def create_room(new_user: RoomDtoPostRequest, return_record: bool = True):
    use_case = UseCaseRegistry.get(new_user, ActionType.CREATE_ROOM)
    dto_response = use_case.execute()
    if return_record:
        return dto_response
    return {'message': f'Пользователь успешно зарегистрирован'}


@route.post(
    path='/room/{room_id}/invitation/users/{user_id}',
    tags=['Rooms'],
    summary='Приглашение в комнату',
    description='Приглашение в комнату',
    operation_id="invitation_room_operation",
)
def invitation(room_id: UUID, user_id: UUID):
    dto_request = InvitationUserInRoomDtoRequest(
        room_id=room_id,
        user_id=user_id
    )
    use_case = UseCaseRegistry.get(dto_request, ActionType.INVITATION_USER_IN_ROOM)
    use_case.execute()
    return {'message': f'Пользователь {user_id} добавлен в комнату {room_id}'}