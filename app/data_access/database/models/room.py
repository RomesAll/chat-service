from uuid import UUID
from sqlalchemy import String, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column
from .base import BaseOrm
from .mixins import IdMixin


class RoomOrm(BaseOrm, IdMixin):
    """Orm модель для группового чата(комнаты)"""
    __tablename__ = 'room'
    name: Mapped[str] = mapped_column(String(20), unique=True)

    def __repr__(self):
        base_repr = super().__repr__()
        result = base_repr.replace(')>', f', name={self.name})>')
        return result


class UserInRoomOrm(BaseOrm):
    """Orm модель для хранения связи пользователь -> комнаты и наоборот"""
    __tablename__ = 'user_in_room'
    user_id: Mapped[str] = mapped_column(ForeignKey('user.id', ondelete='CASCADE'), primary_key=True, nullable=False)
    room_id: Mapped[UUID] = mapped_column(ForeignKey('room.id', ondelete='CASCADE'), primary_key=True, nullable=False)
