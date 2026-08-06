from uuid import UUID
from weakref import WeakSet, WeakKeyDictionary, ref
from starlette.websockets import WebSocket
from typing import TYPE_CHECKING
from repositories.message import GroupMessageRepository
from shared.dtos.base import DtoIdRecordRequest
from shared.dtos.room import RoomDtoGetResponse
from ..exceptions import SendMessageError
from ...shared.dtos.message import GroupMessageDtoPostRequest
from asyncio import Queue, create_task

if TYPE_CHECKING:
    from .gateway import GateWayMessageService


class GroupMessageService:
    """Сервис для управления отправкой групповых сообщений"""
    def __init__(
            self,
            gateway: 'GateWayMessageService',
            group_msg_repo: GroupMessageRepository,
    ):
        self.room_sockets: dict[UUID, WeakSet[WebSocket]] = {}
        self.socket_rooms: WeakKeyDictionary = WeakKeyDictionary()
        self.gateway = ref(gateway)
        self.msg_repo = group_msg_repo
        self.processing_send_queue: Queue = Queue()
        create_task(self._worker())

    def send_message(self, message_request: GroupMessageDtoPostRequest):
        """Отправка и сохранение сообщения всем пользователям в комнате"""
        self.processing_send_queue.put(message_request)

    def get_connection_in_room(self, room_id):
        """Генератор для получения подключений"""
        connections = self.room_sockets.get(room_id)
        if not connections:
            raise Exception
        for connection in connections:
            yield connection

    async def _worker(self):
        """Асинхронный воркер для отправки сообщений всем пользователям"""
        message_request: GroupMessageDtoPostRequest | None = None
        while True:
            try:
                message_request: GroupMessageDtoPostRequest = await self.processing_send_queue.get()
                for connection in self.get_connection_in_room(message_request.chat_id):
                    await connection.send_json(message_request)
            except Exception as e:
                if message_request:
                    raise SendMessageError(
                        message_request.sender_id,
                        message_request.chat_id,
                        str(e)
                    )
                raise

    def add_new_socket(self, room_id: UUID, websocket: WebSocket):
        """Добавление подключений пользователя в комнату"""
        connections: WeakSet | None = self.room_sockets.get(room_id, None)
        if not connections:
            if not(gateway := self.gateway()):
                raise Exception
            room: RoomDtoGetResponse = gateway.room_manager.get_one(DtoIdRecordRequest(id=room_id))
            self.room_sockets[room.id] = WeakSet()
        self.room_sockets[room_id].add(websocket)

        if not(self.socket_rooms.get(websocket, None)):
            self.socket_rooms[websocket] = set()
        self.socket_rooms[websocket].add(room_id)
