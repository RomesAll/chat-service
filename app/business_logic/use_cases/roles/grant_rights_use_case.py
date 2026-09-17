from uuid import UUID

from pydantic import SecretStr

from app.business_logic.active_session import ActiveSessionManager
from app.business_logic.auth import PasswordManager
from app.business_logic.cache import JWTWhiteListCache, SessionKeyStorage
from app.business_logic.decorators import audit_system
from app.business_logic.exceptions import UserNotFoundError, CheckMasterPswError
from app.business_logic.unit_of_work import UnitOfWork
from app.business_logic.use_cases.interface.iuse_case import IUseCase
from app.data_access.database.models.user import RoleEnum
from app.data_access.database.repositories import UserRepository
from app.data_access.exceptions import RecordNotFound
from app.shared.dtos import UserDtoGetResponse, AuditPostDto
from app.shared.log_config import LogMixin
from bootstrap import get_bootstrap


class GrantRightsUseCase(IUseCase, LogMixin):
    """Use case для изменения роли пользователя"""
    def __init__(
            self,
            uow: UnitOfWork,
            dto_audit: AuditPostDto,
            active_session_manager: ActiveSessionManager,
            white_list: JWTWhiteListCache,
            session_key_storage: SessionKeyStorage,
            psw_manager: type[PasswordManager],
    ):
        self.uow = uow
        self.dto_audit = dto_audit
        self.active_session_manager = active_session_manager
        self.white_list = white_list
        self.session_key_storage = session_key_storage
        self.psw_manager = psw_manager

    @audit_system
    def execute(
            self,
            user_id: str,
            role: RoleEnum,
            refresh_token_id: UUID,
            session_id: UUID,
            master_psw: SecretStr | None = None
    ) -> UserDtoGetResponse:
        with self.uow as uow:
            user_repo = uow.get_repository(UserRepository)
            if role == RoleEnum.DEFAULT_USER and master_psw:
                if not self.psw_manager.check_equal_psw(
                        password=master_psw,
                        hashed_password=get_bootstrap().config.app_master_key
                ):
                    raise CheckMasterPswError()
            elif not master_psw:
                raise CheckMasterPswError()
            if not user_repo.check_exist(user_id):
                raise RecordNotFound(user_id)
            result = user_repo.update_role(user_id, role)
            del self.white_list[user_id, refresh_token_id]
            self.log_info(f'id refresh ({refresh_token_id}) токена был успешно удален из '
                          f'white list для пользователя {user_id}')
            del self.session_key_storage[user_id, session_id]
            self.log_info(f'Сессионный ключ был успешно удален из кеша '
                          f'для пользователя {user_id} и session_id {session_id}')
            try:
                self.active_session_manager.remove_user_active_session(user_id, session_id)
            except UserNotFoundError:
                self.log_info(f'У пользователя {user_id} нет активных подключений')
            return result