from app.business_logic.cache.session_key_storage import SessionKeyStorage
from app.business_logic.encryption.asymmetric import AsymmetricEncrypt
from app.business_logic.unit_of_work import UnitOfWork
from app.business_logic.use_cases.interface.iuse_case import IUseCase
from starlette.websockets import WebSocket
from app.shared.dtos import UserDtoBriefInfo
from uuid import UUID
from app.shared.dtos.base import WebsocketPackage, WebsocketActionType


class HandshakeUseCase(IUseCase):
    """
    Use case для первого рукопожатия между клиентом и сервером.
    Сервер передает публичный ключ для шифрования сессионного ключа на стороне клиента.
    Далее сервер принимает зашифрованный сессионный ключ, расшифровывает с помощью приватного
    ключа и сохраняет в хранилище.
    """
    def __init__(
            self,
            uow: UnitOfWork,
            user_connection: WebSocket,
            asymmetric_encrypt: AsymmetricEncrypt,
            session_key_storage: SessionKeyStorage
    ):
        self.uow = uow
        self.user_connection = user_connection
        self.asymmetric_encrypt = asymmetric_encrypt
        self.session_key_storage = session_key_storage

    async def execute(self, session_id: UUID, user_brief_info: UserDtoBriefInfo):
        await self.user_connection.send_json(WebsocketPackage(
            action_type=WebsocketActionType.GET_SERVER_PUBLIC_KEY.value,
            payload=self.asymmetric_encrypt.get_public_key()
        ).model_dump(mode='json'))
        recv_package_raw = await self.user_connection.receive_json()
        recv_package = WebsocketPackage(
            action_type=recv_package_raw['action_type'],
            payload=recv_package_raw['payload']
        )
        user_encrypt_session_key = recv_package.payload['user_encrypt_session_key']
        session_key = self.asymmetric_encrypt.decoding_session_key(
            encrypt_session_key=user_encrypt_session_key
        )
        self.session_key_storage.save(
            user_id=user_brief_info.id,
            session_id=session_id,
            session_key=session_key
        )
        await self.user_connection.send_json(WebsocketPackage(
            action_type=WebsocketActionType.GET_SESSION_ID.value,
            payload=str(session_id)
        ).model_dump(mode='json'))