from business_logic.services.base.base_service import BaseService
from repositories.user import UserRepository
from shared.dtos.base import BaseDtoOrmRecord
from shared.dtos.user import UserDtoGetResponse, UserDtoPostRequest


class UserService(
    BaseService[BaseDtoOrmRecord, UserDtoGetResponse, UserDtoPostRequest]
):
    def __init__(
            self,
            repository: type[UserRepository]
    ):
        super().__init__(repository)