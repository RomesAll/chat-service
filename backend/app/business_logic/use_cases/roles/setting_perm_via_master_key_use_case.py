from pydantic import SecretStr
from app.business_logic.auth import PasswordManager
from app.business_logic.decorators import audit_system
from app.business_logic.exceptions import CheckMasterPswError
from app.business_logic.unit_of_work import UnitOfWork
from app.business_logic.use_cases.interface.iuse_case import IUseCase
from app.data_access.database.models.user import RoleEnum
from app.data_access.database.repositories import UserRepository
from app.data_access.exceptions import RecordNotFound
from app.shared.dtos import UserDtoGetResponse, AuditPostDto
from bootstrap import get_bootstrap


class SettingPermViaMasterKeyUseCase(IUseCase):
    """Use case для добавления установки роли для пользователя по мастер ключу"""
    def __init__(
            self,
            uow: UnitOfWork,
            psw_manager: type[PasswordManager],
            dto_audit: AuditPostDto
    ):
        self.uow = uow
        self.psw_manager = psw_manager
        self.dto_audit = dto_audit

    @audit_system
    def execute(self, user_id: str, role: RoleEnum, psw: SecretStr) -> UserDtoGetResponse:
        with self.uow as uow:
            if not self.psw_manager.check_equal_psw(
                    password=psw,
                    hashed_password=get_bootstrap().config.app_master_key
            ):
                raise CheckMasterPswError()
            repo = uow.get_repository(UserRepository)
            if not repo.check_exist(user_id):
                raise RecordNotFound(user_id)
            user = repo.update_role(user_id, role)
            return user