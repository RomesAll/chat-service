import asyncio
from business_logic.active_session.message_sender.interface import IMessageRoute
from business_logic.exceptions import SendMessageError
from shared.dtos.message import GroupMessageDtoSend
from asyncio import Queue


class GroupMessageRoute(IMessageRoute):
    """Сервис для управления отправкой групповых сообщений"""

    def __init__(self):
        # Асинхронная очередь, в которую добавляются сообщения для broadcast (слушает отдельный воркер)
        self.processing_send_queue: Queue = Queue(maxsize=100)
        # Фоновый воркер для broadcast сообщений в комнате
        loop = asyncio.get_running_loop()
        self._worker_task = loop.create_task(self._worker())

    async def send_message(
            self,
            message_send_request: GroupMessageDtoSend
    ):
        """Отправка и сохранение сообщения всем пользователям в комнате"""
        await self.processing_send_queue.put(message_send_request)

    async def _worker(self):
        """Асинхронный воркер для отправки сообщений всем пользователям"""
        message_send_request: GroupMessageDtoSend | None = None
        while True:
            try:
                message_send_request: GroupMessageDtoSend = await self.processing_send_queue.get()
                for connection in message_send_request.connections:
                    await connection.send_json(message_send_request)
            except Exception as e:
                if message_send_request:
                    raise SendMessageError(
                        message_send_request.sender_id,
                        message_send_request.chat_id,
                        str(e)
                    )
                raise
