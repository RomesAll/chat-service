from uuid import UUID
from sqlalchemy import String, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column
from .base import BaseOrm
from .mixins import IdMixin


class RoomOrm(BaseOrm, IdMixin):
    """Orm модель для комнат"""
    __tablename__ = 'room'
    name: Mapped[str] = mapped_column(String(100), nullable=False)

    def __repr__(self):
        base_repr = super().__repr__()
        result = base_repr.replace(')>', f', id={self.id}, name={self.name}>')
        return result


class UserInRoomOrm(BaseOrm):
    """Orm модель для пользователей в комнате"""
    __tablename__ = 'user_in_room'
    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    user_id: Mapped[str] = mapped_column(ForeignKey('user.id', ondelete='CASCADE'))
    room_id: Mapped[UUID] = mapped_column(ForeignKey('room.id', ondelete='CASCADE'))

    def __repr__(self):
        base_repr = super().__repr__()
        result = base_repr.replace(')>', f', user_id={self.user_id}, room_id={self.room_id}>')
        return result