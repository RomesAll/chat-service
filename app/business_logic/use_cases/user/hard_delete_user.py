from business_logic.unit_of_work import UnitOfWork
from business_logic.use_cases.interface.iuse_case import IUseCase
from repositories import UserRepository


class HardDeleteUser(IUseCase):
    """Use case для удаления пользователей"""
    def __init__(
            self,
            uow: UnitOfWork
    ):
        self.uow = uow

    def execute(self, user_id: str) -> str:
        with self.uow as uow:
            repo = uow.get_repository(UserRepository)
            return repo.hard_delete(user_id)