from business_logic.unit_of_work import UnitOfWork
from business_logic.use_cases.interface.iuse_case import IUseCase
from repositories import UserRepository
from app.shared.dtos import BaseDtoGetListRequest, UserDtoGetResponse


class GetUsers(IUseCase):
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