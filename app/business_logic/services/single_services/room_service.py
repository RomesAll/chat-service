from business_logic.services.base.base_service import BaseService
from repositories.room import RoomRepository
from shared.dtos.base import BaseDtoOrmRecord
from shared.dtos.room import RoomDtoGetResponse, RoomDtoPostRequest


class RoomService(
    BaseService[BaseDtoOrmRecord, RoomDtoGetResponse, RoomDtoPostRequest]
):
    def __init__(
            self,
            repository: type[RoomRepository]
    ):
        super().__init__(repository)