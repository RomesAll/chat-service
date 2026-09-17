from uuid import UUID

from app.business_logic.decorators import audit_system
from app.business_logic.unit_of_work import UnitOfWork
from app.business_logic.use_cases.interface.iuse_case import IUseCase
from app.data_access.database.models.user import RoleEnum
from app.shared.dtos import UserInRoomResponse, JWTBaseToken, AuditPostDto
from app.data_access.database.repositories.room import UserInRoomRepository
from app.shared.log_config import LogMixin
from app.business_logic.exceptions import UserNotFoundInRoom


class GetUserInRoomUseCase(IUseCase, LogMixin):
    """Use case для получения информации о пользователей в комнате"""
    def __init__(
            self,
            uow: UnitOfWork,
            dto_audit: AuditPostDto
    ):
        self.uow = uow
        self.dto_audit = dto_audit

    @audit_system
    def execute(self, room_id: UUID, user_token_info: JWTBaseToken) -> list[str]:
        with self.uow as uow:
            user_in_room_repo = uow.get_repository(UserInRoomRepository)
            is_user_in_room = user_in_room_repo.check_exist_user_in_room(
                user_token_info.user_id, room_id
            )
            role = user_token_info.role
            if role == RoleEnum.DEFAULT_USER and not is_user_in_room:
                exc = UserNotFoundInRoom(user_token_info.user_id, room_id)
                self.log_error(exc.message)
                raise exc
            users_in_room = user_in_room_repo.get_users_in_room(room_id)
            users_id = [users.user_id for users in users_in_room]
            self.log_debug(f'Получена информация пользователях в комнате')
            return users_id