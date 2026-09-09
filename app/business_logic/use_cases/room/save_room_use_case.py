from app.business_logic.unit_of_work import UnitOfWork
from app.business_logic.use_cases.interface.iuse_case import IUseCase
from app.shared.dtos import RoomDtoPostRequest, RoomDtoGetResponse, AuditPostDto
from app.data_access.database.repositories.room import RoomRepository
from business_logic.decorators import audit_system
from app.shared.log_config import LogMixin


class SaveRoomUseCase(IUseCase, LogMixin):
    """Use case для создания новой комнаты"""
    def __init__(
            self,
            uow: UnitOfWork,
            dto_audit: AuditPostDto
    ):
        self.uow = uow
        self.dto_audit = dto_audit

    @audit_system
    def execute(self, dto_request: RoomDtoPostRequest) -> RoomDtoGetResponse:
        with self.uow as uow:
            room_repo = uow.get_repository(RoomRepository)
            result = room_repo.save(dto_request)
            self.log_info(f'Информация о комнате с id {result.id} сохранена')
            return result