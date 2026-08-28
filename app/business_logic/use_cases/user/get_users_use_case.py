from app.business_logic.unit_of_work import UnitOfWork
from app.business_logic.use_cases.interface.iuse_case import IUseCase
from app.data_access.database.repositories import UserRepository
from app.shared.dtos import BaseDtoGetListRequest, UserDtoGetResponse


class GetUsers(IUseCase):
    """Use case для получения всех пользователей"""
    def __init__(
            self,
            uow: UnitOfWork
    ):
        self.uow = uow

    def execute(self, dto_user: BaseDtoGetListRequest) -> list[UserDtoGetResponse]:
        with self.uow as uow:
            group_msg_repo = uow.get_repository(UserRepository)
            dto_response = group_msg_repo.get(dto_user)
            return dto_response