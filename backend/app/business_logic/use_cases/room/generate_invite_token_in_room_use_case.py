from typing import Any

from app.business_logic.exceptions import GenerateInviteTokenOnlyOwner
from app.business_logic.invite_url_generate_service import InviteUrlGenerateService
from app.business_logic.unit_of_work import UnitOfWork
from app.business_logic.use_cases.interface.iuse_case import IUseCase
from app.data_access.database.repositories import RoomRepository
from app.shared.dtos import AuditPostDto
from app.shared.dtos.room import GenerateUrlInviteRoomRequest
from app.shared.log_config import LogMixin
from app.business_logic.decorators import audit_system


class GenerateInviteTokenInRoomUseCase(IUseCase, LogMixin):
    """Use case для генерации ссылки вступления в комнату"""
    def __init__(
            self,
            uow: UnitOfWork,
            dto_audit: AuditPostDto,
            invite_url_service: InviteUrlGenerateService
    ):
        self.uow = uow
        self.dto_audit = dto_audit
        self.invite_url_service = invite_url_service

    @audit_system
    def execute(self, dto_request: GenerateUrlInviteRoomRequest) -> tuple[str, Any]:
        with self.uow as uow:
            room_repo = uow.get_repository(RoomRepository)
            room_info = room_repo.get_by_id(dto_request.room_id)
            if room_info.owner != dto_request.created_by:
                raise GenerateInviteTokenOnlyOwner(dto_request.created_by, room_info.id, room_info.name)
            token, exp = self.invite_url_service.generate_url(
                **dto_request.model_dump()
            )
            self.log_debug(f'Url токен для вступления в комнату {dto_request.room_id} '
                           f'был создан пользователем {dto_request.created_by}')
            return token, exp