from app.business_logic.unit_of_work import UnitOfWork
from app.business_logic.use_cases.interface.iuse_case import IUseCase
from app.shared.dtos.keys import PublicKeyDtoGet
from app.data_access.database.repositories.user_keys import PublicKeyRepository
from app.shared.log_config import LogMixin


class GetPublicKeyUseCase(IUseCase, LogMixin):
    """Use case для получения публичного ключа пользователя"""
    def __init__(
            self,
            uow: UnitOfWork,
    ):
        self.uow = uow

    def execute(self, user_id: str) -> PublicKeyDtoGet:
        with self.uow as uow:
            repo: PublicKeyRepository = uow.get_repository(PublicKeyRepository)
            result = repo.get_by_id(user_id)
            self.log_debug(f'Получена информация о публичном ключе пользователя {user_id}')
            return result