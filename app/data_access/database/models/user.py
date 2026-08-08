from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column
from .base import BaseOrm
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
        base_repr = super().__repr__()
        result = base_repr.replace(')>', f', user_name={self.user_name}, years_old={self.years_old})>')
        return result