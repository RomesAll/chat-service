from app.business_logic.unit_of_work import UnitOfWork
from app.business_logic.use_cases.interface.iuse_case import IUseCase
from app.shared.dtos.keys import PrivateKeyDtoCreate, PrivateKeyDtoGet
from app.data_access.database.repositories.user_keys import PrivateKeyRepository
from app.shared.log_config import LogMixin


class SavePrivateKeysUseCase(IUseCase, LogMixin):
    """Use case для сохранения приватных ключей пользователя"""
    def __init__(
            self,
            uow: UnitOfWork,
    ):
        self.uow = uow

    def execute(self, key_info: PrivateKeyDtoCreate) -> list[PrivateKeyDtoGet]:
        with self.uow as uow:
            repo: PrivateKeyRepository = uow.get_repository(PrivateKeyRepository)
            result = repo.save(key_info)
            self.log_debug(f'Зашифрованный приватный ключ успешно сохранен для пользователя {key_info.user_id}')
            return result
