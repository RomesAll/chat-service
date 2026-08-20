from fastapi import APIRouter, Response, status, Depends
from starlette.responses import JSONResponse
from business_logic.unit_of_work import UnitOfWork
from business_logic.use_cases.user.hard_delete_user import HardDeleteUser
from business_logic.use_cases.user.recovery_user import RecoveryUser
from business_logic.use_cases.user.soft_delete_user import SoftDeleteUser
from database import db
from dtos import (
    UserDtoGetResponse,
    JWTRefreshTokenResponse
)
from models.user import RoleEnum
from presentation.dependencies.auth import RoleChecker

route = APIRouter()


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
        access_token: JWTRefreshTokenResponse = Depends(RoleChecker([RoleEnum.SUPER_ADMIN]))
):
    result: str = SoftDeleteUser(
        uow=UnitOfWork(db)
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
        access_token: JWTRefreshTokenResponse = Depends(RoleChecker([RoleEnum.DEFAULT_USER, RoleEnum.SUPER_ADMIN]))
):
    result: str = SoftDeleteUser(
        uow=UnitOfWork(db)
    ).execute(access_token.user_id)
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
        access_token: JWTRefreshTokenResponse = Depends(RoleChecker([RoleEnum.SUPER_ADMIN]))
):
    result: str = HardDeleteUser(
        uow=UnitOfWork(db)
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
        access_token: JWTRefreshTokenResponse = Depends(RoleChecker([RoleEnum.SUPER_ADMIN]))
):
    result: str = HardDeleteUser(
        uow=UnitOfWork(db)
    ).execute(access_token.user_id)
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
        access_token: JWTRefreshTokenResponse = Depends(RoleChecker([RoleEnum.SUPER_ADMIN]))
):
    result: UserDtoGetResponse = RecoveryUser(
        uow=UnitOfWork(db)
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
        access_token: JWTRefreshTokenResponse = Depends(RoleChecker([RoleEnum.SUPER_ADMIN]))
):
    result: UserDtoGetResponse = RecoveryUser(
        uow=UnitOfWork(db)
    ).execute(access_token.user_id)
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
