from business_logic.unit_of_work import UnitOfWork
from business_logic.use_cases.interface.iuse_case import IUseCase
from dtos.keys import PublicKeyDtoCreate
from repositories.user_keys import PublicKeyRepository


class SavePublicKeyUseCase(IUseCase):
    """Use case для сохранения публичного ключа пользователя"""
    def __init__(
            self,
            uow: UnitOfWork,
    ):
        self.uow = uow

    def execute(self, key_info: PublicKeyDtoCreate):
        with self.uow as uow:
            repo: PublicKeyRepository = uow.get_repository(PublicKeyRepository)
            repo.save(key_info)