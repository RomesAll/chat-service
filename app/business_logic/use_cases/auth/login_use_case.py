from datetime import datetime, timezone
from uuid import uuid4
from app.business_logic.auth.jwt_manager import JWTFacade
from app.business_logic.auth.password_manager import PasswordManager
from app.business_logic.cache.jwt_white_list import JWTWhiteListCache
from app.business_logic.exceptions import CheckPswError
from app.business_logic.unit_of_work import UnitOfWork
from app.business_logic.use_cases.interface.iuse_case import IUseCase
from app.shared.dtos import UserDtoGetResponse
from app.shared.dtos.auth import LoginDtoRequest, LoginOrRegisterDtoResponse
from app.data_access.database.repositories import UserRepository


class LoginUseCase(IUseCase):
    """Use case для входа в систему"""
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

    def execute(self, dto_request_data: LoginDtoRequest) -> LoginOrRegisterDtoResponse:
        with self.uow as uow:
            user_repo = uow.get_repository(UserRepository)
            user_info: UserDtoGetResponse = user_repo.get_by_id(dto_request_data.user_id)
            user_password: bytes = user_repo.get_hash_psw(dto_request_data.user_id)
            if not self.psw_manager.check_equal_psw(
                    dto_request_data.password,
                    user_password
            ):
                raise CheckPswError(dto_request_data.user_id)
            refresh_token_id = uuid4()
            jwt_tokens = self.jwt_manager.create_tokens(
                user_info.id, user_info.user_name, user_info.role, refresh_token_id
            )
            self.jwt_white_list.save_refresh_token(
                user_id=user_info.id,
                token_id=refresh_token_id,
                ex=int((datetime.now(tz=timezone.utc) + JWTFacade.jwt_refresh_manager.EXPIRES_DELTA).timestamp())
            )
            return LoginOrRegisterDtoResponse(
                user_info=user_info,
                refresh_token=jwt_tokens.refresh_token,
                access_token=jwt_tokens.access_token
            )
