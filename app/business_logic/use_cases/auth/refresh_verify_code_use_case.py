from app.business_logic.use_cases.interface.iuse_case import IUseCase
from app.shared.log_config import LogMixin
from app.business_logic.cache.verify_code_storage import VerifyCodeStorage
from app.shared.dtos.auth import RefreshVerifyCodeRequest
from app.business_logic.decorators import audit_system
from app.shared.dtos.user import UserDtoGetResponse
from app.shared.dtos import AuditPostDto
from app.business_logic.unit_of_work import UnitOfWork
from app.data_access.database.repositories import UserRepository
from app.business_logic.sender_service import ISender
from app.shared.dtos.auth import SendType
from app.business_logic.exceptions import VerifyCodeStorageError
import random


class RefreshVerifyCodeUseCase(IUseCase, LogMixin):
    """Use case для обновления кода подтверждения"""
    def __init__(
            self,
            uow: UnitOfWork,
            dto_audit: AuditPostDto,
            verify_code_storage: VerifyCodeStorage,
            sender_service: ISender
    ):
        self.uow = uow
        self.verify_code_storage = verify_code_storage
        self.dto_audit = dto_audit
        self.sender_service = sender_service

    @audit_system
    def execute(
            self,
            request: RefreshVerifyCodeRequest,
            send_type: SendType
    ) -> UserDtoGetResponse:
        with self.uow as uow:
            user_repo = uow.get_repository(UserRepository)
            user_info: UserDtoGetResponse = user_repo.get_by_id(
                request.user_id
            )
            self.log_debug(f'Получена информация о пользователе {request.user_id} из бд')
            new_code = random.randint(10000, 99999)
            is_code_save = self.verify_code_storage.save(user_info.id, user_info.email, new_code)
            if not is_code_save:
                raise VerifyCodeStorageError()
            if not (to := user_info.get_contact_details(send_type)):
                raise Exception
            self.sender_service.send_message(to=to, msg_send=f'Код подтверждения: {new_code}')
            return user_info