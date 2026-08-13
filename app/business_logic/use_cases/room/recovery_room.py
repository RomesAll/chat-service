from uuid import UUID
from business_logic.unit_of_work import UnitOfWork
from business_logic.use_cases.interface.iuse_case import IUseCase
from app.shared.dtos import RoomDtoGetResponse
from repositories import RoomRepository


class RecoveryRoom(IUseCase):
    """Use case для восстановления комнаты"""
    def __init__(
            self,
            uow: UnitOfWork
    ):
        self.uow = uow

    def execute(self, record_id: UUID) -> RoomDtoGetResponse:
        with self.uow as uow:
            repo = uow.get_repository(RoomRepository)
            return repo.recovery(record_id)