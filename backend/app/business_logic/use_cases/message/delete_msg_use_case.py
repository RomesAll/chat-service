from typing import cast
from uuid import UUID
from app.business_logic.active_session.active_session_manager import ActiveSessionManager
from app.business_logic.file_manager.file_manager import FileManager
from app.business_logic.unit_of_work import UnitOfWork
from app.business_logic.use_cases.interface.iuse_case import IUseCase
from app.data_access.exceptions import RecordNotFound
from app.shared.dtos import MessageType, GroupMessageDtoResponse, MessageDtoGetResponse, AuditPostDto
from app.shared.dtos.base import WebsocketPackage, WebsocketActionType
from app.data_access.database.repositories import PrivateMessageRepository, MessageAttachmentsRepository
from app.data_access.database.repositories.message import GroupMessageRepository
from app.business_logic.decorators import audit_system_async
from app.business_logic.exceptions import MessageOwnerInCorrect, UserNotFoundError
from app.shared.log_config import LogMixin


class DeleteMsgUseCase(IUseCase, LogMixin):
    """Use case для удаления сообщения"""
    def __init__(
            self,
            uow: UnitOfWork,
            type_message: MessageType,
            active_session_manager: ActiveSessionManager,
            file_manager: type[FileManager],
            dto_audit: AuditPostDto
    ):
        self.uow = uow
        self.type_message = type_message
        self.active_session_manager = active_session_manager
        self.file_manager = file_manager
        self.dto_audit = dto_audit

    @audit_system_async
    async def execute(
            self,
            message_id: UUID,
            sender_id: str,
            type_msg: MessageType,
    ) -> UUID:
        mapping_msg_type = {
            type_msg.PRIVATE_MSG: self._delete_in_private_msg,
            type_msg.GROUP_MSG: self._delete_in_group_msg
        }
        with self.uow as uow:
            msg_file_repo = uow.get_repository(MessageAttachmentsRepository)
            func = mapping_msg_type.get(type_msg)
            msg_files = msg_file_repo.get_message_id_files(message_id)
            for file_id in list(msg_files):
                try:
                    record_id = msg_file_repo.hard_delete(file_id)
                    self.log_debug(f'Файл {record_id} был удален (сообщение: {message_id})')
                except RecordNotFound:
                    self.log_warning(f'Файл {record_id} для удаления не был найден (сообщение: {message_id})')
                    continue
            result = await func(message_id, sender_id)
            self.log_info(f'Сообщение успешно удалено, id сообщения {message_id}')
            return result

    async def _delete_in_private_msg(self, message_id: UUID, sender_id: str) -> UUID:
        with self.uow as uow:
            msg_repo = uow.get_repository(PrivateMessageRepository)
            msg_info: MessageDtoGetResponse = msg_repo.get_by_id(message_id)
            self.log_debug(f'Получена информация о сообщении для message_id {message_id}')
            if msg_info.sender_id != sender_id:
                exc = MessageOwnerInCorrect(message_id, sender_id)
                self.log_error(exc.message)
                raise exc
            record_id = msg_repo.hard_delete(message_id)
            self.log_info(f'Сообщение успешно удалено, id записи {record_id}')
            try:
                active_session = self.active_session_manager.get_or_create_session(
                    user_id=msg_info.recipient_id
                )
                for conn in active_session.user_sessions.values():
                    package = WebsocketPackage(
                        action_type=WebsocketActionType.DELETE_MSG,
                        payload={
                            'message_id': message_id
                        }
                    )
                    await conn.send_json(**package.model_dump(mode='json'))
            except Exception:
                self.log_debug(f'Не удалось отправить пакет к пользователю об удалении сообщения')
            return cast(UUID, record_id)

    async def _delete_in_group_msg(self, message_id: UUID, sender_id: str) -> UUID:
        with self.uow as uow:
            msg_repo = uow.get_repository(GroupMessageRepository)
            msg_info: GroupMessageDtoResponse = msg_repo.get_by_id(message_id)
            self.log_debug(f'Получена информация о сообщении для message_id {message_id}')
            if msg_info.sender_id != sender_id:
                exc = MessageOwnerInCorrect(message_id, sender_id)
                self.log_error(exc.message)
                raise exc
            record_id = msg_repo.hard_delete(message_id)
            self.log_info(f'Сообщение успешно удалено, id записи {record_id}')
            active_sessions = []
            for user_info in msg_info.payload['keys']:
                for user_id in user_info['user_id']:
                    try:
                        active_sessions.append(self.active_session_manager.get_or_create_session(
                            user_id=user_id
                        ))
                    except UserNotFoundError:
                        continue
            for acs in active_sessions:
                for conn in acs.user_sessions.values():
                    try:
                        package = WebsocketPackage(
                            action_type=WebsocketActionType.DELETE_MSG,
                            payload={
                                'message_id': message_id
                            }
                        )
                        await conn.send_json(**package.model_dump(mode='json'))
                    except Exception:
                        self.log_debug(f'Не удалось отправить пакет к пользователю об удалении сообщения')
                        continue
            return cast(UUID, record_id)
