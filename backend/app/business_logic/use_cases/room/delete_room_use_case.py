from typing import Any
from uuid import UUID
from app.business_logic.decorators import audit_system
from app.business_logic.exceptions import RoomDeleteForbidden
from app.business_logic.unit_of_work import UnitOfWork
from app.business_logic.use_cases.interface.iuse_case import IUseCase
from app.data_access.database.models.user import RoleEnum
from app.shared.dtos import JWTBaseToken, AuditPostDto
from app.data_access.database.repositories.room import RoomRepository
from app.shared.log_config import LogMixin


class DeleteRoomUseCase(IUseCase, LogMixin):
    """Use case для удаления информации о комнате"""
    def __init__(
            self,
            uow: UnitOfWork,
            dto_audit: AuditPostDto
    ):
        self.uow = uow
        self.dto_audit = dto_audit

    @audit_system
    def execute(self, room_id: UUID, user_token_info: JWTBaseToken) -> Any:
        with self.uow as uow:
            room_repo = uow.get_repository(RoomRepository)
            room_info = room_repo.get_by_id(room_id)
            if user_token_info.role == RoleEnum.DEFAULT_USER \
                    and room_info.owner != user_token_info.user_id:
                raise RoomDeleteForbidden(room_id)
            return room_repo.hard_delete(room_id)