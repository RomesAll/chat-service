from fastapi import APIRouter, Depends, status
from pydantic import SecretStr
from starlette.responses import JSONResponse
from app.business_logic.auth import PasswordManager
from app.business_logic.unit_of_work import UnitOfWork
from app.data_access.database.models.user import RoleEnum
from app.presentation.dependencies import RequestClientDepends
from app.shared.dtos import RequestClientDtoHandle, JWTAccessToken, ActionType
from bootstrap import get_bootstrap
from app.business_logic.use_cases import SettingPermViaMasterKeyUseCase, GrantRightsUseCase

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
            RequestClientDepends[JWTAccessToken](
                allowed_roles=[RoleEnum.SUPER_ADMIN],
                action_type=ActionType.GRAND_RIGHTS
            ),
        )
):
    user_info = GrantRightsUseCase(
        uow=UnitOfWork(bootstrap.database),
        dto_audit=request_client_dep.dto_audit
    ).execute(
        user_id=user_id,
        role=role,
    )
    return JSONResponse(
        status_code=status.HTTP_201_CREATED,
        content=user_info.model_dump(mode='json')
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
        master_key: str,
        request_client_dep: RequestClientDtoHandle = Depends(
            RequestClientDepends[JWTAccessToken](
                allowed_roles=[RoleEnum.SUPER_ADMIN, RoleEnum.DEFAULT_USER],
                action_type=ActionType.GRAND_RIGHTS_MASTER_KEY
            ),
        )
):
    user_info = SettingPermViaMasterKeyUseCase(
        uow=UnitOfWork(bootstrap.database),
        psw_manager=PasswordManager,
        dto_audit=request_client_dep.dto_audit
    ).execute(
        user_id=user_id,
        role=role,
        psw=SecretStr(master_key)
    )
    return JSONResponse(
        status_code=status.HTTP_201_CREATED,
        content=user_info.model_dump(mode='json')
    )