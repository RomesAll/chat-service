from enum import Enum
from typing import Iterable
from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column
from base import BaseOrm
from uuid import UUID, uuid4
import pprint

class UserFields(str, Enum):
    ID = 'id'
    USER_NAME = 'user_name'
    BIO = 'bio'
    YEARS_OLD = 'years_old'
    EMAIL = 'email'
    IS_DELETED = 'is_deleted'
    PASSWORD = 'password'

class UserOrm(BaseOrm):
    __tablename__ = 'user'
    id: Mapped[UUID] = mapped_column(primary_key=True, unique=True)
    user_name: Mapped[str] = mapped_column(unique=True)
    bio: Mapped[str] = mapped_column(String(100), default='')
    years_old: Mapped[int]
    email: Mapped[str] = mapped_column(primary_key=True, unique=True)
    is_deleted: Mapped[bool] = mapped_column(default=False)
    password: Mapped[str]

    def __repr__(self):
        return f'<{self.__class__.__name__}(id={self.id}, user_name={self.user_name})>'

    def __str__(self):
        return f'Пользователь {self.user_name} ({self.years_old} лет)'

    def to_dict(
            self,
            exclude: Iterable[UserFields] | None = None,
            uuid_is_str: bool = False
    ):
        serializers_data = {
            'id': str(self.id) if uuid_is_str else self.id,
            'user_name': self.user_name,
            'bio': self.bio,
            'years_old': self.years_old,
            'email': self.email,
            'is_deleted': self.is_deleted,
            'password': self.password
        }
        if not exclude:
            return serializers_data
        exclude_data = {field.value for field in exclude}
        return {
            field : value
            for field, value in serializers_data.items()
            if field not in exclude_data
        }

    def soft_delete(self) -> bool:
        self.is_deleted = True
        return bool(self.is_deleted)

    def soft_recovery(self) -> bool:
        self.is_deleted = False
        return bool(self.is_deleted)
