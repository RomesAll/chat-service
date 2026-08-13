from business_logic.unit_of_work import UnitOfWork
from business_logic.use_cases.interface.iuse_case import IUseCase
from app.shared.dtos import RoomDtoUpdateRequest, RoomDtoGetResponse
from repositories import RoomRepository


class UpdateRoom(IUseCase):
    def __init__(
            self,
            uow: UnitOfWork
    ):
        self.uow = uow

    def execute(self, dto_room: RoomDtoUpdateRequest) -> RoomDtoGetResponse:
        with self.uow as uow:
            repo = uow.get_repository(RoomRepository)
            return repo.update(dto_room)