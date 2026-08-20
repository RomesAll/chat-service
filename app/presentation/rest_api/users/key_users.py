from fastapi import APIRouter, status, Depends
from starlette.responses import JSONResponse
from business_logic.unit_of_work import UnitOfWork
from business_logic.use_cases.keys.get_public_key import GetPublicKeyUseCase
from database import db
from dtos import JWTAccessToken
from models.user import RoleEnum
from presentation.dependencies.auth import RoleChecker

route = APIRouter()


@route.get(
    path='/users/me/public-key',
    tags=['Users'],
    summary='Получение своего текущего публичного ключа',
    operation_id="get_my_public_key",
)
def get_my_public_key(
        access_token: JWTAccessToken = Depends(RoleChecker([RoleEnum.DEFAULT_USER, RoleEnum.SUPER_ADMIN]))
):
    result = GetPublicKeyUseCase(
        uow=UnitOfWork(db)
    ).execute(access_token.user_id)
    return JSONResponse(
        status_code=status.HTTP_200_OK,
        content=result.model_dump(mode='json'),
        media_type="application/json"
    )


@route.get(
    path='/users/{user_id}/public-key',
    tags=['Users'],
    summary='Получение публичного ключа пользователя',
    operation_id="get_user_public_key",
)
def get_user_public_key(
        user_id: str,
        access_token: JWTAccessToken = Depends(RoleChecker([RoleEnum.DEFAULT_USER, RoleEnum.SUPER_ADMIN]))
):
    result = GetPublicKeyUseCase(
        uow=UnitOfWork(db)
    ).execute(user_id)
    return JSONResponse(
        status_code=status.HTTP_200_OK,
        content=result.model_dump(mode='json'),
        media_type="application/json"
    )