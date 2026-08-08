from _weakrefset import WeakSet
from typing import Any
from uuid import UUID
from weakref import WeakKeyDictionary
from starlette.websockets import WebSocket
from app.shared.dtos.user import ActiveSession, UserDtoBriefInfo
from business_logic.exceptions import UserConnectionNotFound
from business_logic.active_session.message_sender.group_message import GroupMessageRoute
from business_logic.active_session.message_sender.private_message import PrivateMessageRoute
from business_logic.active_session.route_message import RouteMessage
from shared.dtos.message import BaseMessageDtoSend


class ActiveSessionManager:
    """Класс для управления активными подключениями пользователей"""

    def __init__(self):
        # Список активных подключений
        self.active_sessions: dict[UUID, ActiveSession] = {}
        # Коллекции для хранения id комнаты -> множества подключений
        self.room_connections: dict[UUID, WeakSet[WebSocket]] = {}
        # Коллекции для хранения подключения -> множества id комнат
        self.connection_rooms: WeakKeyDictionary[Any, set] = WeakKeyDictionary()
        # Маршрутизатор сообщений
        self.route_message = RouteMessage(
            group_message_route=GroupMessageRoute(),
            private_message_route=PrivateMessageRoute()
        )

    # Методы для управления подключениями в атрибуте active_sessions

    async def send_message(
            self,
            message: BaseMessageDtoSend
    ):
        """Метод делегирования отправки сообщения маршрутизатору"""
        await self.route_message.routing_message(message)

    def get_or_create_session(
            self,
            user_info: UserDtoBriefInfo,
            *,
            create_if_not_exist: bool = False
    ) -> ActiveSession:
        """
        Метод для получения активной сессии пользователя или ее создания с пустыми подключениями.
        Управление получением или созданием ActiveSession происходит с помощью флага "create_if_not_exist".

        Мод "create_if_not_exist = False" предназначен для случаев когда пользователь хочет просто получить
        ActiveSession, тогда если ее не будет, то сгенерируется исключение (ошибка).

        Мод "create_if_not_exist = True" предназначен для случаев когда пользователь хочет получить ActiveSession
        (и создать если нет), а потом добавить новое подключение Websocket.
        :param user_info: информация о пользователе
        :param create_if_not_exist: создать ActiveSession если его нет
        :return:
        """
        if (active_session := self.active_sessions.get(user_info.id)) is None:
            if create_if_not_exist:
                active_session = ActiveSession(info=user_info)
                self.active_sessions[user_info.id] = active_session
            else:
                raise Exception
        return active_session

    def add_connection(
            self,
            user_info: UserDtoBriefInfo,
            connection: WebSocket
    ):
        """Добавить новое подключение для пользователя"""
        active_session: ActiveSession = self.get_or_create_session(
            user_info,
            create_if_not_exist=True
        )
        active_session.websockets.add(connection)

    def disconnect(
            self,
            user_info: UserDtoBriefInfo
    ):
        """Отключение пользователя"""
        try:
            self.active_sessions.pop(user_info.id)
        except KeyError:
            raise UserConnectionNotFound(user_info.id)

    def remove_user_active_session(
            self,
            user_info: UserDtoBriefInfo,
            connection: WebSocket
    ):
        """Удалить конкретное подключение"""
        active_session: ActiveSession = self.get_or_create_session(
            user_info,
            create_if_not_exist=False
        )
        active_session.websockets.discard(connection)
        if not active_session.websockets:
            self.disconnect(user_info)

    # Методы для управления подключениями в комнате room_sockets, socket_rooms
    # поскольку в room_sockets, socket_rooms хранятся слабые ссылки, удалять их
    # напрямую из коллекции не нужно!

    def get_or_create_room_connections(
            self,
            room_id: UUID,
            *,
            create_if_not_exist: bool = False
    ) -> WeakSet[WebSocket]:
        """
        Метод для получения подключений в комнате или ее создания с пустыми подключениями.
        Управление происходит с помощью флага "create_if_not_exist".

        Мод "create_if_not_exist = False" предназначен для случаев когда пользователь хочет просто получить
        множество подключений в комнате, тогда если ее не будет, то сгенерируется исключение (ошибка).

        Мод "create_if_not_exist = True" предназначен для случаев когда пользователь хочет получить множество подключений в комнате
        (и создать если нет), а потом добавить новое подключение Websocket.
        :param room_id:
        :param create_if_not_exist:
        :return:
        """
        if (current_room_connections := self.room_connections.get(room_id)) is None:
            if create_if_not_exist:
                current_room_connections = WeakSet()
                self.room_connections[room_id] = current_room_connections
            else:
                raise Exception
        return current_room_connections


    def add_user_connections_in_room(
            self,
            user_info: UserDtoBriefInfo,
            room_id: UUID
    ):
        """Добавление всех подключений пользователя в комнату"""
        user_active_session: ActiveSession = self.get_or_create_session(
            user_info,
            create_if_not_exist=False
        )
        for user_connection in user_active_session.websockets:
            self.add_connection_in_room(room_id, user_connection)

    def add_connection_in_room(
            self,
            room_id: UUID,
            connection: WebSocket
    ):
        """Добавление конкретных подключений в комнату"""
        room_connections: WeakSet[WebSocket] = self.get_or_create_room_connections(
            room_id,
            create_if_not_exist=True
        )
        room_connections.add(connection)
        if (current_connection_rooms := self.connection_rooms.get(connection, None)) is None:
            current_connection_rooms = set()
            self.connection_rooms[connection] = current_connection_rooms
        current_connection_rooms.add(room_id)