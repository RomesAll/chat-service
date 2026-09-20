from app.business_logic.unit_of_work import UnitOfWork
from app.business_logic.use_cases.interface.iuse_case import IUseCase
from app.data_access.database.repositories import UserRepository
from app.shared.dtos import BaseDtoGetListRequest, UserDtoGetResponse, AuditPostDto
from app.shared.log_config import LogMixin
from app.business_logic.decorators import audit_system


class GetUsers(IUseCase, LogMixin):
    """Use case для получения всех пользователей"""
    def __init__(
            self,
            uow: UnitOfWork,
            dto_audit: AuditPostDto
    ):
        self.uow = uow
        self.dto_audit = dto_audit

    @audit_system
    def execute(self, dto_user: BaseDtoGetListRequest) -> list[UserDtoGetResponse]:
        with self.uow as uow:
            group_msg_repo = uow.get_repository(UserRepository)
            dto_response = group_msg_repo.get(dto_user)
            self.log_debug(f'Получена информация о пользователях')
            return dto_response