from app.business_logic.unit_of_work import UnitOfWork
from app.business_logic.use_cases.interface.iuse_case import IUseCase
from app.shared.dtos import UserInRoomPostRequest, UserInRoomResponse, AuditPostDto
from app.data_access.database.repositories import UserRepository
from app.data_access.database.repositories.room import UserInRoomRepository, RoomRepository
from app.shared.log_config import LogMixin
from business_logic.decorators import audit_system
from business_logic.exceptions import RoomNotFound, UserNotFoundError


class SaveUserInRoomUseCase(IUseCase, LogMixin):
    """Use case для добавления пользователя в комнату"""
    def __init__(
            self,
            uow: UnitOfWork,
            dto_audit: AuditPostDto
    ):
        self.uow = uow
        self.dto_audit = dto_audit

    @audit_system
    def execute(self, dto_request: UserInRoomPostRequest) -> UserInRoomResponse:
        with self.uow as uow:
            room_repo = uow.get_repository(RoomRepository)
            user_in_room_repo = uow.get_repository(UserInRoomRepository)
            user_repo = uow.get_repository(UserRepository)
            if not room_repo.check_exist(dto_request.room_id):
                exc = RoomNotFound(dto_request.room_id)
                self.log_error(exc.message)
                raise exc
            if not user_repo.check_exist(dto_request.user_id):
                exc = UserNotFoundError(dto_request.user_id)
                self.log_error(exc.message)
                raise exc
            result = user_in_room_repo.save(dto_request)
            self.log_info(f'Пользователь {dto_request.user_id} добавлен в комнату {dto_request.room_id}')
            return result