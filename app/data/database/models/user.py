from enum import Enum
from typing import Iterable
from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column
from base import BaseOrm
from uuid import UUID, uuid4
import pprint

class UserOrm(BaseOrm):
    __tablename__ = 'user'
    id: Mapped[UUID] = mapped_column(primary_key=True, unique=True)
    user_name: Mapped[str] = mapped_column(unique=True)
    bio: Mapped[str] = mapped_column(String(100), default='')
    years_old: Mapped[int]
    email: Mapped[str] = mapped_column(primary_key=True, unique=True)
    is_deleted: Mapped[bool] = mapped_column(default=False)
    password: Mapped[str]