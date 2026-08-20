import base64
from uuid import UUID

from sqlalchemy.testing import exclude
from starlette.websockets import WebSocket
from websockets import WebSocketException

from business_logic.active_session.active_session_manager import ActiveSessionManager
from business_logic.active_session.message_sender.interface import IMessageRoute
from business_logic.cache.session_key_storage import SessionKeyStorage
from business_logic.encryption.symmetric import SymmetricEncode
from business_logic.exceptions import SendMessageError
from app.shared.dtos import PrivateMessageDtoPostRequest
from dtos import MessageAttachmentsDtoPostRequest, PrivateMessageDtoGetResponse
from dtos.base import WebsocketPackage, WebsocketActionType


class PrivateMessageRoute(IMessageRoute):
    """Сервис для управления отправкой приватных сообщений"""

    def __init__(
            self,
            active_session: ActiveSessionManager,
            symmetric_encode: type[SymmetricEncode],
            session_key_storage: SessionKeyStorage
    ):
        # Менеджер для хранения и управления активными сессиями
        self.active_session = active_session
        self.symmetric_encode = symmetric_encode
        self.session_key_storage = session_key_storage

    async def send_message(
            self,
            session_id: UUID,
            message_send_response: PrivateMessageDtoGetResponse,
    ):
        """Отправка сообщения пользователю"""
        try:
            sender_active_session = self.active_session.get_or_create_session(
                user_id=message_send_response.sender_id
            )
            target_active_session = self.active_session.get_or_create_session(
                user_id=message_send_response.recipient_id
            )
            await self._send_message(
                user_id=message_send_response.sender_id,
                connections=sender_active_session.user_sessions,
                message_send_response=message_send_response,
                exclude_session={session_id, })
            await self._send_message(
                user_id=message_send_response.recipient_id,
                connections=target_active_session.user_sessions,
                message_send_response=message_send_response,
            )
        except Exception as e:
            raise SendMessageError(
                message_send_response.sender_id,
                message_send_response.recipient_id,
                str(e)
            )

    async def _send_message(
            self,
            user_id: str,
            connections: dict[UUID, WebSocket],
            message_send_response: PrivateMessageDtoGetResponse,
            exclude_session: set[UUID] | None = None
    ):
        for session_id, connection in connections:
            if exclude_session and session_id in exclude_session:
                continue
            session_key = self.session_key_storage.get(user_id, session_id)
            if not session_key:
                raise Exception
            encoder = self.symmetric_encode(session_key)
            payload = encoder.encrypt_package(message_send_response.model_dump(mode='json'))
            package = WebsocketPackage(
                action_type=WebsocketActionType.SEND_PRIVATE_MESSAGE,
                payload=base64.b64encode(payload).decode('utf-8')
            )
            await connection.send_json(package.model_dump())