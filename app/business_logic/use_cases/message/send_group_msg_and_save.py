from business_logic.active_session.route_message import RouteMessage
from business_logic.unit_of_work import UnitOfWork
from business_logic.use_cases.interface.iuse_case import IUseCase
from repositories.message import GroupMessageRepository
from app.shared.dtos import GroupMessageDtoPostRequest, GroupMessageDtoGetResponse


class SendGroupMsgAndSave(IUseCase):
    """Use case для отправки сообщений в комнату"""
    def __init__(
            self,
            uow: UnitOfWork,
            route_message: RouteMessage
    ):
        self.uow = uow
        self.route_message = route_message

    async def execute(self, dto_group_msg: GroupMessageDtoPostRequest) -> GroupMessageDtoGetResponse:
        with self.uow as uow:
            group_msg_repo = uow.get_repository(GroupMessageRepository)
            dto_response = group_msg_repo.save(dto_group_msg)
            await self.route_message.routing_message(dto_group_msg)
            return dto_response