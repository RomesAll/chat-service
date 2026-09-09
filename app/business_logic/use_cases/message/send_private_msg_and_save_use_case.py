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
from app.shared.log_config import LogMixin
from business_logic.decorators import audit_system
from dtos import AuditPostDto


class SendPrivateMsgAndSave(IUseCase, LogMixin):
    """Use case для отправки сообщений другому пользователю"""
    def __init__(
            self,
            session_id: UUID,
            uow: UnitOfWork,
            private_msg_route: PrivateMessageRoute,
            file_manager: type[FileManager],
            dto_audit: AuditPostDto
    ):
        self.session_id = session_id
        self.uow = uow
        self.private_msg_route = private_msg_route
        self.file_manager=file_manager
        self.dto_audit = dto_audit

    @audit_system
    async def execute(
            self,
            dto_private_msg: PrivateMessageDtoPostRequest,
            upload_file: list[UploadFile] | None = None,
    ) -> MessageDtoGetResponse:
        with self.uow as uow:
            private_msg_repo = uow.get_repository(PrivateMessageRepository)
            file_msg_repo = uow.get_repository(MessageAttachmentsRepository)
            dto_response = private_msg_repo.save(dto_private_msg)
            self.log_debug(f'Сообщение сохранено, id {dto_response.id}')
            if upload_file:
                for dto_file in self.file_manager.upload_file(upload_file, dto_response):
                    file_msg_repo.save(dto_file)
                    self.log_debug(f'Файл успешно сохранен {dto_file}')
            await self.private_msg_route.send_message(self.session_id, dto_response)
            return dto_response