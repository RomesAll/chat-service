import re
from enum import Enum
from sqlalchemy import String, LargeBinary
from sqlalchemy.orm import Mapped, mapped_column, validates
from .base import BaseOrm
from .mixins import StringIdMixin


class RoleEnum(str, Enum):
    SUPER_ADMIN = 'super_admin'
    DEFAULT_USER = 'default_user'


class UserOrm(BaseOrm, StringIdMixin):
    """Orm модель для пользователей"""
    __tablename__ = 'user'
    email: Mapped[str] = mapped_column(primary_key=True, unique=True)
    phone: Mapped[str] = mapped_column(unique=True, nullable=False)
    user_name: Mapped[str] = mapped_column()
    bio: Mapped[str] = mapped_column(String(100), default=None, nullable=True)
    years_old: Mapped[int] = mapped_column(default=None, nullable=True)
    password: Mapped[bytes] = mapped_column(LargeBinary(60), nullable=False)
    role: Mapped[RoleEnum] = mapped_column()

    @validates('id')
    def validate_id(self, key, value):
        if not re.match(r'^[a-zA-Z0-9\-_]+$', value):
            raise ValueError(
                f"ID '{value}' содержит недопустимые символы. "
                f"Разрешены: буквы, цифры, '-', '_'"
            )
        reserved = {'admin', 'root', 'system', 'null', 'undefined'}
        if value.lower() in reserved:
            raise ValueError(f"ID '{value}' зарезервирован системой")
        return value

    def __repr__(self):
        base_repr = super().__repr__()
        result = base_repr.replace(')>', f', id={self.id}, user_name={self.user_name}, years_old={self.years_old}), role={self.role}>')
        return result