from business_logic.active_session.active_session_manager import ActiveSessionManager
from business_logic.active_session.message_sender.interface import IMessageRoute
from business_logic.exceptions import SendMessageError
from app.shared.dtos import PrivateMessageDtoPostRequest, ActiveSession


class PrivateMessageRoute(IMessageRoute):
    """Сервис для управления отправкой приватных сообщений"""

    def __init__(
            self,
            active_session: ActiveSessionManager
    ):
        # Менеджер для хранения и управления активными сессиями
        self.active_session = active_session

    async def send_message(
            self,
            message_send_request: PrivateMessageDtoPostRequest
    ):
        """Отправка сообщения пользователю"""
        try:
            sender_active_session: ActiveSession = self.active_session.get_or_create_session(
                user_id=message_send_request.sender_id
            )
            target_active_session: ActiveSession = self.active_session.get_or_create_session(
                user_id=message_send_request.recipient_id
            )
            if not sender_active_session.websockets:
                raise Exception
            if not target_active_session.websockets:
                raise Exception
            for sender_connection in sender_active_session.websockets:
                sender_json_data = message_send_request.model_dump_json()
                await sender_connection.send_json(sender_json_data)
            if message_send_request.sender_id != message_send_request.recipient_id:
                for target_connection in target_active_session.websockets:
                    target_json_data = message_send_request.model_dump_json()
                    await target_connection.send_json(target_json_data)
        except Exception as e:
            raise SendMessageError(
                message_send_request.sender_id,
                message_send_request.recipient_id,
                str(e)
            )