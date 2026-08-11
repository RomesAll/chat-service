import bcrypt
from pydantic import SecretStr
from business_logic.active_session.active_session_manager import ActiveSessionManager
from business_logic.unit_of_work import UnitOfWork
from business_logic.use_cases.interface.iuse_case import IUseCase, check_request_data_exist
from app.shared.dtos import UserDtoPostRequest, UserDtoGetResponse, ActionType
from database import db
from repositories import UserRepository


class RegisterUser(IUseCase):
    def __init__(
            self,
            dto_request_data: UserDtoPostRequest,
            action_type: ActionType,
            active_session_manager: ActiveSessionManager
    ):
        super().__init__(dto_request_data, action_type, active_session_manager)

    @check_request_data_exist
    def execute(self) -> UserDtoGetResponse:
        with UnitOfWork(db) as uow:
            repo = uow.get_repository(UserRepository)
            salt = bcrypt.gensalt()
            hashed_psw = bcrypt.hashpw(
                self.dto_request_data.password.get_secret_value().encode(), # type: ignore
                salt
            )
            self.dto_request_data.password = SecretStr(hashed_psw.decode())
            self.dto_request_data.repeat_password = SecretStr(hashed_psw.decode())
            return repo.save(self.dto_request_data)