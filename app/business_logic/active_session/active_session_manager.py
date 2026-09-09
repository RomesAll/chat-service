from uuid import UUID
from starlette.websockets import WebSocket
from app.shared.dtos import ActiveSession, UserDtoBriefInfo
from app.business_logic.exceptions import UserConnectionNotFound, UserNotFoundError
from log_config import LogMixin


class ActiveSessionManager(LogMixin):
    """Класс для управления активными подключениями пользователей"""
    def __init__(self):
        # Список активных подключений
        self.active_sessions: dict[str, ActiveSession] = {}

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
            if create_if_not_exist and user_info:
                active_session = ActiveSession(
                    info=user_info.model_dump(),
                    user_sessions={}
                )
                self.active_sessions[user_info.id] = active_session
                self.log_info(f'Для пользователя {user_id} была создана новая (пустая) активная сессия')
            else:
                exc = UserNotFoundError(user_id)
                self.log_error(exc.message)
                raise exc
        return active_session

    def add_connection(
            self,
            user_info: UserDtoBriefInfo,
            session_id: UUID,
            connection: WebSocket
    ):
        """Добавить новое подключение для пользователя"""
        active_session: ActiveSession = self.get_or_create_session(
            user_id=user_info.id,
            user_info=user_info,
            create_if_not_exist=True
        )
        active_session.user_sessions[session_id] = connection
        self.log_debug(f'Добавлено новое подключение для пользователя {user_info.id}')

    def disconnect(
            self,
            user_id: str
    ):
        """Отключение пользователя"""
        try:
            self.active_sessions.pop(user_id)
            self.log_debug(f'Активная сессия для пользователя {user_id} была удаленна, '
                           f'из-за отсутсвия активных подключений')
        except KeyError:
            exc = UserConnectionNotFound(user_id)
            self.log_error(exc.message)
            raise exc

    def remove_user_active_session(
            self,
            user_id: str,
            session_id: UUID
    ):
        """Удалить конкретное подключение"""
        active_session: ActiveSession = self.get_or_create_session(
            user_id=user_id,
        )
        active_session.user_sessions.pop(session_id)
        self.log_debug(f'Подключение с session_id: {session_id} для пользователя {user_id} было удалено')
        if not active_session.user_sessions:
            self.disconnect(user_id)