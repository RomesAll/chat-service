from app.business_logic.unit_of_work import UnitOfWork
from app.business_logic.use_cases.interface.iuse_case import IUseCase
from app.data_access.database.repositories import UserRepository
from app.shared.log_config import LogMixin
from business_logic.decorators import audit_system
from dtos import AuditPostDto


class SoftDeleteUser(IUseCase, LogMixin):
    """Use case для мягкого удаления пользователей"""
    def __init__(
            self,
            uow: UnitOfWork,
            dto_audit: AuditPostDto
    ):
        self.uow = uow
        self.dto_audit = dto_audit

    @audit_system
    def execute(self, user_id: str):
        with self.uow as uow:
            repo = uow.get_repository(UserRepository)
            result = repo.soft_delete(user_id)
            self.log_info(f'Пользователь {user_id} удален (soft delete)')
            return result