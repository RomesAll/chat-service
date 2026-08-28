from app.business_logic.unit_of_work import UnitOfWork
from app.business_logic.use_cases.interface.iuse_case import IUseCase
from app.shared.dtos import UserDtoGetResponse, UserDtoUpdateRequest
from app.data_access.database.repositories import UserRepository


class UpdateUser(IUseCase):
    """Use case для обновления пользователей"""
    def __init__(
            self,
            uow: UnitOfWork
    ):
        self.uow = uow

    def execute(self, dto_user: UserDtoUpdateRequest) -> UserDtoGetResponse:
        with self.uow as uow:
            repo = uow.get_repository(UserRepository)
            return repo.update(dto_user)