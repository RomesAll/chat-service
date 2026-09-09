from uuid import UUID
from app.business_logic.unit_of_work import UnitOfWork
from app.business_logic.use_cases.interface.iuse_case import IUseCase
from app.shared.dtos import RoomDtoGetResponse
from app.data_access.database.repositories.room import RoomRepository, UserInRoomRepository
from app.shared.log_config import LogMixin
from business_logic.exceptions import UserNotFoundInRoom


class GetOneRoomUseCase(IUseCase, LogMixin):
    """Use case для получения информации о комнате"""
    def __init__(
            self,
            uow: UnitOfWork
    ):
        self.uow = uow

    def execute(self, room_id: UUID, user_id: str) -> RoomDtoGetResponse:
        room_repo = self.uow.get_repository(RoomRepository)
        user_in_room_repo = self.uow.get_repository(UserInRoomRepository)
        if not user_in_room_repo.check_exist_user_in_room(user_id, room_id):
            exc = UserNotFoundInRoom(user_id, room_id)
            self.log_error(exc.message)
            raise exc
        result = room_repo.get_by_id(room_id)
        self.log_debug(f'Получена информация о комнате {result.id}')
        return result