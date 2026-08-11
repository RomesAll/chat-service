from business_logic.active_session.active_session_manager import ActiveSessionManager
from business_logic.active_session.message_sender.group_message import GroupMessageRoute
from business_logic.active_session.message_sender.interface import IMessageRoute
from business_logic.active_session.message_sender.private_message import PrivateMessageRoute
from business_logic.exceptions import RouteMessageError
from models.message import MessageType
from app.shared.dtos import BaseMessageDtoPostRequest


class RouteMessage:
    """Класс маршрутизации сообщений"""

    def __init__(
            self,
            active_session: ActiveSessionManager,
    ):
        # Менеджер для хранения и управления активными сессиями
        self.active_session = active_session
        # Приватные и групповые пути для отправки сообщений
        self.private_message_route = PrivateMessageRoute(active_session)
        self.group_message_route = GroupMessageRoute(active_session)
        # Маппинг сообщений по типам сообщения
        self.MAPPING_MESSAGE_TYPE = {
            MessageType.PRIVATE: self.private_message_route,
            MessageType.GROUP: self.group_message_route
        }

    async def routing_message(
            self,
            message_dto_request: BaseMessageDtoPostRequest,
    ):
        """Маршрутизация сообщений"""
        route: IMessageRoute | None = self.MAPPING_MESSAGE_TYPE.get(message_dto_request.type)
        if not route:
            raise RouteMessageError(message_dto_request)
        await route.send_message(message_dto_request)