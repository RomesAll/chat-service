from fastapi import APIRouter, Response, status, Depends
from starlette.responses import JSONResponse
from business_logic.unit_of_work import UnitOfWork
from business_logic.use_cases.user.update_user import UpdateUser
from database import db
from dtos import (
    UserDtoGetResponse,
    UserDtoUpdateRequest,
    JWTRefreshTokenResponse
)
from models.user import RoleEnum
from presentation.dependencies.auth import RoleChecker

route = APIRouter()


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
        access_token: JWTRefreshTokenResponse = Depends(RoleChecker([RoleEnum.SUPER_ADMIN]))
):
    result: UserDtoGetResponse = UpdateUser(
        uow=UnitOfWork(db)
    ).execute(update_user_info)
    if not return_record:
        return Response(
            status_code=status.HTTP_204_NO_CONTENT
        )
    return JSONResponse(
        status_code=status.HTTP_201_CREATED,
        content=result.model_dump(mode='json'),
        media_type="application/json"
    )

@route.put(
path='/users/me',
    tags=['Users'],
    summary='Обновление информацию о себе',
    description='Изменение информации о себе по токену',
    operation_id="update_my_user_info_operation",
)
def update_me(
        update_user_info: UserDtoUpdateRequest,
        return_record: bool = True,
        access_token: JWTRefreshTokenResponse = Depends(RoleChecker([RoleEnum.DEFAULT_USER, RoleEnum.SUPER_ADMIN]))
):
    if access_token.user_id != update_user_info.id:
        return JSONResponse(
            status_code=status.HTTP_403_FORBIDDEN,
            content='Id пользователя в токене не совпадает с id пользователя в теле запроса',
            media_type="application/json"
        )
    result: UserDtoGetResponse = UpdateUser(
        uow=UnitOfWork(db)
    ).execute(update_user_info)
    if not return_record:
        return Response(
            status_code=status.HTTP_204_NO_CONTENT
        )
    return JSONResponse(
        status_code=status.HTTP_201_CREATED,
        content=result.model_dump(mode='json'),
        media_type="application/json"
    )