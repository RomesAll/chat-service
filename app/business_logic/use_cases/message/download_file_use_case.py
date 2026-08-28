from uuid import UUID
from starlette.responses import StreamingResponse
from app.business_logic.exceptions import PermissionFileDownError
from app.business_logic.file_manager.file_manager import FileManager
from app.business_logic.unit_of_work import UnitOfWork
from app.business_logic.use_cases.interface.iuse_case import IUseCase
from app.data_access.database.repositories.message import PrivateMessageRepository
from app.data_access.database.repositories.message_attachments import MessageAttachmentsRepository


class DownloadFileUseCase(IUseCase):
    """Use case для загрузки файла с сервера"""
    def __init__(
            self,
            uow: UnitOfWork,
            file_manager: type[FileManager]
    ):
        self.uow = uow
        self.file_manager = file_manager

    async def execute(self, user_upload_id: str, file_id: UUID) -> StreamingResponse:
        with self.uow as uow:
            file_repo = uow.get_repository(MessageAttachmentsRepository)
            message_repo = uow.get_repository(PrivateMessageRepository)
            file_meta = file_repo.get_by_id(file_id)
            message_info = message_repo.get_by_id(file_meta.message_id)
            if user_upload_id not in [message_info.sender_id, message_info.recipient_id]:
                raise PermissionFileDownError(user_upload_id, file_id)
            return StreamingResponse(
                self.file_manager.read_file(file_meta.file_path),
                media_type=file_meta.mime_type,
                headers={
                    "Content-Disposition": f"attachment; filename={file_meta.file_name}"
                }
            )