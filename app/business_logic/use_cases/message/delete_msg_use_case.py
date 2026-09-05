from uuid import UUID
from app.business_logic.active_session.active_session_manager import ActiveSessionManager
from app.business_logic.file_manager.file_manager import FileManager
from app.business_logic.unit_of_work import UnitOfWork
from app.business_logic.use_cases.interface.iuse_case import IUseCase
from app.shared.dtos import MessageType, GroupMessageDtoResponse, MessageDtoGetResponse
from app.shared.dtos.base import WebsocketPackage, WebsocketActionType
from app.data_access.database.repositories import PrivateMessageRepository
from app.data_access.database.repositories.message import GroupMessageRepository


class DeleteMsgUseCase(IUseCase):
    """Use case для удаления сообщения"""
    def __init__(
            self,
            uow: UnitOfWork,
            type_message: MessageType,
            active_session_manager: ActiveSessionManager,
            file_manager: type[FileManager]
    ):
        self.uow = uow
        self.type_message = type_message
        self.active_session_manager = active_session_manager
        self.file_manager = file_manager

    async def execute(self, message_id: UUID, sender_id: str, type_msg: MessageType) -> UUID:
        mapping_msg_type = {
            type_msg.PRIVATE_MSG: self._get_user_connection_in_private_msg,
            type_msg.GROUP_MSG: self._get_user_connection_in_group_msg
        }
        result = await mapping_msg_type.get(type_msg)(message_id, sender_id)
        return result

    async def _get_user_connection_in_private_msg(self, message_id: UUID, sender_id: str) -> UUID:
        with self.uow as uow:
            msg_repo = uow.get_repository(PrivateMessageRepository)
            msg_info: MessageDtoGetResponse = msg_repo.get_by_id(message_id)
            if msg_info.sender_id != sender_id:
                raise Exception
            record_id = msg_repo.hard_delete(message_id)
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
            return record_id

    async def _get_user_connection_in_group_msg(self, message_id: UUID, sender_id: str) -> UUID:
        with self.uow as uow:
            msg_repo = uow.get_repository(GroupMessageRepository)
            msg_info: GroupMessageDtoResponse = msg_repo.get_by_id(message_id)
            if msg_info.sender_id != sender_id:
                raise Exception
            record_id = msg_repo.hard_delete(message_id)
            active_sessions = []
            for user_info in msg_info.payload['keys']:
                for user_id in user_info['user_id']:
                    active_sessions.append(self.active_session_manager.get_or_create_session(
                        user_id=user_id
                    ))
            for acs in active_sessions:
                for conn in acs.user_sessions.values():
                    package = WebsocketPackage(
                        action_type=WebsocketActionType.DELETE_MSG,
                        payload={
                            'message_id': message_id
                        }
                    )
                    await conn.send_json(**package.model_dump(mode='json'))
            return record_id
