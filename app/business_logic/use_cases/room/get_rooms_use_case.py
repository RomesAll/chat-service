from app.business_logic.unit_of_work import UnitOfWork
from app.business_logic.use_cases.interface.iuse_case import IUseCase
from app.shared.dtos import RoomDtoGetResponse, BaseDtoGetListRequest
from app.data_access.database.repositories.room import RoomRepository
from log_config import LogMixin


class GetRoomsUseCase(IUseCase, LogMixin):
    """Use case для получения информации о комнатах"""
    def __init__(
            self,
            uow: UnitOfWork
    ):
        self.uow = uow

    def execute(self, request: BaseDtoGetListRequest) -> list[RoomDtoGetResponse]:
        room_repo = self.uow.get_repository(RoomRepository)
        result = room_repo.get(request)
        self.log_debug('Поучена информация о комнатах')
        return result