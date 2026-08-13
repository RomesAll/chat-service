from business_logic.unit_of_work import UnitOfWork
from business_logic.use_cases.interface.iuse_case import IUseCase
from database import db
from dtos import BaseDtoGetListRequest
from repositories import UserRepository
from app.shared.dtos import RoomDtoGetResponse


class GetRooms(IUseCase):
    """Use case для получения комнат"""
    def __init__(
            self,
            uow: UnitOfWork
    ):
        self.uow = uow

    async def execute(self, dto_room: BaseDtoGetListRequest) -> list[RoomDtoGetResponse]:
        with UnitOfWork(db) as uow:
            repo = uow.get_repository(UserRepository)
            dto_response = repo.get(dto_room)
            return dto_response