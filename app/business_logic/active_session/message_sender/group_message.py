import asyncio
from uuid import UUID
from app.business_logic.active_session.active_session_manager import ActiveSessionManager
from app.business_logic.active_session.message_sender.interface import IMessageRoute
from app.business_logic.exceptions import SendMessageError
from asyncio import Queue
from app.shared.dtos import GroupMessageDtoResponse, ActiveSession
from app.shared.dtos.base import WebsocketActionType, WebsocketPackage
from app.shared.log_config import LogMixin


class GroupMessageRoute(IMessageRoute, LogMixin):
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
            session_id: UUID,
            message_send_request: GroupMessageDtoResponse,
    ):
        """Отправка и сохранение сообщения всем пользователям в комнате"""
        self.log_debug(f'Групповое сообщение {message_send_request.id} отправлено в очередь')
        await self.processing_send_queue.put((session_id, message_send_request))

    async def _worker(self):
        """Асинхронный воркер для отправки сообщений всем пользователям"""
        message_send_request: GroupMessageDtoResponse | None = None
        while True:
            try:
                session_id, message_send_request = await self.processing_send_queue.get()
                if not hasattr(message_send_request, 'payload'):
                    raise Exception
                keys_info: list[dict] = message_send_request.payload.get('keys', [])
                users_id: list[str] = [key['user_id'] for key in keys_info]
                active_sessions: list[ActiveSession] = []
                for user_id in users_id:
                    try:
                        active_sessions.append(
                            self.active_session.get_or_create_session(
                                user_id=user_id
                            )
                        )
                    except Exception as e:
                        continue
                for acs in active_sessions:
                    package = WebsocketPackage(
                        action_type=WebsocketActionType.SEND_GROUP_MESSAGE,
                        payload=message_send_request.model_dump(mode='json')
                    )
                    for c_session_id, conn in acs.user_sessions.items():
                        if session_id == c_session_id:
                            continue
                        self.log_debug(f'Групповое сообщение отправлено пользователю {acs.info.id} '
                                       f'на подключение с session_id {c_session_id}')
                        await conn.send_json(package)
            except Exception as e:
                if message_send_request:
                    exc = SendMessageError(
                        message_send_request.sender_id,
                        message_send_request.room_id,
                        str(e)
                    )
                    self.log_error(exc.message)
                    raise exc
                self.log_error(f'Неизвестная ошибка при отправки сообщения в группу: {e}')
