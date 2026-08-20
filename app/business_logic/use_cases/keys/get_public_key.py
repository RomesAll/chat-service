from business_logic.unit_of_work import UnitOfWork
from business_logic.use_cases.interface.iuse_case import IUseCase
from dtos.keys import PublicKeyDtoGet
from repositories.user_keys import PublicKeyRepository


class GetPublicKeyUseCase(IUseCase):
    """Use case для получения публичного ключа пользователя"""
    def __init__(
            self,
            uow: UnitOfWork,
    ):
        self.uow = uow

    def execute(self, user_id: str) -> PublicKeyDtoGet:
        with self.uow as uow:
            repo: PublicKeyRepository = uow.get_repository(PublicKeyRepository)
            return repo.get_by_id(user_id)