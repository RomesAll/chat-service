from business_logic.active_session.active_session_manager import ActiveSessionManager
from business_logic.active_session.route_message import RouteMessage
from business_logic.unit_of_work import UnitOfWork
from business_logic.use_cases.interface.iuse_case import IUseCase, check_request_data_exist
from database import db
from repositories.message import GroupMessageRepository
from app.shared.dtos import GroupMessageDtoPostRequest, ActionType, GroupMessageDtoGetResponse


class SendGroupMsgAndSave(IUseCase):
    def __init__(
            self,
            dto_request_data: GroupMessageDtoPostRequest,
            action_type: ActionType,
            active_session_manager: ActiveSessionManager
    ):
        super().__init__(dto_request_data, action_type, active_session_manager)

    @check_request_data_exist
    async def execute(self) -> GroupMessageDtoGetResponse:
        with UnitOfWork(db) as uow:
            group_msg_repo = uow.get_repository(GroupMessageRepository)
            dto_response = group_msg_repo.save(self.dto_request_data)
            await RouteMessage(self.active_session_manager).routing_message(self.dto_request_data)
            return dto_response