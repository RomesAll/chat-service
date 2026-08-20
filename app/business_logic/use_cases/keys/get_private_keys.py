from business_logic.unit_of_work import UnitOfWork
from business_logic.use_cases.interface.iuse_case import IUseCase
from dtos.keys import PrivateKeyDtoGet
from repositories.user_keys import PrivateKeyRepository


class GetPrivateKeysUseCase(IUseCase):
    """Use case для получения приватных ключей пользователя"""
    def __init__(
            self,
            uow: UnitOfWork,
    ):
        self.uow = uow

    def execute(self, user_id: str) -> PrivateKeyDtoGet:
        with self.uow as uow:
            repo: PrivateKeyRepository = uow.get_repository(PrivateKeyRepository)
            return repo.get_by_id(user_id)
