from weakref import ref
from typing import TYPE_CHECKING
from repositories.message import PrivateMessageRepository
from ..exceptions import UserConnectionNotFound, SendMessageError
from ...shared.dtos.message import PrivateMessageDtoPostRequest

if TYPE_CHECKING:
    from .gateway import GateWayMessageService


class PrivateMessageService:
    """Сервис для управления отправкой приватных сообщений"""
    def __init__(
            self,
            gateway: 'GateWayMessageService',
            private_msg_repo: PrivateMessageRepository
    ):
        self.gateway = ref(gateway)
        self.msg_repo = private_msg_repo

    async def send_message(self, message_request: PrivateMessageDtoPostRequest):
        """Отправка сообщения пользователю"""
        try:
            if not(gateway := self.gateway()):
                raise Exception
            if not(active_session := gateway.active_sessions.get(
                    message_request.recipient_id)
            ):
                raise UserConnectionNotFound(message_request.recipient_id)
            for websocket in active_session.websockets:
                await websocket.send_json(message_request)
        except Exception as e:
            raise SendMessageError(
                message_request.sender_id,
                message_request.recipient_id,
                str(e)
            )