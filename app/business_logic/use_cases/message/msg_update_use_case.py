from app.business_logic.active_session import ActiveSessionManager
from app.business_logic.active_session.message_sender.interface import IMessageRoute
from app.business_logic.decorators import audit_system, audit_system_async
from app.business_logic.exceptions import MessageOwnerInCorrect, SendMessageError
from app.business_logic.file_manager import FileManager
from app.business_logic.unit_of_work import UnitOfWork
from app.business_logic.use_cases.interface.iuse_case import IUseCase
from app.data_access.database.repositories import MessageAttachmentsRepository, PrivateMessageRepository, \
    GroupMessageRepository
from app.data_access.database.repositories.base import BaseRepositoryUpdate
from app.data_access.exceptions import RecordNotFound
from app.shared.dtos import AuditPostDto, BaseDtoPutPathRequest, BaseDtoGetResponse
from uuid import UUID
from app.shared.log_config import LogMixin


class MsgUpdateUseCase(IUseCase, LogMixin):
    """Use case для обновления информации о приватном сообщении"""
    def __init__(
            self,
            session_id: UUID,
            uow: UnitOfWork,
            dto_audit: AuditPostDto,
            msg_route: IMessageRoute,
            file_manager: type[FileManager],
            repo: type[PrivateMessageRepository | GroupMessageRepository],
    ):
        self.session_id = session_id
        self.uow = uow
        self.dto_audit = dto_audit
        self.msg_route = msg_route
        self.file_manager = file_manager
        self.repo = repo

    @audit_system_async
    async def execute(
            self,
            sender_id: str,
            message_id: UUID,
            dto_request: BaseDtoPutPathRequest,
            file_ids: list[UUID] | None = None
    ) -> BaseDtoGetResponse:
        with self.uow as uow:
            msg_repo = uow.get_repository(self.repo)
            msg_file_repo = uow.get_repository(MessageAttachmentsRepository)
            msg_info = msg_repo.get_by_id(message_id)
            if msg_info.sender_id != sender_id:
                exc = MessageOwnerInCorrect(message_id, sender_id)
                self.log_error(exc.message)
                raise exc
            updated_msg = msg_repo.update(message_id, dto_request)
            self.log_debug(f'Сообщение {message_id} было обновлено')
            if file_ids:
                for file_id in file_ids:
                    try:
                        record_id = msg_file_repo.hard_delete(file_id)
                        self.log_debug(f'Файл {record_id} был удален')
                    except RecordNotFound:
                        self.log_warning(f'Файл {record_id} для удаления не был найден')
                        continue
            msg_id_files = msg_file_repo.get_message_id_files(message_id)
            updated_msg.file_id = list(msg_id_files)
            try:
                await self.msg_route.send_message(
                    session_id=self.session_id,
                    message_send_response=updated_msg
                )
            except SendMessageError:
                self.log_debug(f'Не удалось отправить пакет пользователю об обновлении сообщения {message_id}'
                               f'(возможно у отправителя {sender_id} нет активных подключений)')
            return updated_msg