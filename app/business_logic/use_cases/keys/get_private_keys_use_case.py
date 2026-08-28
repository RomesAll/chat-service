from app.business_logic.unit_of_work import UnitOfWork
from app.business_logic.use_cases.interface.iuse_case import IUseCase
from app.shared.dtos.keys import PrivateKeyDtoGet
from app.data_access.database.repositories.user_keys import PrivateKeyRepository


class GetPrivateKeysUseCase(IUseCase):
    """Use case для получения приватных ключей пользователя"""
    def __init__(
            self,
            uow: UnitOfWork,
    ):
        self.uow = uow

    def execute(self, user_id: str) -> list[PrivateKeyDtoGet]:
        with self.uow as uow:
            repo: PrivateKeyRepository = uow.get_repository(PrivateKeyRepository)
            return repo.get_by_id(user_id)
