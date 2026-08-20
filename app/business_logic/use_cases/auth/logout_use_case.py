from uuid import UUID
from app.business_logic.active_session.active_session_manager import ActiveSessionManager
from business_logic.cache.jwt_white_list import JWTWhiteListCache
from business_logic.cache.session_key_storage import SessionKeyStorage
from business_logic.use_cases.interface.iuse_case import IUseCase


class LogoutUseCase(IUseCase):
    """Use case для выхода из системы"""
    def __init__(
            self,
            active_session_manager: ActiveSessionManager,
            white_list: JWTWhiteListCache,
            session_key_storage: SessionKeyStorage
    ):
        self.active_session_manager = active_session_manager
        self.white_list = white_list
        self.session_key_storage = session_key_storage

    def execute(self, user_id: str, refresh_token_id: UUID, session_id: UUID) -> tuple[bool, bool]:
        is_delete_refresh = self.white_list.delete_refresh_token(
            user_id=user_id,
            token_id=refresh_token_id,
        )
        is_delete_session_key = self.session_key_storage.delete(
            user_id=user_id,
            session_id=session_id,
        )
        return is_delete_refresh, is_delete_session_key