from business_logic.active_session.message_sender.group_message import GroupMessageRoute
from business_logic.active_session.message_sender.interface import IMessageRoute
from business_logic.active_session.message_sender.private_message import PrivateMessageRoute
from business_logic.exceptions import RouteMessageError
from models.message import MessageType
from shared.dtos.message import BaseMessageDtoSend


class RouteMessage:
    """Класс маршрутизации сообщений"""

    def __init__(
            self,
            private_message_route: PrivateMessageRoute,
            group_message_route: GroupMessageRoute
    ):
        # Приватные и групповые пути для отправки сообщений
        self.private_message_route = private_message_route
        self.group_message_route = group_message_route
        # Маппинг сообщений по типам сообщения
        self.MAPPING_MESSAGE_TYPE = {
            MessageType.PRIVATE: self.private_message_route,
            MessageType.GROUP: self.group_message_route
        }

    async def routing_message(
            self,
            message_request: BaseMessageDtoSend,
    ):
        """Маршрутизация сообщений"""
        service: IMessageRoute | None = self.MAPPING_MESSAGE_TYPE.get(message_request.type)
        if not service:
            raise RouteMessageError(message_request)
        await service.send_message(message_request)