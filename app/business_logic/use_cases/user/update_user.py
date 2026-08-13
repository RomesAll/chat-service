from business_logic.unit_of_work import UnitOfWork
from business_logic.use_cases.interface.iuse_case import IUseCase
from app.shared.dtos import UserDtoGetResponse, UserDtoUpdateRequest
from repositories import UserRepository
from database import db


class UpdateUser(IUseCase):
    """Use case для обновления пользователей"""
    def __init__(
            self,
            uow: UnitOfWork
    ):
        self.uow = uow

    def execute(self, dto_user: UserDtoUpdateRequest) -> UserDtoGetResponse:
        with UnitOfWork(db) as uow:
            repo = uow.get_repository(UserRepository)
            return repo.update(dto_user)