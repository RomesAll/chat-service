from business_logic.unit_of_work import UnitOfWork
from business_logic.use_cases.interface.iuse_case import IUseCase
from app.shared.dtos import RoomDtoGetResponse, RoomDtoPostRequest
from repositories import RoomRepository


class CreateRoom(IUseCase):
    def __init__(
            self,
            uow: UnitOfWork
    ):
        self.uow = uow

    def execute(self, dto_room: RoomDtoPostRequest) -> RoomDtoGetResponse:
        with self.uow as uow:
            repo = uow.get_repository(RoomRepository)
            return repo.save(dto_room)