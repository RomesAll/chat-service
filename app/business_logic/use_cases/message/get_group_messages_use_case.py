from uuid import UUID
from app.business_logic.decorators import audit_system
from app.business_logic.unit_of_work import UnitOfWork
from app.business_logic.use_cases.interface.iuse_case import IUseCase
from app.data_access.database.repositories import MessageAttachmentsRepository
from app.data_access.database.repositories.message import GroupMessageRepository
from app.shared.dtos import GroupMessageDtoResponse, AuditPostDto
from app.data_access.database.repositories.room import UserInRoomRepository
from app.business_logic.exceptions import UserNotFoundInRoom
from app.shared.log_config import LogMixin


class GetGroupMsg(IUseCase, LogMixin):
    """Use case для получения сообщений с пользователем"""
    def __init__(
            self,
            uow: UnitOfWork,
            dto_audit: AuditPostDto
    ):
        self.uow = uow
        self.dto_audit = dto_audit

    @audit_system
    def execute(
            self,
            room_id: UUID,
            user_id: str
    ) -> list[GroupMessageDtoResponse]:
        with self.uow as uow:
            group_msg_repo = uow.get_repository(GroupMessageRepository)
            user_in_room_repo = uow.get_repository(UserInRoomRepository)
            msg_file_repo = uow.get_repository(MessageAttachmentsRepository)
            if not user_in_room_repo.check_exist_user_in_room(user_id, room_id):
                exc = UserNotFoundInRoom(user_id, room_id)
                self.log_error(exc.message)
                raise exc
            messages = group_msg_repo.get_message_by_room(room_id)
            for msg in messages:
                msg_file = msg_file_repo.get_message_id_files(msg.id)
                msg.file_id = list(msg_file)
            self.log_debug(f'Получена информация о сообщениях в комнате {room_id} для пользователя {user_id}')
            return messages