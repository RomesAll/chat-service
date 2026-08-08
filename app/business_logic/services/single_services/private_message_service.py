from business_logic.services.base.base_service import BaseService
from repositories.message import PrivateMessageRepository
from shared.dtos.base import BaseDtoOrmRecord
from shared.dtos.message import PrivateMessageDtoGetResponse, PrivateMessageDtoPostRequest


class PrivateMessageService(
    BaseService[BaseDtoOrmRecord, PrivateMessageDtoGetResponse, PrivateMessageDtoPostRequest]
):
    def __init__(
            self,
            repository: type[PrivateMessageRepository]
    ):
        super().__init__(repository)