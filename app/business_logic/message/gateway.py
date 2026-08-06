from uuid import UUID
from starlette.websockets import WebSocket
from app.business_logic.message.group_message import GroupMessageService
from app.business_logic.message.private_message import PrivateMessageService
from app.shared.dtos.base import DtoIdRecordRequest
from app.shared.dtos.user import ActiveSession, UserInfo, UserDtoGetResponse
from business_logic.exceptions import UserConnectionNotFound
from business_logic.room.room_manager import RoomManager
from business_logic.user.user_manager import UserManager
from models.message import MessageType
from repositories.message import PrivateMessageRepository, GroupMessageRepository
from shared.dtos.message import BaseMessageDtoPostRequest


class GateWayMessageService:
    """
    Сервис оркестрации отправки сообщений
    """
    def __init__(
            self,
            private_msg_repo: PrivateMessageRepository,
            group_msg_repo: GroupMessageRepository,
            room_manager: RoomManager,
            user_manager: UserManager
    ):
        # Список активных подключений
        self.active_sessions: dict[UUID, ActiveSession] = {}

        # Приватные и групповые сервисы для отправки сообщений
        self.group_message: GroupMessageService = GroupMessageService(
            gateway=self,
            group_msg_repo=group_msg_repo,
        )
        self.private_message: PrivateMessageService = PrivateMessageService(
            gateway=self,
            private_msg_repo=private_msg_repo
        )

        # Менеджеры для управления пользователями и комнатами
        self.room_manager = room_manager
        self.user_manager = user_manager

        # Маппинг сообщений по типам сообщения
        self.MAPPING_MESSAGE_TYPE = {
            MessageType.PRIVATE: self.private_message,
            MessageType.GROUP: self.group_message
        }

    def append_connection(self, user_id: DtoIdRecordRequest, websocket: WebSocket):
        """Добавление нового подключения"""
        if not(active_session := self.active_sessions.get(user_id.id, None)):
            user_info: UserInfo = UserInfo(**self.user_manager.get_one(user_id).model_dump())
            active_session = ActiveSession(
                info=user_info,
            )
        active_session.websockets.add(websocket)

    def append_connection_in_room(self, user_id: DtoIdRecordRequest):
        """Добавление подключений в комнату"""
        if not(active_session := self.active_sessions.get(user_id.id, None)):
            raise UserConnectionNotFound(user_id.id)
        for websocket in active_session.websockets:
            self.group_message.add_new_socket(user_id.id, websocket)

    def remove_connection(self, user_id: DtoIdRecordRequest, websocket: WebSocket):
        """Удаление подключения"""
        if not (active_session := self.active_sessions.get(user_id.id, None)):
            raise UserConnectionNotFound(user_id.id)
        active_session.websockets.discard(websocket)
        if len(active_session.websockets) == 0:
            self.disconnect(user_id)

    def disconnect(self, user_id: DtoIdRecordRequest):
        """Отключение пользователя"""
        if not(self.active_sessions.get(user_id.id, None)):
            raise UserConnectionNotFound(user_id.id)
        self.active_sessions.pop(user_id.id)

    def get_active_session(self, user_id: DtoIdRecordRequest) -> ActiveSession:
        """Получение активной сессии пользователя"""
        if not(active_session := self.active_sessions.get(user_id.id, None)):
            raise UserConnectionNotFound(user_id.id)
        return active_session

    async def get_active_sessions_stream(self, limit: int | None = None):
        """Генератор для порционного вывода данных об активных подключений"""
        count = 0
        for user_id, active_session in self.active_sessions.items():
            if limit and count >= limit:
                break
            count += 1
            yield active_session

    def routing_message(self, message_request: BaseMessageDtoPostRequest):
        """Маршрутизация сообщений"""
        service = self.MAPPING_MESSAGE_TYPE.get(message_request.type)
        if not service:
            raise Exception
        service.send_message(message_request)
        result = service.msg_repo.save(message_request)
        return result