from datetime import datetime, timezone
from uuid import uuid4
from pydantic import SecretStr
from app.business_logic.auth.jwt_manager import JWTFacade
from app.business_logic.auth.password_manager import PasswordManager
from app.business_logic.cache.jwt_white_list import JWTWhiteListCache
from app.business_logic.unit_of_work import UnitOfWork
from app.business_logic.use_cases.interface.iuse_case import IUseCase
from app.shared.dtos import UserDtoPostRequest, UserDtoGetResponse, AuditPostDto
from app.shared.dtos.auth import LoginOrRegisterDtoResponse
from app.data_access.database.repositories import UserRepository
from business_logic.decorators import audit_system
from business_logic.exceptions import SaveIdRefreshTokenWhiteListError
from log_config import LogMixin


class RegisterUser(IUseCase, LogMixin):
    """Use case для регистрации пользователей"""
    def __init__(
            self,
            uow: UnitOfWork,
            psw_manager: type[PasswordManager],
            jwt_manager: type[JWTFacade],
            jwt_white_list: JWTWhiteListCache,
            dto_audit: AuditPostDto
    ):
        self.uow = uow
        self.psw_manager = psw_manager
        self.jwt_manager = jwt_manager
        self.jwt_white_list = jwt_white_list
        self.dto_audit = dto_audit

    @audit_system
    def execute(
            self, *,
            dto_register_user: UserDtoPostRequest,
    ) -> LoginOrRegisterDtoResponse:
        with self.uow as uow:
            user_repo = uow.get_repository(UserRepository)
            hash_psw: bytes = self.psw_manager.hash_password(dto_register_user.password)
            dto_register_user.password = SecretStr(hash_psw.decode())
            user_info: UserDtoGetResponse = user_repo.save(dto_register_user)
            refresh_token_id = uuid4()
            tokens = self.jwt_manager.create_tokens(
                user_info.id, user_info.user_name, user_info.role, refresh_token_id
            )
            try:
                self.jwt_white_list.save_refresh_token(
                    user_id=user_info.id,
                    token_id=refresh_token_id,
                    ex=int((datetime.now(tz=timezone.utc) + JWTFacade.jwt_refresh_manager.EXPIRES_DELTA).timestamp())
                )
                self.log_info(f'Сохранение id refresh токена {refresh_token_id} '
                              f'в white list для пользователя {user_info.id} прошло успешно')
            except SaveIdRefreshTokenWhiteListError:
                self.log_warning(f'Не удалось сохранить id refresh токена {refresh_token_id} в white list '
                                 f'для пользователя {user_info.id} (он был сохранен во временное хранилище)')
            self.log_info(f'Регистрация для пользователя {user_info.id} выполнена успешно')
            return LoginOrRegisterDtoResponse(
                user_info=user_info,
                access_token=tokens.access_token,
                refresh_token=tokens.refresh_token
            )