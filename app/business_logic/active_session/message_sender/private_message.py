from starlette.websockets import WebSocket
from business_logic.active_session.message_sender.interface import IMessageRoute
from business_logic.exceptions import SendMessageError
from shared.dtos.message import PrivateMessageDtoPostRequest


class PrivateMessageRoute(IMessageRoute):
    """Сервис для управления отправкой приватных сообщений"""

    async def send_message(
            self,
            message_request: PrivateMessageDtoPostRequest,
            connections: set[WebSocket]
    ):
        """Отправка сообщения пользователю"""
        try:
            for websocket in connections:
                await websocket.send_json(message_request)
        except Exception as e:
            raise SendMessageError(
                message_request.sender_id,
                message_request.recipient_id,
                str(e)
            )