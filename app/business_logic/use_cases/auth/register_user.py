from pydantic import SecretStr
from business_logic.auth.jwt_manager import JWTFacade
from business_logic.auth.password_manager import PasswordManager
from business_logic.unit_of_work import UnitOfWork
from business_logic.use_cases.interface.iuse_case import IUseCase
from dtos import UserDtoPostRequest, UserDtoGetResponse
from dtos.auth import LoginOrRegisterDtoResponse
from repositories import UserRepository


class RegisterUser(IUseCase):

    def __init__(
            self,
            uow: UnitOfWork,
            psw_manager: type[PasswordManager],
            jwt_manager: type[JWTFacade]
    ):
        self.uow = uow
        self.psw_manager = psw_manager
        self.jwt_manager = jwt_manager

    def execute(self, dto_register_user: UserDtoPostRequest) -> LoginOrRegisterDtoResponse:
        with self.uow as uow:
            user_repo = uow.get_repository(UserRepository)
            hash_psw: bytes = self.psw_manager.hash_password(dto_register_user.password)
            dto_register_user.password = SecretStr(hash_psw.decode())
            user_info: UserDtoGetResponse = user_repo.save(dto_register_user)
            tokens = self.jwt_manager.create_tokens(user_info.id, user_info.user_name, user_info.role)
            return LoginOrRegisterDtoResponse(
                user_info=user_info,
                access_token=tokens.access_token,
                refresh_token=tokens.refresh_token
            )