from app.business_logic.unit_of_work import UnitOfWork
from app.business_logic.use_cases.interface.iuse_case import IUseCase
from app.data_access.database.repositories import UserRepository


class SoftDeleteUser(IUseCase):
    """Use case для мягкого удаления пользователей"""
    def __init__(
            self,
            uow: UnitOfWork
    ):
        self.uow = uow

    def execute(self, user_id: str) -> str:
        with self.uow as uow:
            repo = uow.get_repository(UserRepository)
            return repo.soft_delete(user_id)