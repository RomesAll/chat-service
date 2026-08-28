from app.business_logic.unit_of_work import UnitOfWork
from app.business_logic.use_cases.interface.iuse_case import IUseCase
from app.data_access.database.repositories.message import PrivateMessageRepository
from app.shared.dtos import MessageDtoGetResponse


class GetPrivateMsgAndSave(IUseCase):
    """Use case для получения сообщений с пользователем"""
    def __init__(self, uow: UnitOfWork):
        self.uow = uow

    def execute(
            self,
            user_id_who: str,
            user_id_whom: str
    ) -> list[MessageDtoGetResponse]:
        with self.uow as uow:
            private_msg_repo = uow.get_repository(PrivateMessageRepository)
            return private_msg_repo.get_message_by_user(user_id_who, user_id_whom)