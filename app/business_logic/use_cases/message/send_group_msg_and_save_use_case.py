from uuid import UUID
from starlette.datastructures import UploadFile
from app.business_logic.active_session.message_sender.group_message import GroupMessageRoute
from app.business_logic.file_manager.file_manager import FileManager
from app.business_logic.unit_of_work import UnitOfWork
from app.business_logic.use_cases.interface.iuse_case import IUseCase
from app.shared.dtos import GroupMessageDtoPostRequest, GroupMessageDtoResponse
from app.data_access.database.repositories.message import GroupMessageRepository
from app.data_access.database.repositories.message_attachments import MessageAttachmentsRepository
from app.data_access.database.repositories.room import RoomRepository, UserInRoomRepository
from business_logic.exceptions import UserNotFoundInRoom, RoomNotFound


class SendGroupMsgAndSave(IUseCase):
    """Use case для отправки сообщений в группу"""
    def __init__(
            self,
            session_id: UUID,
            uow: UnitOfWork,
            group_msg_route: GroupMessageRoute,
            file_manager: type[FileManager]
    ):
        self.session_id = session_id
        self.uow = uow
        self.group_msg_route = group_msg_route
        self.file_manager = file_manager

    async def execute(
            self,
            dto_group_msg: GroupMessageDtoPostRequest,
            upload_file: list[UploadFile] | None = None
    ) -> GroupMessageDtoResponse:
        with self.uow as uow:
            group_msg_repo = uow.get_repository(GroupMessageRepository)
            room_repo = uow.get_repository(RoomRepository)
            user_in_room_repo = uow.get_repository(UserInRoomRepository)
            file_msg_repo = uow.get_repository(MessageAttachmentsRepository)
            if not room_repo.check_exist(
                    record_id=dto_group_msg.room_id
            ):
                raise RoomNotFound(dto_group_msg.room_id)
            if not user_in_room_repo.check_exist_user_in_room(
                    user_id=dto_group_msg.sender_id,
                    room_id=dto_group_msg.room_id
            ):
                raise UserNotFoundInRoom(dto_group_msg.sender_id, dto_group_msg.room_id)
            dto_response = group_msg_repo.save(dto_group_msg)
            if upload_file:
                for dto_file in self.file_manager.upload_file(upload_file, dto_response):
                    file_msg_repo.save(dto_file)
            await self.group_msg_route.send_message(self.session_id, dto_response)
            return dto_response