from starlette.exceptions import WebSocketException
from app.business_logic.active_session.active_session_manager import ActiveSessionManager
from app.business_logic.exceptions import SyncKeyError
from app.business_logic.use_cases.interface.iuse_case import IUseCase


class SyncPrivateKeysUseCase(IUseCase):
    """Use case для синхронизации приватных ключей между всем подключениями"""
    def __init__(
            self,
            active_session: ActiveSessionManager
    ):
        self.active_session = active_session

    async def execute(self, user_id: str, encrypt_private_keys: dict):
        try:
            user_info = self.active_session.get_or_create_session(
                user_id=user_id
            )
            user_connections = user_info.user_sessions.values()
            for connection in user_connections:
                await connection.send_json(encrypt_private_keys)
        except WebSocketException as e:
            raise SyncKeyError(user_id)