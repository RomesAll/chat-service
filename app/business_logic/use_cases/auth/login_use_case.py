from business_logic.auth.jwt_manager import JWTFacade
from business_logic.auth.password_manager import PasswordManager
from business_logic.unit_of_work import UnitOfWork
from business_logic.use_cases.interface.iuse_case import IUseCase
from app.shared.dtos import UserDtoGetResponse
from dtos.auth import LoginDtoRequest, LoginOrRegisterDtoResponse
from repositories import UserRepository


class LoginUseCase(IUseCase):

    def __init__(
            self,
            uow: UnitOfWork,
            psw_manager: type[PasswordManager],
            jwt_manager: type[JWTFacade]
    ):
        self.uow = uow
        self.psw_manager = psw_manager
        self.jwt_manager = jwt_manager

    def execute(self, dto_request_data: LoginDtoRequest) -> LoginOrRegisterDtoResponse:
        with self.uow as uow:
            user_repo = uow.get_repository(UserRepository)
            user_info: UserDtoGetResponse = user_repo.get_by_id(dto_request_data.user_id)
            user_password: bytes = user_repo.get_hash_psw(dto_request_data.user_id)
            if not self.psw_manager.check_equal_psw(
                    dto_request_data.password,
                    user_password
            ):
                raise Exception
            jwt_tokens = self.jwt_manager.create_tokens(
                user_info.id, user_info.user_name, user_info.role
            )
            return LoginOrRegisterDtoResponse(
                user_info=user_info,
                refresh_token=jwt_tokens.refresh_token,
                access_token=jwt_tokens.access_token
            )
