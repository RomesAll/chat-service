from sqlalchemy import ForeignKey
from sqlalchemy.orm import Mapped, mapped_column
from models.base import BaseOrm


class UserPrivateKey(BaseOrm):
    """Orm модель приватных ключей пользователей"""
    __tablename__ = 'user_private_key'
    id: Mapped[int] = mapped_column(autoincrement=True, primary_key=True, nullable=False)
    user_id: Mapped[str] = mapped_column(ForeignKey('user.id', ondelete='CASCADE'), unique=True)
    encrypted_private_keys: Mapped[str] = mapped_column(nullable=False)