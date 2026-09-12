from app.business_logic.decorators import audit_system
from app.business_logic.unit_of_work import UnitOfWork
from app.business_logic.use_cases.interface.iuse_case import IUseCase
from app.data_access.database.models.user import RoleEnum
from app.data_access.database.repositories import UserRepository
from app.shared.dtos import UserDtoGetResponse, AuditPostDto


class GrantRightsUseCase(IUseCase):
    """Use case для изменения роли пользователя"""
    def __init__(
            self,
            uow: UnitOfWork,
            dto_audit: AuditPostDto
    ):
        self.uow = uow
        self.dto_audit = dto_audit

    @audit_system
    def execute(self, user_id: str, role: RoleEnum) -> UserDtoGetResponse:
        with self.uow as uow:
            repo = uow.get_repository(UserRepository)
            result = repo.update_role(user_id, role)
            return result