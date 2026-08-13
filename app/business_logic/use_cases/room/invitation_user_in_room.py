from business_logic.active_session.active_session_manager import ActiveSessionManager
from business_logic.unit_of_work import UnitOfWork
from business_logic.use_cases.interface.iuse_case import IUseCase
from app.shared.dtos import InvitationUserInRoomDtoRequest, ActiveSession
from repositories import RoomRepository, UserRepository
from repositories.room import UserInRoomRepository


class InvitationUserInRoom(IUseCase):
    def __init__(
            self,
            uow: UnitOfWork,
            active_session_manager: ActiveSessionManager
    ):
        self.uow = uow
        self.active_session_manager = active_session_manager

    def execute(self, inv_user: InvitationUserInRoomDtoRequest):
        with self.uow as uow:
            room_repo = uow.get_repository(RoomRepository)
            user_repo = uow.get_repository(UserRepository)
            user_in_room = uow.get_repository(UserInRoomRepository)
            if not room_repo.check_exist(inv_user.room_id):
                raise Exception
            if not user_repo.check_exist(inv_user.user_id):
                raise Exception
            user_active_session: ActiveSession = self.active_session_manager.get_or_create_session(
                user_id=inv_user.user_id
            )
            for connection in user_active_session.websockets:
                self.active_session_manager.add_connection_in_room(
                    inv_user.room_id,
                    connection
                )
            user_in_room.save(inv_user)