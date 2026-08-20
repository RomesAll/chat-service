from business_logic.unit_of_work import UnitOfWork
from business_logic.use_cases.interface.iuse_case import IUseCase
from dtos.keys import PrivateKeyDtoCreate
from repositories.user_keys import PrivateKeyRepository


class SavePrivateKeysUseCase(IUseCase):
    """Use case для сохранения приватных ключей пользователя"""
    def __init__(
            self,
            uow: UnitOfWork,
    ):
        self.uow = uow

    def execute(self, key_info: PrivateKeyDtoCreate):
        with self.uow as uow:
            repo: PrivateKeyRepository = uow.get_repository(PrivateKeyRepository)
            repo.save(key_info)
