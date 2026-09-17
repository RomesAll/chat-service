from fastapi import APIRouter, Depends, status
from pydantic import SecretStr
from starlette.responses import JSONResponse
from app.business_logic.auth import PasswordManager
from app.business_logic.unit_of_work import UnitOfWork
from app.data_access.database.models.user import RoleEnum
from app.presentation.dependencies import RequestClientDepends
from app.shared.dtos import RequestClientDtoHandle, ActionType
from app.shared.dtos.jwt import TokenType, JWTRefreshTokenResponse
from bootstrap import get_bootstrap
from app.business_logic.use_cases import GrantRightsUseCase

route = APIRouter()
bootstrap = get_bootstrap()


@route.post(
    path='/auth/{user_id}/roles/grand-rights',
    tags=['Auth'],
    summary='Изменение роли для пользователя',
    operation_id="grand_rights_operation",
)
def grand_rights(
        user_id: str,
        role: RoleEnum,
        request_client_dep: RequestClientDtoHandle = Depends(
            RequestClientDepends[JWTRefreshTokenResponse](
                token_type=TokenType.REFRESH_TOKEN,
                allowed_roles=[RoleEnum.SUPER_ADMIN],
                action_type=ActionType.GRAND_RIGHTS
            ),
        )
):
    GrantRightsUseCase(
        uow=UnitOfWork(bootstrap.database),
        dto_audit=request_client_dep.dto_audit,
        session_key_storage=bootstrap.redis_cache.session_key_storage,
        active_session_manager=bootstrap.active_session_manager,
        white_list=bootstrap.redis_cache.jwt_white_list,
        psw_manager=PasswordManager
    ).execute(
        user_id=user_id,
        role=role,
        session_id=request_client_dep.token_info.session_id,
        refresh_token_id=request_client_dep.token_info.refresh_id,
    )
    return JSONResponse(
        status_code=status.HTTP_201_CREATED,
        content={
             'message': f'Роль успешна изменена на {role.value} для {user_id}',
        }
    )


@route.post(
    path='/auth/{user_id}/roles/grand-rights/master-key',
    tags=['Auth'],
    summary='Изменение роли для пользователя по мастер ключу',
    operation_id="grand_rights_master_key_operation",
)
def grand_rights_via_master_key(
        user_id: str,
        role: RoleEnum,
        master_psw: str,
        request_client_dep: RequestClientDtoHandle = Depends(
            RequestClientDepends[JWTRefreshTokenResponse](
                token_type=TokenType.REFRESH_TOKEN,
                allowed_roles=[RoleEnum.SUPER_ADMIN, RoleEnum.DEFAULT_USER],
                action_type=ActionType.GRAND_RIGHTS_MASTER_KEY
            ),
        )
):
    GrantRightsUseCase(
        uow=UnitOfWork(bootstrap.database),
        dto_audit=request_client_dep.dto_audit,
        session_key_storage=bootstrap.redis_cache.session_key_storage,
        active_session_manager=bootstrap.active_session_manager,
        white_list=bootstrap.redis_cache.jwt_white_list,
        psw_manager=PasswordManager
    ).execute(
        user_id=user_id,
        role=role,
        session_id=request_client_dep.token_info.session_id,
        refresh_token_id=request_client_dep.token_info.refresh_id,
        master_psw=SecretStr(master_psw)
    )
    return JSONResponse(
        status_code=status.HTTP_201_CREATED,
        content={
            'message': f'Роль успешна изменена на {role.value} для {user_id} по мастер ключу',
        }
    )