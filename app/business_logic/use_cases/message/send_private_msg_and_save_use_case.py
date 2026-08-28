from uuid import UUID, uuid4
from starlette.datastructures import UploadFile
from app.business_logic.active_session.message_sender.private_message import PrivateMessageRoute
from app.business_logic.file_manager.file_manager import FileManager
from app.business_logic.unit_of_work import UnitOfWork
from app.business_logic.use_cases.interface.iuse_case import IUseCase
from app.shared.dtos import MessageAttachmentsDtoPostRequest
from app.data_access.database.models.message_attachments import MimeType
from app.data_access.database.repositories.message import PrivateMessageRepository
from app.shared.dtos import PrivateMessageDtoPostRequest, MessageDtoGetResponse
from app.data_access.database.repositories.message_attachments import MessageAttachmentsRepository
from bootstrap import get_bootstrap


class SendPrivateMsgAndSave(IUseCase):
    """Use case для отправки сообщений другому пользователю"""
    def __init__(
            self,
            session_id: UUID,
            uow: UnitOfWork,
            private_msg_route: PrivateMessageRoute,
            file_manager: type[FileManager]
    ):
        self.session_id = session_id
        self.uow = uow
        self.private_msg_route = private_msg_route
        self.file_manager=file_manager

    async def execute(
            self,
            dto_private_msg: PrivateMessageDtoPostRequest,
            upload_file: list[UploadFile] | None = None
    ) -> MessageDtoGetResponse:
        with self.uow as uow:
            private_msg_repo = uow.get_repository(PrivateMessageRepository)
            file_msg_repo = uow.get_repository(MessageAttachmentsRepository)
            dto_response = private_msg_repo.save(dto_private_msg)
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
            await self.private_msg_route.send_message(self.session_id, dto_response)
            return dto_response