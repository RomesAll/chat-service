from business_logic.active_session.message_sender.interface import IMessageRoute
from business_logic.exceptions import SendMessageError
from shared.dtos.message import PrivateMessageDtoSend


class PrivateMessageRoute(IMessageRoute):
    """Сервис для управления отправкой приватных сообщений"""

    async def send_message(
            self,
            message_send_request: PrivateMessageDtoSend
    ):
        """Отправка сообщения пользователю"""
        try:
            for websocket in message_send_request.connections:
                await websocket.send_json(message_send_request)
        except Exception as e:
            raise SendMessageError(
                message_send_request.sender_id,
                message_send_request.recipient_id,
                str(e)
            )