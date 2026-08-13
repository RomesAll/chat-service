from fastapi import APIRouter, Query, Response, status, Depends
from starlette.responses import JSONResponse
from business_logic.unit_of_work import UnitOfWork
from business_logic.use_cases.user.get_one_user import GetOneUsers
from business_logic.use_cases.user.get_users import GetUsers
from business_logic.use_cases.user.hard_delete_user import HardDeleteUser
from business_logic.use_cases.user.recovery_user import RecoveryUser
from business_logic.use_cases.user.soft_delete_user import SoftDeleteUser
from business_logic.use_cases.user.update_user import UpdateUser
from database import db
from dtos import (
    UserDtoGetResponse,
    BaseDtoGetListRequest,
    PaginationDto,
    SortDto,
    SortEnum,
    UserDtoUpdateRequest
)
from models.user import RoleEnum
from presentation.dependencies.auth import AuthChecker, RoleChecker

route = APIRouter()


@route.get(
    path='/users',
    tags=['Users'],
    summary='Получение пользователей',
    description='Получение списка зарегистрированных пользователей',
    operation_id='get_users_operation'
)
def get_users(
        limit: int = Query(default=10, le=100, ge=1, description="Кол-во выводимых записей за раз"),
        offset: int = Query(default=0, ge=0, description="Кол-во пропускаемых записей"),
        sort_field: list[str] = Query(default_factory=list, description="Поля для сортировки (порядок важен)"),
        sort_order: list[str] | None = Query(default_factory=list, description="Порядки сортировки (asc, desc) в том же порядке, что и sort_field"),
        user_info: dict = Depends(RoleChecker([RoleEnum.SUPER_ADMIN]))
):
    dto_request = BaseDtoGetListRequest(
        pagination=PaginationDto(limit=limit, offset=offset),
        sort=[
            SortDto(field=sort_field[i], order_mode=SortEnum(sort_order[i]))
            for i in range(len(sort_field))
        ]
    )
    results: list[UserDtoGetResponse] = GetUsers(
        uow=UnitOfWork(db)
    ).execute(dto_request)
    return JSONResponse(
        status_code=status.HTTP_200_OK,
        content={
            'contents': [result.model_dump(exclude_unset=True, mode='json') for result in results]
        }
    )


@route.get(
    path='/users/{user_id}',
    tags=['Users'],
    summary='Получить пользователя по id',
    description='Получение одного пользователя по id',
    operation_id='get_one_users_operation'
)
def get_one_user(
        user_id: str,
        user_info: dict = Depends(RoleChecker([RoleEnum.DEFAULT_USER, RoleEnum.SUPER_ADMIN]))
):
    result: UserDtoGetResponse = GetOneUsers(
        uow=UnitOfWork(db)
    ).execute(user_id)
    return Response(
        status_code=status.HTTP_200_OK,
        content=result.model_dump_json(exclude_unset=True),
        media_type="application/json"
    )


@route.put(
path='/users',
    tags=['Users'],
    summary='Обновление пользователя',
    description='Изменение информации о пользователе',
    operation_id="update_user_operation",
)
def update_user(
        update_user_info: UserDtoUpdateRequest,
        return_record: bool = True,
        user_info: dict = Depends(RoleChecker([RoleEnum.DEFAULT_USER, RoleEnum.SUPER_ADMIN]))
):
    result: UserDtoGetResponse = UpdateUser(
        uow=UnitOfWork(db)
    ).execute(update_user_info)
    if not return_record:
        return Response(
            status_code=status.HTTP_204_NO_CONTENT
        )
    return Response(
        status_code=status.HTTP_201_CREATED,
        content=result.model_dump_json(exclude_none=True),
        media_type="application/json"
    )


@route.patch(
    path='/users/{user_id}/soft-delete',
    tags=['Users'],
    summary='Мягкое удаление пользователя',
    description='Мягкое удаление с возможность восстановления',
    response_model_exclude_unset=True,
    response_model=UserDtoGetResponse,
    operation_id="soft_delete_operation",
)
def soft_delete_user(
        user_id: str,
        user_info: dict = Depends(RoleChecker([RoleEnum.DEFAULT_USER, RoleEnum.SUPER_ADMIN]))
):
    result: str = SoftDeleteUser(
        uow=UnitOfWork(db)
    ).execute(user_id)
    return Response(
        status_code=status.HTTP_204_NO_CONTENT,
        content=result
    )


@route.delete(
    path='/users/{user_id}/hard-delete',
    tags=['Users'],
    summary='Жесткое удаление пользователя',
    description='Жесткое удаление без возможности восстановления',
    operation_id="hard_delete_operation",
)
def hard_delete_user(
        user_id: str,
        user_info: dict = Depends(RoleChecker([RoleEnum.DEFAULT_USER, RoleEnum.SUPER_ADMIN]))
):
    result: str = HardDeleteUser(
        uow=UnitOfWork(db)
    ).execute(user_id)
    return Response(
        status_code=status.HTTP_204_NO_CONTENT,
        content=result
    )


@route.post(
    path='/users/{user_id}/recovery',
    tags=['Users'],
    summary='Восстановление пользователя',
    description='Восстановление пользователя после мягкого удаления',
    operation_id="recovery_operation",
)
def recovery_user(
        user_id: str,
        return_record: bool = True,
        user_info: dict = Depends(RoleChecker([RoleEnum.DEFAULT_USER, RoleEnum.SUPER_ADMIN]))
):
    result: UserDtoGetResponse = RecoveryUser(
        uow=UnitOfWork(db)
    ).execute(user_id)
    if not return_record:
        return Response(
            status_code=status.HTTP_204_NO_CONTENT
        )
    return Response(
        status_code=status.HTTP_201_CREATED,
        content=result.model_dump_json(exclude_unset=True),
        media_type="application/json"
    )