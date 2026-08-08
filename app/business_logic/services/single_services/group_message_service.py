from business_logic.services.base.base_service import BaseService
from repositories.message import GroupMessageRepository
from shared.dtos.base import BaseDtoOrmRecord
from shared.dtos.message import GroupMessageDtoGetResponse, GroupMessageDtoPostRequest


class GroupMessageService(
    BaseService[BaseDtoOrmRecord, GroupMessageDtoGetResponse, GroupMessageDtoPostRequest]
):
    def __init__(
            self,
            repository: type[GroupMessageRepository]
    ):
        super().__init__(repository)