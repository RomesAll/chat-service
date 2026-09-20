from uuid import UUID
from app.business_logic.active_session.active_session_manager import ActiveSessionManager
from app.business_logic.cache.session_key_storage import SessionKeyStorage
from app.business_logic.use_cases.interface.iuse_case import IUseCase
from app.shared.log_config import LogMixin
from app.business_logic.decorators import audit_system


class DeactivateUseCase(IUseCase, LogMixin):
    """Use case для выхода из системы"""
    def __init__(
            self,
            active_session_manager: ActiveSessionManager,
            session_key_storage: SessionKeyStorage
    ):
        self.active_session_manager = active_session_manager
        self.session_key_storage = session_key_storage

    @audit_system
    def execute(self, user_id: str, session_id: UUID):
        del self.session_key_storage[user_id, session_id]
        self.log_info(f'Сессионный ключ пользователя {user_id} успешно удален из кеша')
        self.active_session_manager.remove_user_active_session(user_id, session_id)