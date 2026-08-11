from abc import ABC, abstractmethod
from typing import TYPE_CHECKING
from business_logic.active_session.active_session_manager import ActiveSessionManager

if TYPE_CHECKING:
    from app.shared.dtos import BaseDtoClientRequest, ActionType, BaseDtoGetListRequest, InvitationUserInRoomDtoRequest

def check_request_data_exist(func):
    def wrapper(self: IUseCase):
        if not self.dto_request_data:
            raise Exception
        return func(self)
    return wrapper


class IUseCase(ABC):
    def __init__(
            self,
            dto_request_data: 'BaseDtoClientRequest | BaseDtoGetListRequest | InvitationUserInRoomDtoRequest',
            action_type: 'ActionType',
            active_session_manager: ActiveSessionManager
    ):
        self.dto_request_data = dto_request_data
        self.action_type = action_type
        self.active_session_manager = active_session_manager

    @abstractmethod
    async def execute(self) -> 'BaseDtoClientRequest | None':
        pass