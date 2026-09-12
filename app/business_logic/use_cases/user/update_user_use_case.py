from app.business_logic.unit_of_work import UnitOfWork
from app.business_logic.use_cases.interface.iuse_case import IUseCase
from app.shared.dtos import UserDtoGetResponse, UserDtoUpdateRequest, AuditPostDto
from app.data_access.database.repositories import UserRepository
from app.shared.log_config import LogMixin
from app.business_logic.decorators import audit_system


class UpdateUser(IUseCase, LogMixin):
    """Use case для обновления пользователей"""
    def __init__(
            self,
            uow: UnitOfWork,
            dto_audit: AuditPostDto
    ):
        self.uow = uow
        self.dto_audit = dto_audit

    @audit_system
    def execute(self, user_id: str, dto_user: UserDtoUpdateRequest) -> UserDtoGetResponse:
        with self.uow as uow:
            repo = uow.get_repository(UserRepository)
            result = repo.update(user_id, dto_user)
            self.log_debug(f'Информация о пользователе {user_id} успешно обновлена')
            return result