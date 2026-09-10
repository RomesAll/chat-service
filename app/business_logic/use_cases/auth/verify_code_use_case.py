from datetime import datetime, timezone
from uuid import uuid4
from app.business_logic.cache.verify_code_storage import VerifyCodeStorage
from app.business_logic.use_cases.interface.iuse_case import IUseCase
from app.business_logic.auth import JWTFacade
from app.business_logic.cache import JWTWhiteListCache
from app.business_logic.decorators import audit_system
from app.business_logic.exceptions import SaveIdRefreshTokenWhiteListError, VerifyCodeInCorrect
from app.business_logic.unit_of_work import UnitOfWork
from app.data_access.database.repositories import UserRepository
from app.shared.dtos import AuditPostDto, UserDtoGetResponse
from app.shared.log_config import LogMixin
from app.shared.dtos.auth import VerifyCodeRequest
from app.shared.dtos.user import VerifyCodeResponse


class VerifyCodeUseCase(IUseCase, LogMixin):
    """Use case для подтверждения входа, регистрации с помощью кода"""
    def __init__(
            self,
            uow: UnitOfWork,
            verify_code_storage: VerifyCodeStorage,
            jwt_manager: type[JWTFacade],
            jwt_white_list: JWTWhiteListCache,
            dto_audit: AuditPostDto
    ):
        self.uow = uow
        self.verify_code_storage = verify_code_storage
        self.jwt_manager = jwt_manager
        self.jwt_white_list = jwt_white_list
        self.dto_audit = dto_audit

    @audit_system
    def execute(self, verify_code_request: VerifyCodeRequest) -> VerifyCodeResponse:
        with self.uow as uow:
            user_repo = uow.get_repository(UserRepository)
            user_info: UserDtoGetResponse = user_repo.get_by_id(verify_code_request.user_id)
            if not(self.verify_code_storage.validate_code(
                    user_id=verify_code_request.user_id,
                    email=verify_code_request.email,
                    code=verify_code_request.code
            )):
                exc = VerifyCodeInCorrect()
                self.log_error(f'Введенный код подтверждения неверный для пользователя {user_info.id}')
                raise exc
            refresh_token_id = uuid4()
            self.log_info(f'Сгенерирован id для refresh токена для пользователя '
                          f'{verify_code_request.user_id}, который будет храниться в white list')
            jwt_tokens = self.jwt_manager.create_tokens(
                user_info.id, user_info.user_name, user_info.role, refresh_token_id
            )
            self.log_info(f'Для пользователя {verify_code_request.user_id} создана пара access и refresh токенов')
            try:
                self.jwt_white_list.save_refresh_token(
                    user_id=user_info.id,
                    token_id=refresh_token_id,
                    ex=int((datetime.now(tz=timezone.utc) + JWTFacade.jwt_refresh_manager.EXPIRES_DELTA).timestamp())
                )
                self.log_info(f'Для пользователя {verify_code_request.user_id} id refresh токена сохранено в white list')
            except SaveIdRefreshTokenWhiteListError:
                self.log_warning(f'Не удалось сохранить id refresh токена в white list, '
                                 f'поэтому он будет сохранен во временное хранилище')
            return VerifyCodeResponse(
                user_info=user_info,
                refresh_token=jwt_tokens.refresh_token,
                access_token=jwt_tokens.access_token
            )