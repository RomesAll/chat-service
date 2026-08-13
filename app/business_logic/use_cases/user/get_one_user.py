from business_logic.unit_of_work import UnitOfWork
from business_logic.use_cases.interface.iuse_case import IUseCase
from repositories import UserRepository
from app.shared.dtos import UserDtoGetResponse


class GetOneUsers(IUseCase):
    def __init__(
            self,
            uow: UnitOfWork
    ):
        self.uow = uow

    def execute(self, user_id: str) -> UserDtoGetResponse:
        with self.uow as uow:
            group_msg_repo = uow.get_repository(UserRepository)
            dto_response = group_msg_repo.get_by_id(user_id)
            return dto_response