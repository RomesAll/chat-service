from uuid import UUID
from fastapi import APIRouter, Query
from business_logic.use_cases.registry.use_case_registry import UseCaseRegistry
from dtos import (
    UserDtoGetResponse,
    BaseDtoGetListRequest,
    PaginationDto,
    SortDto,
    SortEnum,
    ActionType, BaseDtoClientRequest, UserDtoPostRequest, UserDtoUpdateRequest
)

route = APIRouter()


@route.get(
    path='/users',
    tags=['Users'],
    summary='Получение пользователей',
    description='Получение списка зарегистрированных пользователей',
    response_model_exclude_none=True,
    response_model=list[UserDtoGetResponse],
    operation_id='get_users_operation'
)
async def get_users(
        limit: int = Query(
            default=10,
            le=100,
            ge=1,
            description="Кол-во выводимых записей за раз"
        ),
        offset: int = Query(
            default=0,
            ge=0,
            description="Кол-во пропускаемых записей"
        ),
        sort_field: list[str] = Query(
            default_factory=list,
            description="Поля для сортировки (порядок важен)"
        ),
        sort_order: list[str] | None = Query(
            default_factory=list,
            description="Порядки сортировки (asc, desc) в том же порядке, что и sort_field"
        ),
):
    dto_request = BaseDtoGetListRequest(
        pagination=PaginationDto(limit=limit, offset=offset),
        sort=[
            SortDto(field=sort_field[i], order_mode=SortEnum(sort_order[i]))
            for i in range(len(sort_field))
        ]
    )
    use_case = UseCaseRegistry.get(dto_request, ActionType.GET_USERS)
    dto_response = await use_case.execute()
    return dto_response


@route.get(
    path='/users/{user_id}',
    tags=['Users'],
    summary='Получить пользователя по id',
    description='Получение одного пользователя по id',
    response_model_exclude_unset=True,
    response_model=UserDtoGetResponse,
    operation_id='get_one_users_operation'
)
def get_one_user(user_id: UUID):
    dto_request = BaseDtoClientRequest(id=user_id)
    use_case = UseCaseRegistry.get(dto_request, ActionType.GET_ONE_USER)
    dto_response = use_case.execute()
    return dto_response


@route.post(
    path='/users',
    tags=['Users'],
    summary='Регистрация пользователя',
    description='Добавление нового пользователя в систему',
    response_model_exclude_unset=True,
    response_model=UserDtoGetResponse,
    operation_id="register_user_operation",
)
def register_user(new_user: UserDtoPostRequest, return_record: bool = True):
    use_case = UseCaseRegistry.get(new_user, ActionType.REGISTER_USER)
    dto_response = use_case.execute()
    if return_record:
        return dto_response
    return {'message': f'Пользователь успешно зарегистрирован'}


@route.put(
path='/users',
    tags=['Users'],
    summary='Обновление пользователя',
    description='Изменение информации о пользователе',
    response_model_exclude_unset=True,
    response_model=UserDtoGetResponse,
    operation_id="update_user_operation",
)
def update_user(update_user_info: UserDtoUpdateRequest, return_record: bool = True):
    use_case = UseCaseRegistry.get(update_user_info, ActionType.UPDATE_USER)
    dto_response = use_case.execute()
    if return_record:
        return dto_response
    return {'message': f'Пользователь успешно обновлен'}


@route.patch(
    path='/users/{user_id}/soft-delete',
    tags=['Users'],
    summary='Мягкое удаление пользователя',
    description='Мягкое удаление с возможность восстановления',
    response_model_exclude_unset=True,
    response_model=UserDtoGetResponse,
    operation_id="soft_delete_operation",
)
def soft_delete_user(user_id: UUID, return_record: bool = True):
    dto_request = BaseDtoClientRequest(id=user_id)
    use_case = UseCaseRegistry.get(dto_request, ActionType.SOFT_DELETE_USER)
    dto_response = use_case.execute()
    if return_record:
        return dto_response
    return {'message': f'Пользователь теперь не активен'}


@route.delete(
    path='/users/{user_id}/hard-delete',
    tags=['Users'],
    summary='Жесткое удаление пользователя',
    description='Жесткое удаление без возможности восстановления',
    response_model_exclude_unset=True,
    response_model=UserDtoGetResponse,
    operation_id="hard_delete_operation",
)
def hard_delete_user(user_id: UUID, return_record: bool = True):
    dto_request = BaseDtoClientRequest(id=user_id)
    use_case = UseCaseRegistry.get(dto_request, ActionType.HARD_DELETE_USER)
    dto_response = use_case.execute()
    if return_record:
        return dto_response
    return {'message': f'Пользователь успешно удален'}


@route.post(
    path='/users/{user_id}/recovery',
    tags=['Users'],
    summary='Восстановление пользователя',
    description='Восстановление пользователя после мягкого удаления',
    response_model_exclude_unset=True,
    response_model=UserDtoGetResponse,
    operation_id="recovery_operation",
)
def recovery_user(user_id: UUID, return_record: bool = True):
    dto_request = BaseDtoClientRequest(id=user_id)
    use_case = UseCaseRegistry.get(dto_request, ActionType.RECOVERY_USER)
    dto_response = use_case.execute()
    if return_record:
        return dto_response
    return {'message': f'Пользователь восстановлен'}
