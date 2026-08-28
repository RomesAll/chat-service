from app.business_logic.unit_of_work import UnitOfWork
from app.business_logic.use_cases.interface.iuse_case import IUseCase
from app.shared.dtos import RoomDtoPostRequest, RoomDtoGetResponse
from app.data_access.database.repositories.room import RoomRepository


class SaveRoomUseCase(IUseCase):
    """Use case для создания новой комнаты"""
    def __init__(
            self,
            uow: UnitOfWork,
    ):
        self.uow = uow

    def execute(self, dto_request: RoomDtoPostRequest) -> RoomDtoGetResponse:
        with self.uow as uow:
            room_repo = uow.get_repository(RoomRepository)
            return room_repo.save(dto_request)