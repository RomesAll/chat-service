from fastapi import APIRouter, Response, status, Depends
from starlette.responses import JSONResponse
from bootstrap import get_bootstrap
from app.business_logic.unit_of_work import UnitOfWork
from app.business_logic.use_cases.user.hard_delete_user_use_case import HardDeleteUser
from app.business_logic.use_cases.user.recovery_user_use_case import RecoveryUser
from app.business_logic.use_cases.user.soft_delete_user_use_case import SoftDeleteUser
from app.shared.dtos import UserDtoGetResponse, RequestClientDtoHandle, JWTAccessToken, ActionType
from app.data_access.database.models.user import RoleEnum
from app.presentation.dependencies.base import RequestClientDepends

route = APIRouter()
bootstrap = get_bootstrap()


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
        request_client_dep: RequestClientDtoHandle = Depends(
            RequestClientDepends[JWTAccessToken](
                allowed_roles=[RoleEnum.SUPER_ADMIN],
                action_type=ActionType.SOFT_DELETE_USER
            )
        )
):
    result: str = SoftDeleteUser(
        uow=UnitOfWork(bootstrap.database),
        dto_audit=request_client_dep.dto_audit
    ).execute(user_id)
    return JSONResponse(
        status_code=status.HTTP_200_OK,
        content=f'Пользователь с id {result} теперь неактивен'
    )


@route.patch(
    path='/users/me/soft-delete',
    tags=['Users'],
    summary='Мягкое удаление своей информации по токену',
    description='Мягкое удаление своей информации по токену возможность восстановления',
    response_model_exclude_unset=True,
    response_model=UserDtoGetResponse,
    operation_id="soft_delete_me_operation",
)
def soft_delete_me(
        request_client_dep: RequestClientDtoHandle = Depends(
            RequestClientDepends[JWTAccessToken](
                allowed_roles=[RoleEnum.SUPER_ADMIN, RoleEnum.DEFAULT_USER],
                action_type=ActionType.SOFT_DELETE_USER
            )
        )
):
    result: str = SoftDeleteUser(
        uow=UnitOfWork(bootstrap.database),
        dto_audit=request_client_dep.dto_audit
    ).execute(request_client_dep.token_info.user_id)
    return JSONResponse(
        status_code=status.HTTP_200_OK,
        content=f'Пользователь с id {result} теперь неактивен'
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
        request_client_dep: RequestClientDtoHandle = Depends(
            RequestClientDepends[JWTAccessToken](
                allowed_roles=[RoleEnum.SUPER_ADMIN],
                action_type=ActionType.HARD_DELETE_USER
            )
        )
):
    result: str = HardDeleteUser(
        uow=UnitOfWork(bootstrap.database),
        dto_audit=request_client_dep.dto_audit
    ).execute(user_id)
    return JSONResponse(
        status_code=status.HTTP_200_OK,
        content=f'Пользователь с id {result} теперь удален'
    )


@route.delete(
    path='/users/me/hard-delete',
    tags=['Users'],
    summary='Жесткое удаление своей информации',
    description='Жесткое удаление своей информации без возможности восстановления',
    operation_id="hard_delete_me_operation",
)
def hard_delete_me(
        request_client_dep: RequestClientDtoHandle = Depends(
            RequestClientDepends[JWTAccessToken](
                allowed_roles=[RoleEnum.SUPER_ADMIN, RoleEnum.DEFAULT_USER],
                action_type=ActionType.HARD_DELETE_USER
            )
        )
):
    result: str = HardDeleteUser(
        uow=UnitOfWork(bootstrap.database),
        dto_audit=request_client_dep.dto_audit
    ).execute(request_client_dep.token_info.user_id)
    return JSONResponse(
        status_code=status.HTTP_200_OK,
        content=f'Пользователь с id {result} теперь удален'
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
        request_client_dep: RequestClientDtoHandle = Depends(
            RequestClientDepends[JWTAccessToken](
                allowed_roles=[RoleEnum.SUPER_ADMIN],
                action_type=ActionType.RECOVERY_USER
            )
        )
):
    result: UserDtoGetResponse = RecoveryUser(
        uow=UnitOfWork(bootstrap.database),
        dto_audit=request_client_dep.dto_audit
    ).execute(user_id)
    if not return_record:
        return Response(
            status_code=status.HTTP_204_NO_CONTENT
        )
    return JSONResponse(
        status_code=status.HTTP_201_CREATED,
        content=result.model_dump(mode='json'),
        media_type="application/json"
    )


@route.post(
    path='/users/me/recovery',
    tags=['Users'],
    summary='Восстановление пользователя',
    description='Восстановление пользователя после мягкого удаления',
    operation_id="recovery_me_operation",
)
def recovery_me(
        return_record: bool = True,
        request_client_dep: RequestClientDtoHandle = Depends(
            RequestClientDepends[JWTAccessToken](
                allowed_roles=[RoleEnum.SUPER_ADMIN, RoleEnum.DEFAULT_USER],
                action_type=ActionType.RECOVERY_USER
            )
        )
):
    result: UserDtoGetResponse = RecoveryUser(
        uow=UnitOfWork(bootstrap.database),
        dto_audit=request_client_dep.dto_audit
    ).execute(request_client_dep.token_info.user_id)
    if not return_record:
        return Response(
            status_code=status.HTTP_204_NO_CONTENT
        )
    return JSONResponse(
        status_code=status.HTTP_200_OK,
        content={
            'message': result.model_dump(mode='json')
        },
        media_type="application/json"
    )
