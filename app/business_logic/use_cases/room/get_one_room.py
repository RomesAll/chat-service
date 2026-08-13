from uuid import UUID

from business_logic.unit_of_work import UnitOfWork
from business_logic.use_cases.interface.iuse_case import IUseCase
from repositories import RoomRepository
from app.shared.dtos import RoomDtoGetResponse


class GetOneRoom(IUseCase):
    def __init__(
            self,
            uow: UnitOfWork
    ):
        self.uow = uow

    async def execute(self, record_id: UUID) -> RoomDtoGetResponse:
        with self.uow as uow:
            repo = uow.get_repository(RoomRepository)
            dto_response = repo.get_by_id(record_id)
            return dto_response