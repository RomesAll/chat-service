import asyncio
from _weakrefset import WeakSet
from starlette.websockets import WebSocket
from business_logic.active_session.active_session_manager import ActiveSessionManager
from business_logic.active_session.message_sender.interface import IMessageRoute
from business_logic.exceptions import SendMessageError
from app.shared.dtos import GroupMessageDtoPostRequest
from asyncio import Queue


class GroupMessageRoute(IMessageRoute):
    """Сервис для управления отправкой групповых сообщений"""

    def __init__(
            self,
            active_session: ActiveSessionManager
    ):
        # Менеджер для хранения и управления активными сессиями
        self.active_session = active_session
        # Асинхронная очередь, в которую добавляются сообщения для broadcast (слушает отдельный воркер)
        self.processing_send_queue: Queue = Queue(maxsize=100)
        # Фоновый воркер для broadcast сообщений в комнате
        self._worker_task = asyncio.create_task(self._worker())

    async def send_message(
            self,
            message_send_request: GroupMessageDtoPostRequest
    ):
        """Отправка и сохранение сообщения всем пользователям в комнате"""
        await self.processing_send_queue.put(message_send_request)

    async def _worker(self):
        """Асинхронный воркер для отправки сообщений всем пользователям"""
        message_send_request: GroupMessageDtoPostRequest | None = None
        while True:
            try:
                message_send_request: GroupMessageDtoPostRequest = await self.processing_send_queue.get()
                room_connections: WeakSet[WebSocket] = self.active_session.get_or_create_room_connections(
                    room_id=message_send_request.chat_id
                )
                for connection in room_connections:
                    json_data = message_send_request.model_dump_json()
                    await connection.send_json(json_data)
            except Exception as e:
                if message_send_request:
                    raise SendMessageError(
                        message_send_request.sender_id,
                        message_send_request.chat_id,
                        str(e)
                    )
                raise
