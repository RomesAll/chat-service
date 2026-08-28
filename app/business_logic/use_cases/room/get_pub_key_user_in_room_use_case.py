from app.business_logic.unit_of_work import UnitOfWork
from app.business_logic.use_cases.interface.iuse_case import IUseCase
from app.shared.dtos.keys import PublicKeyDtoGet
from app.data_access.database.repositories.room import UserInRoomRepository
from app.data_access.database.repositories.user_keys import PublicKeyRepository


class GetPubKeyUserInRoomUseCase(IUseCase):
    """Use case для получения всех публичных ключей пользователей"""
    def __init__(
            self,
            uow: UnitOfWork,
    ):
        self.uow = uow

    def execute(self, room_id) -> dict[str, PublicKeyDtoGet]:
        with self.uow as uow:
            keys_repo = uow.get_repository(PublicKeyRepository)
            user_in_room_repo = uow.get_repository(UserInRoomRepository)
            users = user_in_room_repo.get_users_in_room(room_id=room_id)
            user_key_info = {}
            for user in users:
                key = keys_repo.get_by_id(user.user_id)
                user_key_info.update({user.user_id: key.model_dump(mode='json')})
            return user_key_info