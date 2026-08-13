from business_logic.active_session.route_message import RouteMessage
from business_logic.unit_of_work import UnitOfWork
from business_logic.use_cases.interface.iuse_case import IUseCase
from repositories.message import PrivateMessageRepository
from app.shared.dtos import PrivateMessageDtoPostRequest, PrivateMessageDtoGetResponse


class SendPrivateMsgAndSave(IUseCase):
    def __init__(
            self,
            uow: UnitOfWork,
            route_message: RouteMessage
    ):
        self.uow = uow
        self.route_message = route_message

    async def execute(self, dto_private_msg: PrivateMessageDtoPostRequest) -> PrivateMessageDtoGetResponse:
        with self.uow as uow:
            private_msg_repo = uow.get_repository(PrivateMessageRepository)
            dto_response: PrivateMessageDtoGetResponse = private_msg_repo.save(dto_private_msg)
            await self.route_message.routing_message(dto_private_msg)
            return dto_response