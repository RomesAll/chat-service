from app.business_logic.unit_of_work import UnitOfWork
from app.business_logic.use_cases.interface.iuse_case import IUseCase
from app.shared.dtos.keys import PublicKeyDtoGet
from app.data_access.database.repositories.user_keys import PublicKeyRepository
from app.shared.log_config import LogMixin
from business_logic.decorators import audit_system
from app.shared.dtos import AuditPostDto


class GetPublicKeyUseCase(IUseCase, LogMixin):
    """Use case для получения публичного ключа пользователя"""
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
            user_id: str,
    ) -> PublicKeyDtoGet:
        with self.uow as uow:
            repo: PublicKeyRepository = uow.get_repository(PublicKeyRepository)
            result = repo.get_by_id(user_id)
            self.log_debug(f'Получена информация о публичном ключе пользователя {user_id}')
            return result