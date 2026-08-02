from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column
from base import BaseOrm
from models.mixins import IdMixin, TimeStampMixin


class UserOrm(BaseOrm, IdMixin, TimeStampMixin):
    """Orm модель для пользователей"""
    __tablename__ = 'user'
    user_name: Mapped[str] = mapped_column(unique=True)
    bio: Mapped[str] = mapped_column(String(100), default='')
    years_old: Mapped[int]
    email: Mapped[str] = mapped_column(primary_key=True, unique=True)
    password: Mapped[str]

    def __repr__(self):
        return f'<{self.__class__.__name__}(id={self.id}, user_name={self.user_name})>'

    def __str__(self):
        return f'Пользователь {self.user_name} ({self.years_old} лет)'