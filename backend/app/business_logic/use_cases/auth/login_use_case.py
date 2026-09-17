import random
from app.business_logic.auth.password_manager import PasswordManager
from app.business_logic.exceptions import CheckPswError, VerifyCodeStorageError
from app.business_logic.unit_of_work import UnitOfWork
from app.business_logic.use_cases.interface.iuse_case import IUseCase
from app.shared.config import AppMode
from app.shared.dtos import UserDtoGetResponse
from app.shared.dtos.auth import LoginDtoRequest
from app.data_access.database.repositories import UserRepository
from app.shared.dtos.user import UserDtoGetResponseWithCode
from app.shared.log_config import LogMixin
from app.shared.dtos import AuditPostDto
from app.business_logic.cache.verify_code_storage import VerifyCodeStorage
from app.business_logic.decorators import audit_system
from app.shared.dtos.auth import SendType
from app.business_logic.celery_tasks.sender_tasks import send_message


class LoginUseCase(IUseCase, LogMixin):
    """Use case для входа в систему"""
    def __init__(
            self,
            uow: UnitOfWork,
            verify_code_storage: VerifyCodeStorage,
            psw_manager: type[PasswordManager],
            dto_audit: AuditPostDto,
            app_mode: AppMode
    ):
        self.uow = uow
        self.psw_manager = psw_manager
        self.dto_audit = dto_audit
        self.verify_code_storage = verify_code_storage
        self.app_mode = app_mode

    @audit_system
    def execute(
            self, *,
            dto_request_data: LoginDtoRequest,
            send_type: SendType
    ) -> UserDtoGetResponse:
        with self.uow as uow:
            user_repo = uow.get_repository(UserRepository)
            user_info: UserDtoGetResponse = user_repo.get_by_id(dto_request_data.user_id)
            self.log_debug(f'Получена информация о пользователе {dto_request_data.user_id} из бд')
            user_password: bytes = user_repo.get_hash_psw(dto_request_data.user_id)
            self.log_debug(f'Получен хеш введенного пароля для пользователя {dto_request_data.user_id}')
            if not self.psw_manager.check_equal_psw(
                    dto_request_data.password,
                    user_password
            ):
                exc = CheckPswError(dto_request_data.user_id)
                self.log_error(exc.message)
                raise exc
            new_code = random.randint(10000, 99999)
            is_code_save = self.verify_code_storage.save(user_info.id, new_code)
            if not is_code_save:
                raise VerifyCodeStorageError()
            self.log_info(f'Вход для пользователя {user_info.id} выполнен успешно')
            to = user_info.get_contact_details(send_type)
            if self.app_mode == AppMode.DEV:
                return UserDtoGetResponseWithCode(
                    **user_info.model_dump(),
                    code=new_code
                )
            result = send_message.delay(to=to, msg=f'Код подтверждения: {new_code}', send_type=send_type)
            self.log_debug(f'UUID задачи отправки кода: {result.id}, статус: {result.status}')
            return user_info