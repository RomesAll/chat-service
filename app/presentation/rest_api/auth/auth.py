from fastapi import APIRouter, Response, status, Depends
from starlette.responses import JSONResponse
from bootstrap import get_bootstrap
from app.business_logic.auth import JWTFacade, PasswordManager
from app.business_logic.exceptions import CheckPswError, RefreshTokenInActive, RefreshTokenIdNotFound
from app.business_logic.unit_of_work import UnitOfWork
from app.data_access.database.models.user import RoleEnum
from app.presentation.dependencies.base import RequestClientDepends
from app.business_logic.use_cases import (
    LoginUseCase,
    LogoutUseCase,
    RefreshTokenUseCase,
    RegisterUser,
)
from app.shared.dtos import (
    UserDtoPostRequest,
    LoginDtoRequest,
    JWTRefreshTokenResponse,
    JWTTokenResponse,
    LoginOrRegisterDtoResponse,
    AuditPostDto,
    ActionType,
)
from dtos import RequestClientDtoHandle
from presentation.dependencies.audit import AuditDep


route = APIRouter()
bootstrap = get_bootstrap()


@route.post(
    path='/auth/login',
    tags=['Auth'],
    summary='Вход с систему',
    operation_id="login_user_operation",
)
def login_user(
        credentials: LoginDtoRequest,
        dto_audit: AuditPostDto = Depends(AuditDep(action=ActionType.LOGIN))
):
    try:
        dto_audit.user_id = credentials.user_id
        result: LoginOrRegisterDtoResponse = LoginUseCase(
            uow=UnitOfWork(bootstrap.database),
            jwt_manager=JWTFacade,
            psw_manager=PasswordManager,
            jwt_white_list=bootstrap.redis_cache.jwt_white_list,
            dto_audit=dto_audit
        ).execute(
            dto_request_data=credentials,
        )
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
def register_user(
        new_user: UserDtoPostRequest,
        dto_audit: AuditPostDto = Depends(AuditDep(action=ActionType.REGISTER)),
        return_record: bool = True
):
    dto_audit.user_id = new_user.id
    result: LoginOrRegisterDtoResponse = RegisterUser(
        uow=UnitOfWork(bootstrap.database),
        jwt_manager=JWTFacade,
        psw_manager=PasswordManager,
        jwt_white_list=bootstrap.redis_cache.jwt_white_list,
        dto_audit=dto_audit
    ).execute(
        dto_register_user=new_user,
    )
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
        request_client_dep: RequestClientDtoHandle = Depends(
            RequestClientDepends[JWTRefreshTokenResponse](
                allowed_roles=[RoleEnum.DEFAULT_USER, RoleEnum.SUPER_ADMIN],
                action_type=ActionType.REFRESH_TOKENS
            ),
        )
):
    try:
        result: JWTTokenResponse = RefreshTokenUseCase(
            jwt_facade=JWTFacade,
            jwt_white_list=bootstrap.redis_cache.jwt_white_list,
            dto_audit=request_client_dep.dto_audit
        ).execute(
            refresh_token=request_client_dep.token_info,
        )
        return JSONResponse(
            status_code=status.HTTP_201_CREATED,
            content=result.model_dump(mode='json'),
            media_type="application/json"
        )
    except RefreshTokenInActive:
        return Response(
            status_code=status.HTTP_401_UNAUTHORIZED,
            content='Токен не активен, пройдите аутентификацию заново'
        )
    except RefreshTokenIdNotFound:
        return Response(
            status_code=status.HTTP_401_UNAUTHORIZED,
            content='Токен недействителен, пройдите аутентификацию заново'
        )


@route.post(
    path='/auth/logout',
    tags=['Auth'],
    summary='Выход из системы',
    description='Выход из системы, удаляет сессионный ключ и id refresh токена из white list',
    operation_id="logout_user_operation",
)
def logout_user_operation(
        request_client_dep: RequestClientDtoHandle = Depends(
            RequestClientDepends[JWTRefreshTokenResponse](
                allowed_roles=[RoleEnum.DEFAULT_USER, RoleEnum.SUPER_ADMIN],
                action_type=ActionType.LOGOUT
            ),
        )
):
    is_delete_refresh, is_delete_session_key = LogoutUseCase(
        session_key_storage=bootstrap.redis_cache.session_key_storage,
        active_session_manager=bootstrap.active_session_manager,
        white_list=bootstrap.redis_cache.jwt_white_list,
        dto_audit=request_client_dep.dto_audit
    ).execute(
        user_id=request_client_dep.token_info.user_id,
        session_id=request_client_dep.token_info.session_id,
        refresh_token_id=request_client_dep.token_info.refresh_id,
    )
    return Response(
        status_code=status.HTTP_200_OK,
        content=f'Выход из системы, удаление refresh_token: {is_delete_refresh if is_delete_refresh else 'уже удален'}, '
                f'удаление session_key: {is_delete_session_key if is_delete_session_key else 'уже удален'} '
    )