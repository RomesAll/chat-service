from _weakrefset import WeakSet
from typing import Any
from uuid import UUID
from weakref import WeakKeyDictionary
from starlette.websockets import WebSocket
from app.shared.dtos import ActiveSession, UserDtoBriefInfo
from business_logic.exceptions import UserConnectionNotFound


class ActiveSessionManager:
    """Класс для управления активными подключениями пользователей"""

    def __init__(self):
        # Список активных подключений
        self.active_sessions: dict[str, ActiveSession] = {}
        # Коллекции для хранения id комнаты -> множества подключений
        self.room_connections: dict[UUID, WeakSet[WebSocket]] = {}
        # Коллекции для хранения подключения -> множества id комнат
        self.connection_rooms: WeakKeyDictionary[Any, set] = WeakKeyDictionary()
        self.route_message = None

    # Методы для управления подключениями в атрибуте active_sessions

    def get_or_create_session(
            self,
            *,
            user_id: str,
            user_info: UserDtoBriefInfo | None = None,
            create_if_not_exist: bool = False
    ) -> ActiveSession:
        """
        Метод для получения активной сессии пользователя или ее создания с пустыми подключениями.
        Управление получением или созданием ActiveSession происходит с помощью флага "create_if_not_exist".

        Мод "create_if_not_exist = False" предназначен для случаев когда пользователь хочет просто получить
        ActiveSession, тогда если ее не будет, то сгенерируется исключение (ошибка).

        Мод "create_if_not_exist = True" предназначен для случаев когда пользователь хочет получить ActiveSession
        (и создать если нет), а потом добавить новое подключение Websocket.
        :param user_id: id пользователя
        :param user_info: информация о пользователе (опционально), но если нужно создать, то (обязательно)
        :param create_if_not_exist: создать ActiveSession если его нет
        :return:
        """
        if (active_session := self.active_sessions.get(user_id)) is None:
            if create_if_not_exist:
                if not user_info:
                    raise Exception
                active_session = ActiveSession(info=user_info, websockets=set())
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
            user_id=user_info.id,
            user_info=user_info,
            create_if_not_exist=True
        )
        active_session.websockets.add(connection)

    def disconnect(
            self,
            user_id: str
    ):
        """Отключение пользователя"""
        try:
            self.active_sessions.pop(user_id)
        except KeyError:
            raise UserConnectionNotFound(user_id)

    def remove_user_active_session(
            self,
            user_id: str,
            connection: WebSocket
    ):
        """Удалить конкретное подключение"""
        active_session: ActiveSession = self.get_or_create_session(
            user_id=user_id,
        )
        active_session.websockets.discard(connection)
        if not active_session.websockets:
            self.disconnect(user_id)

    # Методы для управления подключениями в комнате room_sockets, socket_rooms
    # поскольку в room_sockets, socket_rooms хранятся слабые ссылки, удалять их
    # напрямую из коллекции не нужно!

    def get_or_create_room_connections(
            self,
            *,
            room_id: UUID,
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
            user_id: str,
            room_id: UUID
    ):
        """Добавление всех подключений пользователя в комнату"""
        user_active_session: ActiveSession = self.get_or_create_session(
            user_id=user_id,
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
            room_id=room_id,
            create_if_not_exist=True
        )
        room_connections.add(connection)
        if (current_connection_rooms := self.connection_rooms.get(connection, None)) is None:
            current_connection_rooms = set()
            self.connection_rooms[connection] = current_connection_rooms
        current_connection_rooms.add(room_id)


_manager_instance = None

def get_session_manager() -> ActiveSessionManager:
    """Единственная точка доступа к менеджеру"""
    global _manager_instance
    if _manager_instance is None:
        _manager_instance = ActiveSessionManager()
    return _manager_instance

active_session_manager = get_session_manager()

__all__ = ['get_session_manager', 'active_session_manager', 'ActiveSessionManager']