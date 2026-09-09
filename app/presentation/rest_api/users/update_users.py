from fastapi import APIRouter, Response, status, Depends
from starlette.responses import JSONResponse
from bootstrap import get_bootstrap
from app.business_logic.unit_of_work import UnitOfWork
from app.business_logic.use_cases.user.update_user_use_case import UpdateUser
from app.shared.dtos import (
    UserDtoGetResponse,
    UserDtoUpdateRequest,
)
from app.data_access.database.models.user import RoleEnum
from dtos import RequestClientDtoHandle, JWTAccessToken, ActionType
from presentation.dependencies import RequestClientDepends

route = APIRouter()
bootstrap = get_bootstrap()

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
        request_client_dep: RequestClientDtoHandle = Depends(
            RequestClientDepends[JWTAccessToken](
                allowed_roles=[RoleEnum.SUPER_ADMIN],
                action_type=ActionType.UPDATE_USER
            )
        )
):
    result: UserDtoGetResponse = UpdateUser(
        uow=UnitOfWork(bootstrap.database),
        dto_audit=request_client_dep.dto_audit
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
        request_client_dep: RequestClientDtoHandle = Depends(
            RequestClientDepends[JWTAccessToken](
                allowed_roles=[RoleEnum.SUPER_ADMIN, RoleEnum.DEFAULT_USER],
                action_type=ActionType.UPDATE_USER
            )
        )
):
    if request_client_dep.token_info.user_id != update_user_info.id:
        return JSONResponse(
            status_code=status.HTTP_403_FORBIDDEN,
            content='Id пользователя в токене не совпадает с id пользователя в теле запроса',
            media_type="application/json"
        )
    result: UserDtoGetResponse = UpdateUser(
        uow=UnitOfWork(bootstrap.database),
        dto_audit=request_client_dep.dto_audit
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