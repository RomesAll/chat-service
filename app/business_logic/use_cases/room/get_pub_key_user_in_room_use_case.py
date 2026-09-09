from app.business_logic.unit_of_work import UnitOfWork
from app.business_logic.use_cases.interface.iuse_case import IUseCase
from app.shared.dtos.keys import PublicKeyDtoGet
from app.data_access.database.repositories.room import UserInRoomRepository
from app.data_access.database.repositories.user_keys import PublicKeyRepository
from app.shared.log_config import LogMixin
from business_logic.decorators import audit_system
from dtos import AuditPostDto


class GetPubKeyUserInRoomUseCase(IUseCase, LogMixin):
    """Use case для получения всех публичных ключей пользователей"""
    def __init__(
            self,
            uow: UnitOfWork,
            dto_audit: AuditPostDto
    ):
        self.uow = uow
        self.dto_audit = dto_audit

    @audit_system
    def execute(self, room_id) -> dict[str, PublicKeyDtoGet]:
        with self.uow as uow:
            keys_repo = uow.get_repository(PublicKeyRepository)
            user_in_room_repo = uow.get_repository(UserInRoomRepository)
            users = user_in_room_repo.get_users_in_room(room_id=room_id)
            user_key_info = {}
            for user in users:
                key = keys_repo.get_by_id(user.user_id)
                user_key_info.update({user.user_id: key.model_dump(mode='json')})
            self.log_debug(f'Получена информация о публичных ключах пользователей в комнате {room_id}')
            return user_key_info