from uuid import UUID
from business_logic.unit_of_work import UnitOfWork
from business_logic.use_cases.interface.iuse_case import IUseCase
from repositories import RoomRepository


class HardDeleteRoom(IUseCase):
    def __init__(
            self,
            uow: UnitOfWork
    ):
        self.uow = uow

    def execute(self, record_id: UUID) -> UUID:
        with self.uow as uow:
            repo = uow.get_repository(RoomRepository)
            return repo.hard_delete(record_id)