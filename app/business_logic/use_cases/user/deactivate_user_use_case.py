from uuid import UUID
from app.business_logic.active_session.active_session_manager import ActiveSessionManager
from app.business_logic.cache.session_key_storage import SessionKeyStorage
from app.business_logic.exceptions import UserNotFoundError
from app.business_logic.use_cases.interface.iuse_case import IUseCase


class DeactivateUseCase(IUseCase):
    """Use case для выхода из системы"""
    def __init__(
            self,
            active_session_manager: ActiveSessionManager,
            session_key_storage: SessionKeyStorage
    ):
        self.active_session_manager = active_session_manager
        self.session_key_storage = session_key_storage

    def execute(self, user_id: str, session_id: UUID) -> tuple[bool, bool]:
        is_delete_session_key = self.session_key_storage.delete(
            user_id=user_id,
            session_id=session_id,
        )
        user_session = self.active_session_manager.active_sessions.get(user_id)
        if not user_session:
            raise UserNotFoundError(user_id)
        is_delete_websocket_conn = user_session.user_sessions.pop(session_id, None)
        return is_delete_session_key, bool(is_delete_websocket_conn)