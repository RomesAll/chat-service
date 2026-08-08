from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column
from .base import BaseOrm
from models.mixins import IdMixin, TimeStampMixin


class RoomOrm(BaseOrm, IdMixin, TimeStampMixin):
    """Orm модель для группового чата(комнаты)"""
    __tablename__ = 'room'
    name: Mapped[str] = mapped_column(String(20), unique=True)

    def __repr__(self):
        base_repr = super().__repr__()
        result = base_repr.replace(')>', f', name={self.name})>')
        return result