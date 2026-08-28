from fastapi import APIRouter, Query, status, Depends
from starlette.responses import JSONResponse
from bootstrap import get_bootstrap
from app.business_logic.unit_of_work import UnitOfWork
from app.business_logic.use_cases.user.get_one_user_use_case import GetOneUsers
from app.business_logic.use_cases.user.get_users_use_case import GetUsers
from app.shared.dtos import (
    UserDtoGetResponse,
    BaseDtoGetListRequest,
    PaginationDto,
    SortDto,
    SortEnum,
    JWTRefreshTokenResponse, UserDtoBriefInfo
)
from app.data_access.database.models.user import RoleEnum
from app.presentation.dependencies.auth import RoleChecker

route = APIRouter()
bootstrap = get_bootstrap()

@route.get(
    path='/users',
    tags=['Users'],
    summary='Получение полной информации о пользователях',
    description='Получение списка зарегистрированных пользователей',
    operation_id='get_users_operation'
)
def get_users(
        limit: int = Query(default=10, le=100, ge=1, description="Кол-во выводимых записей за раз"),
        offset: int = Query(default=0, ge=0, description="Кол-во пропускаемых записей"),
        sort_field: list[str] = Query(default_factory=list, description="Поля для сортировки (порядок важен)"),
        sort_order: list[str] | None = Query(default_factory=list, description="Порядки сортировки (asc, desc) в том же порядке, что и sort_field"),
        access_token: JWTRefreshTokenResponse = Depends(RoleChecker([RoleEnum.SUPER_ADMIN]))
):
    dto_request = BaseDtoGetListRequest(
        pagination=PaginationDto(limit=limit, offset=offset),
        sort=[
            SortDto(field=sort_field[i], order_mode=SortEnum(sort_order[i]))
            for i in range(len(sort_field))
        ]
    )
    results: list[UserDtoGetResponse] = GetUsers(
        uow=UnitOfWork(bootstrap.database)
    ).execute(dto_request)
    return JSONResponse(
        status_code=status.HTTP_200_OK,
        content=[result.model_dump(mode='json') for result in results]
    )


@route.get(
    path='/users/{user_id}',
    tags=['Users'],
    summary='Получить полную информацию о пользователе по id',
    description='Получение одного пользователя по id',
    operation_id='get_one_users_operation'
)
def get_one_user(
        user_id: str,
        access_token: JWTRefreshTokenResponse = Depends(RoleChecker([RoleEnum.SUPER_ADMIN]))
):
    result: UserDtoGetResponse = GetOneUsers(
        uow=UnitOfWork(bootstrap.database)
    ).execute(user_id).dto_response
    return JSONResponse(
        status_code=status.HTTP_200_OK,
        content=result.model_dump(mode='json'),
        media_type="application/json"
    )


@route.get(
    path='/users/me',
    tags=['Users'],
    summary='Получить полную информацию о себе',
    description='Получение полную информацию о себе по токену',
    operation_id='get_me_info_operation'
)
def get_me_info(
        access_token: JWTRefreshTokenResponse = Depends(RoleChecker([RoleEnum.DEFAULT_USER, RoleEnum.SUPER_ADMIN]))
):
    result: UserDtoGetResponse = GetOneUsers(
        uow=UnitOfWork(bootstrap.database)
    ).execute(access_token.user_id).dto_response
    return JSONResponse(
        status_code=status.HTTP_200_OK,
        content={
            'message': result.model_dump(mode='json')
        },
        media_type="application/json"
    )


@route.get(
    path='/users/{user_id}/brief-info',
    tags=['Users'],
    summary='Получить краткую информацию о пользователе',
    description='Получение полную информацию о себе по токену',
    operation_id='get_user_brief_info'
)
def get_user_brief_info(
        user_id: str,
        access_token: JWTRefreshTokenResponse = Depends(RoleChecker([RoleEnum.DEFAULT_USER, RoleEnum.SUPER_ADMIN]))
):
    result: UserDtoBriefInfo | None = GetOneUsers(
        uow=UnitOfWork(bootstrap.database)
    ).execute(user_id).get_brief_info()
    if not result:
        return JSONResponse(
            status_code=status.HTTP_404_NOT_FOUND,
            content=f'Информация о пользователе {user_id} не найдена',
            media_type="application/json"
        )
    return JSONResponse(
        status_code=status.HTTP_200_OK,
        content=result.model_dump(mode='json'),
        media_type="application/json"
    )
