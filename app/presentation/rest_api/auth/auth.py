from fastapi import APIRouter, Response, status, Depends
from starlette.responses import JSONResponse
from bootstrap import get_bootstrap
from app.business_logic.auth.jwt_manager import JWTFacade
from app.business_logic.auth.password_manager import PasswordManager
from app.business_logic.exceptions import CheckPswError
from app.business_logic.unit_of_work import UnitOfWork
from app.business_logic.use_cases.auth.login_use_case import LoginUseCase
from app.shared.dtos import UserDtoPostRequest
from app.shared.dtos.auth import LoginDtoRequest
from app.business_logic.use_cases.auth.logout_use_case import LogoutUseCase
from app.business_logic.use_cases.auth.refresh_token_use_case import RefreshTokenUseCase
from app.business_logic.use_cases.user.register_user_use_case import RegisterUser
from app.shared.dtos import JWTRefreshTokenResponse, JWTTokenResponse
from app.shared.dtos.auth import LoginOrRegisterDtoResponse
from app.data_access.database.models.user import RoleEnum
from app.presentation.dependencies.auth import RoleChecker

route = APIRouter()
bootstrap = get_bootstrap()

@route.post(
    path='/auth/login',
    tags=['Auth'],
    summary='Вход с систему',
    operation_id="login_user_operation",
)
def login_user(credentials: LoginDtoRequest):
    try:
        result: LoginOrRegisterDtoResponse = LoginUseCase(
            uow=UnitOfWork(bootstrap.database),
            jwt_manager=JWTFacade,
            psw_manager=PasswordManager,
            jwt_white_list=bootstrap.jwt_white_list
        ).execute(credentials)
        return JSONResponse(
            status_code=status.HTTP_200_OK,
            content=result.model_dump(mode='json'),
            media_type="application/json"
        )
    except CheckPswError:
        return Response(
            status_code=status.HTTP_400_BAD_REQUEST,
            content='Неверный логин или пароль',
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
        uow=UnitOfWork(bootstrap.database),
        jwt_manager=JWTFacade,
        psw_manager=PasswordManager,
        jwt_white_list=bootstrap.jwt_white_list
    ).execute(new_user)
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
    path='/auth/tokens/refresh',
    tags=['Auth'],
    summary='Обновление токенов',
    description='Обновление access и refresh токенов',
    operation_id="refresh_tokens_operation",
)
def refresh_tokens(
    refresh_token: JWTRefreshTokenResponse = Depends(RoleChecker([RoleEnum.DEFAULT_USER, RoleEnum.SUPER_ADMIN]))
):
    result: JWTTokenResponse = RefreshTokenUseCase(
        jwt_facade=JWTFacade,
        jwt_white_list=bootstrap.jwt_white_list
    ).execute(refresh_token)
    return JSONResponse(
        status_code=status.HTTP_201_CREATED,
        content=result.model_dump(mode='json'),
        media_type="application/json"
    )


@route.post(
    path='/auth/logout',
    tags=['Auth'],
    summary='Выход из системы',
    description='Выход из системы, удаляет сессионный ключ и id refresh токена из white list',
    operation_id="logout_user_operation",
)
def logout_user_operation(
    refresh_token: JWTRefreshTokenResponse = Depends(RoleChecker([RoleEnum.DEFAULT_USER, RoleEnum.SUPER_ADMIN]))
):
    is_delete_refresh, is_delete_session_key = LogoutUseCase(
        session_key_storage=bootstrap.session_key_storage,
        active_session_manager=bootstrap.active_session_manager,
        white_list=bootstrap.jwt_white_list
    ).execute(
        user_id=refresh_token.user_id,
        session_id=refresh_token.session_id,
        refresh_token_id=refresh_token.refresh_id
    )
    return Response(
        status_code=status.HTTP_200_OK,
        content=f'Выход из системы, удаление refresh_token: {is_delete_refresh if is_delete_refresh else 'уже удален'}, '
                f'удаление session_key: {is_delete_session_key if is_delete_session_key else 'уже удален'} '
    )