from business_logic.active_session.active_session_manager import ActiveSessionManager
from business_logic.unit_of_work import UnitOfWork
from business_logic.use_cases.interface.iuse_case import IUseCase, check_request_data_exist
from database import db
from repositories import UserRepository
from app.shared.dtos import BaseDtoGetListRequest, ActionType, RoomDtoGetResponse


class GetRooms(IUseCase):
    def __init__(
            self,
            dto_request_data: BaseDtoGetListRequest,
            action_type: ActionType,
            active_session_manager: ActiveSessionManager
    ):
        super().__init__(dto_request_data, action_type, active_session_manager)

    @check_request_data_exist
    async def execute(self) -> list[RoomDtoGetResponse]:
        with UnitOfWork(db) as uow:
            repo = uow.get_repository(UserRepository)
            dto_response = repo.get(self.dto_request_data)
            return dto_response