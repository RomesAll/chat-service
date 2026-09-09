from app.business_logic.cache.session_key_storage import SessionKeyStorage
from app.business_logic.encryption.asymmetric import AsymmetricEncrypt
from app.business_logic.unit_of_work import UnitOfWork
from app.business_logic.use_cases.interface.iuse_case import IUseCase
from starlette.websockets import WebSocket
from app.shared.dtos import UserDtoBriefInfo, AuditPostDto
from uuid import UUID
from app.shared.dtos.base import WebsocketPackage, WebsocketActionType
from business_logic.active_session.active_session_manager import ActiveSessionManager
from app.shared.log_config import LogMixin
from business_logic.decorators import audit_system
from business_logic.exceptions import SaveSessionKeyError


class HandshakeUseCase(IUseCase, LogMixin):
    """
    Use case для первого рукопожатия между клиентом и сервером.
    Сервер передает публичный ключ для шифрования сессионного ключа на стороне клиента.
    Далее сервер принимает зашифрованный сессионный ключ, расшифровывает с помощью приватного
    ключа и сохраняет в хранилище.
    """
    def __init__(
            self,
            uow: UnitOfWork,
            active_session_manager: ActiveSessionManager,
            user_connection: WebSocket,
            asymmetric_encrypt: AsymmetricEncrypt,
            session_key_storage: SessionKeyStorage,
            dto_audit: AuditPostDto
    ):
        self.uow = uow
        self.active_session_manager = active_session_manager
        self.user_connection = user_connection
        self.asymmetric_encrypt = asymmetric_encrypt
        self.session_key_storage = session_key_storage
        self.dto_audit = dto_audit

    @audit_system
    async def execute(self, session_id: UUID, user_brief_info: UserDtoBriefInfo, websocket: WebSocket):
        await self.user_connection.send_json(WebsocketPackage(
            action_type=WebsocketActionType.GET_SERVER_PUBLIC_KEY.value,
            payload=self.asymmetric_encrypt.get_public_key()
        ).model_dump(mode='json'))
        self.log_info(f'Пользователю {user_brief_info.id} был отправлен публичный ключ сервера')
        recv_package_raw = await self.user_connection.receive_json()
        self.log_info(f'От пользователя {user_brief_info.id} был получен пакет с '
                      f'зашифрованы (пуб. ключом сервера) сессионным ключом')
        recv_package = WebsocketPackage(
            action_type=recv_package_raw['action_type'],
            payload=recv_package_raw['payload']
        )
        user_encrypt_session_key = recv_package.payload['user_encrypt_session_key']
        session_key = self.asymmetric_encrypt.decoding_session_key(
            encrypt_session_key=user_encrypt_session_key
        )
        try:
            self.session_key_storage.save(
                user_id=user_brief_info.id,
                session_id=session_id,
                session_key=session_key
            )
            self.log_info(f'Сессионный ключ пользователя {user_brief_info.id} был'
                          f'успешно сохранен в кеш по session_id {session_id}')
        except SaveSessionKeyError:
            self.log_warning(f'Ошибка сохранения сессионного ключа для '
                             f'пользователя {user_brief_info.id} в кеш, поэтому он был '
                             f'сохранен во временное хранилище')
        await self.user_connection.send_json(
            WebsocketPackage(
                action_type=WebsocketActionType.GET_SESSION_ID.value,
                payload=str(session_id)).model_dump(mode='json')
        )
        self.log_info(f'Пользователю {user_brief_info.id} был отправлен id сессионного ключа')
        self.active_session_manager.add_connection(
            user_info=user_brief_info,
            session_id=session_id,
            connection=websocket
        )
        self.log_info(f'Новое подключение пользователя {user_brief_info.id} '
                      f'было добавлено в менеджер активных сессий')