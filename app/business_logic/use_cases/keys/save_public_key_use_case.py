from app.business_logic.unit_of_work import UnitOfWork
from app.business_logic.use_cases.interface.iuse_case import IUseCase
from app.shared.dtos.keys import PublicKeyDtoCreate
from app.data_access.database.repositories.user_keys import PublicKeyRepository
from app.shared.log_config import LogMixin
from business_logic.decorators import audit_system
from dtos import AuditPostDto


class SavePublicKeyUseCase(IUseCase, LogMixin):
    """Use case для сохранения публичного ключа пользователя"""
    def __init__(
            self,
            uow: UnitOfWork,
            dto_audit: AuditPostDto
    ):
        self.uow = uow
        self.dto_audit = dto_audit

    @audit_system
    def execute(
            self, *,
            key_info: PublicKeyDtoCreate,
    ):
        with self.uow as uow:
            repo: PublicKeyRepository = uow.get_repository(PublicKeyRepository)
            repo.save(key_info)
            self.log_debug(f'Публичный ключ успешно сохранен для пользователя {key_info.user_id}')