from app.business_logic.unit_of_work import UnitOfWork
from app.business_logic.use_cases.interface.iuse_case import IUseCase
from app.shared.dtos import UserDtoGetResponse
from app.data_access.database.repositories import UserRepository
from app.shared.log_config import LogMixin


class RecoveryUser(IUseCase, LogMixin):
    """Use case для восстановления пользователей"""
    def __init__(
            self,
            uow: UnitOfWork
    ):
        self.uow = uow

    def execute(self, user_id: str) -> UserDtoGetResponse:
        with self.uow as uow:
            repo = uow.get_repository(UserRepository)
            result = repo.recovery(user_id)
            self.log_info(f'Пользователь {user_id} восстановлен')
            return result