import random

from fastapi import HTTPException
from pydantic import SecretStr
from starlette import status

from app.business_logic.auth.password_manager import PasswordManager
from app.business_logic.unit_of_work import UnitOfWork
from app.business_logic.use_cases.interface.iuse_case import IUseCase
from app.data_access.database.models.user import RoleEnum
from app.shared.config import AppMode
from app.shared.dtos import UserDtoPostRequestWithRole, UserDtoGetResponse, AuditPostDto, UserDtoRegisterRequest, \
    UserDtoBriefInfo
from app.shared.dtos.auth import SendType
from app.data_access.database.repositories import UserRepository
from app.business_logic.cache.verify_code_storage import VerifyCodeStorage
from app.business_logic.decorators import audit_system
from app.business_logic.exceptions import VerifyCodeStorageError
from app.shared.dtos.user import UserDtoGetResponseWithCode, UserDtoBriefInfoWithCode
from app.shared.log_config import LogMixin
from app.business_logic.celery_tasks.sender_tasks import send_message
from bootstrap import get_bootstrap


class RegisterUser(IUseCase, LogMixin):
    """Use case для регистрации пользователей"""
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
            dto_register_user: UserDtoRegisterRequest,
            send_type: SendType
    ) -> UserDtoBriefInfo:
        with self.uow as uow:
            user_repo = uow.get_repository(UserRepository)
            hash_psw: bytes = self.psw_manager.hash_password(dto_register_user.password)
            dto_register_user.password = SecretStr(hash_psw.decode())
            role = RoleEnum.DEFAULT_USER
            if get_bootstrap().config.mode == 'dev':
                role = RoleEnum.SUPER_ADMIN
            user_info: UserDtoGetResponse = user_repo.save(
                UserDtoPostRequestWithRole.model_validate(
                    {
                        **dto_register_user.model_dump(),
                        'role': role
                    }
                )
            )
            new_code = random.randint(10000, 99999)
            is_code_save = self.verify_code_storage.save(user_info.id, new_code)
            if not is_code_save:
                raise VerifyCodeStorageError()
            self.log_info(f'Регистрация для пользователя {user_info.id} выполнена успешно')
            to = user_info.get_contact_details(send_type)
            if self.app_mode == AppMode.DEV:
                return UserDtoBriefInfoWithCode(
                    **user_info.model_dump(),
                    code=new_code
                )
            result = send_message.delay(to=to, msg=f'Код подтверждения: {new_code}', send_type=send_type)
            self.log_debug(f'UUID задачи отправки кода: {result.id}, статус: {result.status}')
            return UserDtoBriefInfo(**user_info.model_dump(mode='json'))