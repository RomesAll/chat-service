from uuid import UUID
from app.business_logic.unit_of_work import UnitOfWork
from app.business_logic.use_cases.interface.iuse_case import IUseCase
from app.data_access.database.repositories.message import GroupMessageRepository
from app.shared.dtos import GroupMessageDtoResponse
from app.data_access.database.repositories.room import UserInRoomRepository
from business_logic.exceptions import UserNotFoundInRoom


class GetGroupMsg(IUseCase):
    """Use case для получения сообщений с пользователем"""
    def __init__(self, uow: UnitOfWork):
        self.uow = uow

    def execute(
            self,
            room_id: UUID,
            user_id: str
    ) -> list[GroupMessageDtoResponse]:
        with self.uow as uow:
            group_msg_repo = uow.get_repository(GroupMessageRepository)
            user_in_room_repo = uow.get_repository(UserInRoomRepository)
            if not user_in_room_repo.check_exist_user_in_room(user_id, room_id):
                raise UserNotFoundInRoom(user_id, room_id)
            return group_msg_repo.get_message_by_room(room_id)