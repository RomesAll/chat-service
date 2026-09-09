from uuid import UUID
from app.business_logic.active_session.active_session_manager import ActiveSessionManager
from app.business_logic.cache.jwt_white_list import JWTWhiteListCache
from app.business_logic.cache.session_key_storage import SessionKeyStorage
from app.business_logic.use_cases.interface.iuse_case import IUseCase
from app.shared.log_config import LogMixin
from business_logic.decorators import audit_system
from app.shared.dtos import AuditPostDto


class LogoutUseCase(IUseCase, LogMixin):
    """Use case для выхода из системы"""
    def __init__(
            self,
            active_session_manager: ActiveSessionManager,
            white_list: JWTWhiteListCache,
            session_key_storage: SessionKeyStorage,
            dto_audit: AuditPostDto
    ):
        self.active_session_manager = active_session_manager
        self.white_list = white_list
        self.session_key_storage = session_key_storage
        self.dto_audit = dto_audit

    @audit_system
    def execute(
            self, *,
            user_id: str,
            refresh_token_id: UUID,
            session_id: UUID,
    ):
        del self.white_list[user_id, refresh_token_id]
        self.log_info(f'id refresh ({refresh_token_id}) токена был успешно удален из '
                      f'white list для пользователя {user_id}')
        del self.session_key_storage[user_id, session_id]
        self.log_info(f'Сессионный ключ был успешно удален из кеша '
                      f'для пользователя {user_id} и session_id {session_id}')
        self.active_session_manager.remove_user_active_session(user_id, session_id)