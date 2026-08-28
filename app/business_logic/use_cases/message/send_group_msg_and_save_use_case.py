from uuid import UUID, uuid4
from starlette.datastructures import UploadFile
from app.business_logic.active_session.message_sender.group_message import GroupMessageRoute
from app.business_logic.file_manager.file_manager import FileManager
from app.business_logic.unit_of_work import UnitOfWork
from app.business_logic.use_cases.interface.iuse_case import IUseCase
from app.shared.dtos import GroupMessageDtoPostRequest, GroupMessageDtoResponse, MessageAttachmentsDtoPostRequest
from app.data_access.database.models.message_attachments import MimeType
from app.data_access.database.repositories.message import GroupMessageRepository
from app.data_access.database.repositories.message_attachments import MessageAttachmentsRepository
from app.data_access.database.repositories.room import RoomRepository, UserInRoomRepository
from bootstrap import get_bootstrap

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
                    dto_group_msg.room_id
            ):
                raise Exception
            if not user_in_room_repo.check_exist_user_in_room(
                    dto_group_msg.sender_id,
                    dto_group_msg.room_id
            ):
                raise Exception
            dto_response = group_msg_repo.save(dto_group_msg)
            if upload_file:
                for file in upload_file:
                    if not file.filename or not file.size:
                        continue
                    file_id = uuid4()
                    file_path=get_bootstrap().config.upload_file_path
                    dto_file = MessageAttachmentsDtoPostRequest(
                        id=file_id,
                        file_name=file.filename,
                        file_path=file_path,
                        file_size=file.size,
                        message_id=dto_response.id,
                        mime_type=MimeType(file.content_type)
                    )
                    file_msg_repo.save(dto_file)
                    await self.file_manager.write_file(
                        path_to_save=file_path,
                        file=file
                    )
                    dto_response.file_id.append(file_id)
            await self.group_msg_route.send_message(self.session_id, dto_response)
            return dto_response