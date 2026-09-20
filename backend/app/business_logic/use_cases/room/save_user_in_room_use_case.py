from fastapi import HTTPException
from starlette import status
from app.business_logic.invite_url_generate_service import InviteUrlGenerateService
from app.business_logic.unit_of_work import UnitOfWork
from app.business_logic.use_cases.interface.iuse_case import IUseCase
from app.shared.dtos import UserInRoomPostRequest, UserInRoomResponse, AuditPostDto
from app.data_access.database.repositories import UserRepository
from app.data_access.database.repositories.room import UserInRoomRepository, RoomRepository
from app.shared.log_config import LogMixin
from app.business_logic.decorators import audit_system
from app.business_logic.exceptions import RoomNotFound, UserNotFoundError


class SaveUserInRoomUseCase(IUseCase, LogMixin):
    """Use case для добавления пользователя в комнату"""
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
    def execute(self, user_id: str, token: str) -> UserInRoomResponse:
        with self.uow as uow:
            doc_id, room_id = self.invite_url_service.check_token_invite_exist(token)
            room_repo = uow.get_repository(RoomRepository)
            user_in_room_repo = uow.get_repository(UserInRoomRepository)
            user_repo = uow.get_repository(UserRepository)
            if not room_repo.check_exist(room_id):
                exc = RoomNotFound(room_id)
                self.log_error(exc.message)
                raise exc
            if not user_repo.check_exist(user_id):
                exc = UserNotFoundError(user_id)
                self.log_error(exc.message)
                raise exc
            users_in_room = user_in_room_repo.get_users_in_room(room_id)
            if user_id in users_in_room:
                raise HTTPException(
                    status_code=status.HTTP_409_CONFLICT,
                    detail=f'Пользователь {user_id} уже есть в группе {room_id}'
                )
            result = user_in_room_repo.save(UserInRoomPostRequest(
                user_id=user_id,
                room_id=room_id
            ))
            self.invite_url_service.increment_uses_count(doc_id)
            self.log_info(f'Пользователь {user_id} добавлен в комнату {room_id}')
            return result