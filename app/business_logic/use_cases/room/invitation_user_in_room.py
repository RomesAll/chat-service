from business_logic.active_session.active_session_manager import ActiveSessionManager
from business_logic.unit_of_work import UnitOfWork
from business_logic.use_cases.interface.iuse_case import IUseCase, check_request_data_exist
from app.shared.dtos import ActionType, InvitationUserInRoomDtoRequest, ActiveSession
from database import db
from repositories import RoomRepository, UserRepository


class InvitationUserInRoom(IUseCase):
    def __init__(
            self,
            dto_request_data: InvitationUserInRoomDtoRequest,
            action_type: ActionType,
            active_session_manager: ActiveSessionManager
    ):
        super().__init__(dto_request_data, action_type, active_session_manager)

    @check_request_data_exist
    def execute(self) -> None:
        with UnitOfWork(db) as uow:
            room_repo = uow.get_repository(RoomRepository)
            user_repo = uow.get_repository(UserRepository)
            if not room_repo.check_exist(self.dto_request_data.room_id):
                raise Exception
            if not user_repo.check_exist(self.dto_request_data.user_id):
                raise Exception
            user_active_session: ActiveSession = self.active_session_manager.get_or_create_session(
                user_id=self.dto_request_data.user_id
            )
            for connection in user_active_session.websockets:
                self.active_session_manager.add_connection_in_room(
                    self.dto_request_data.room_id,
                    connection
                )