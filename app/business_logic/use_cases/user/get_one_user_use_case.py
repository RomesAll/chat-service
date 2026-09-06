from typing import Self
from app.business_logic.unit_of_work import UnitOfWork
from app.business_logic.use_cases.interface.iuse_case import IUseCase
from app.shared.dtos import UserDtoBriefInfo
from app.data_access.database.repositories import UserRepository
from app.shared.log_config import LogMixin


class GetOneUsers(IUseCase, LogMixin):
    """Use case для получения пользователя"""
    def __init__(
            self,
            uow: UnitOfWork
    ):
        self.uow = uow
        self.dto_response = None

    def execute(self, user_id: str) -> Self:
        with self.uow as uow:
            group_msg_repo = uow.get_repository(UserRepository)
            self.dto_response = group_msg_repo.get_by_id(user_id)
            self.log_debug(f'Получена информация о пользователе {user_id}')
            return self

    def get_brief_info(self) -> UserDtoBriefInfo | None:
        if self.dto_response:
            return UserDtoBriefInfo(
                id=self.dto_response.id,
                user_name=self.dto_response.user_name,
                years_old=self.dto_response.years_old,
                email=self.dto_response.email,
                phone=self.dto_response.phone
            )
        return None