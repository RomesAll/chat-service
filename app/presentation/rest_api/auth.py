from fastapi import APIRouter, Response, status
from business_logic.auth.jwt_manager import JWTFacade
from business_logic.auth.password_manager import PasswordManager
from business_logic.unit_of_work import UnitOfWork
from business_logic.use_cases.auth.login_use_case import LoginUseCase
from app.shared.dtos import UserDtoPostRequest
from app.shared.dtos.auth import LoginDtoRequest
from business_logic.use_cases.auth.refresh_token_use_case import RefreshTokenUseCase
from business_logic.use_cases.auth.register_user import RegisterUser
from database import db
from dtos import JWTRefreshTokenResponse
from dtos.auth import LoginOrRegisterDtoResponse

route = APIRouter()


@route.post(
    path='/auth/login',
    tags=['Auth'],
    summary='Вход с систему',
    operation_id="login_user_operation",
)
def login_user(credentials: LoginDtoRequest):
    result: LoginOrRegisterDtoResponse = LoginUseCase(
        uow=UnitOfWork(db),
        jwt_manager=JWTFacade,
        psw_manager=PasswordManager
    ).execute(credentials)
    return Response(
        status_code=status.HTTP_201_CREATED,
        content=result.model_dump_json(exclude_none=True),
        media_type="application/json"
    )


@route.post(
    path='/auth/register',
    tags=['Auth'],
    summary='Регистрация пользователя',
    description='Добавление нового пользователя в систему',
    operation_id="register_user_operation",
)
def register_user(new_user: UserDtoPostRequest, return_record: bool = True):
    result: LoginOrRegisterDtoResponse = RegisterUser(
        uow=UnitOfWork(db),
        jwt_manager=JWTFacade,
        psw_manager=PasswordManager
    ).execute(new_user)
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
    path='/auth/refresh',
    tags=['Auth'],
    summary='Обновление токенов',
    description='Обновление access и refresh токенов',
    operation_id="refresh_tokens_operation",
)
def refresh_tokens(refresh_token: str):
    result: JWTRefreshTokenResponse = RefreshTokenUseCase(
        jwt_manager=JWTFacade
    ).execute(refresh_token)
    return Response(
        status_code=status.HTTP_201_CREATED,
        content=result.model_dump_json(exclude_none=True),
        media_type="application/json"
    )