from datetime import datetime, timezone
from uuid import uuid4
from pydantic import SecretStr
from business_logic.auth.jwt_manager import JWTFacade
from business_logic.auth.password_manager import PasswordManager
from business_logic.cache.jwt_white_list import JWTWhiteListCache
from business_logic.unit_of_work import UnitOfWork
from business_logic.use_cases.interface.iuse_case import IUseCase
from dtos import UserDtoPostRequest, UserDtoGetResponse
from dtos.auth import LoginOrRegisterDtoResponse
from repositories import UserRepository


class RegisterUser(IUseCase):
    """Use case для регистрации пользователей"""
    def __init__(
            self,
            uow: UnitOfWork,
            psw_manager: type[PasswordManager],
            jwt_manager: type[JWTFacade],
            jwt_white_list: JWTWhiteListCache
    ):
        self.uow = uow
        self.psw_manager = psw_manager
        self.jwt_manager = jwt_manager
        self.jwt_white_list = jwt_white_list

    def execute(self, dto_register_user: UserDtoPostRequest) -> LoginOrRegisterDtoResponse:
        with self.uow as uow:
            user_repo = uow.get_repository(UserRepository)
            hash_psw: bytes = self.psw_manager.hash_password(dto_register_user.password)
            dto_register_user.password = SecretStr(hash_psw.decode())
            user_info: UserDtoGetResponse = user_repo.save(dto_register_user)
            refresh_token_id = uuid4()
            tokens = self.jwt_manager.create_tokens(
                user_info.id, user_info.user_name, user_info.role, refresh_token_id
            )
            self.jwt_white_list.save_refresh_token(
                user_id=user_info.id,
                token_id=refresh_token_id,
                ex=int((datetime.now(tz=timezone.utc) + JWTFacade.jwt_refresh_manager.EXPIRES_DELTA).timestamp())
            )
            return LoginOrRegisterDtoResponse(
                user_info=user_info,
                access_token=tokens.access_token,
                refresh_token=tokens.refresh_token
            )