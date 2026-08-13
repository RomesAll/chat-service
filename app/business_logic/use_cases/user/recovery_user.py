from business_logic.unit_of_work import UnitOfWork
from business_logic.use_cases.interface.iuse_case import IUseCase
from app.shared.dtos import UserDtoGetResponse, UserDtoDeleteRequest
from repositories import UserRepository


class RecoveryUser(IUseCase):
    def __init__(
            self,
            uow: UnitOfWork
    ):
        self.uow = uow

    def execute(self, user_id: str) -> UserDtoGetResponse:
        with self.uow as uow:
            repo = uow.get_repository(UserRepository)
            return repo.recovery(user_id)