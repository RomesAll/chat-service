from uuid import uuid4
from app.business_logic.auth.jwt_manager import JWTFacade
from app.business_logic.cache.jwt_white_list import JWTWhiteListCache
from app.business_logic.use_cases.interface.iuse_case import IUseCase
from app.shared.dtos import JWTRefreshTokenResponse
from app.shared.dtos.jwt import JWTTokenResponse
from business_logic.decorators import audit_system
from business_logic.exceptions import RefreshTokenInActive
from app.shared.log_config import LogMixin
from dtos import AuditPostDto


class RefreshTokenUseCase(IUseCase, LogMixin):
    """Use case для обновления токенов"""
    def __init__(
            self,
            jwt_facade: type[JWTFacade],
            jwt_white_list: JWTWhiteListCache,
            dto_audit: AuditPostDto
    ):
        self.jwt_facade = jwt_facade
        self.jwt_white_list = jwt_white_list
        self.dto_audit = dto_audit

    @audit_system
    def execute(
            self, *,
            refresh_token: JWTRefreshTokenResponse,
    ) -> JWTTokenResponse:
        if self.jwt_white_list.is_token_active(
                user_id=refresh_token.user_id,
                token_id=refresh_token.refresh_id
        ):
            exc = RefreshTokenInActive(refresh_token.user_id, refresh_token.refresh_id)
            self.log_error(exc.message)
            raise exc
        new_refresh_id = uuid4()
        self.log_debug(f'Для пользователя {refresh_token.user_id} был '
                       f'сгенерирован id для refresh токена {new_refresh_id}')
        self.jwt_white_list(
            user_id=refresh_token.user_id,
            old_refresh_id=refresh_token.refresh_id,
            new_refresh_id=new_refresh_id
        )
        self.log_info(f'id refresh токена для пользователя {refresh_token.user_id} '
                      f'успешно обновлен в white list')
        tokens = self.jwt_facade.create_tokens(
            user_id=refresh_token.user_id,
            role=refresh_token.role,
            sub=refresh_token.sub,
            refresh_id=new_refresh_id
        )
        self.log_info(f'Для пользователя {refresh_token.user_id} сгенерирована пара токенов access и refresh')
        return tokens