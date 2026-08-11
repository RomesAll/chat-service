from business_logic.active_session.active_session_manager import ActiveSessionManager
from business_logic.active_session.route_message import RouteMessage
from business_logic.use_cases.interface.iuse_case import IUseCase, check_request_data_exist
from app.shared.dtos import GroupMessageDtoPostRequest, ActionType


class SendGroupMsgAutoDelete(IUseCase):
    def __init__(
            self,
            dto_request_data: GroupMessageDtoPostRequest,
            action_type: ActionType,
            active_session_manager: ActiveSessionManager
    ):
        super().__init__(dto_request_data, action_type, active_session_manager)

    @check_request_data_exist
    async def execute(self) -> None:
        await RouteMessage(self.active_session_manager).routing_message(self.dto_request_data)