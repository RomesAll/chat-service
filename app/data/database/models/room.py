from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column
from base import BaseOrm, IdMixin, TimeStampMixin


class RoomOrm(BaseOrm, IdMixin, TimeStampMixin):
    """Orm модель для группового чата(комнаты)"""
    __tablename__ = 'room'
    name: Mapped[str] = mapped_column(String(20), unique=True)

    def __repr__(self):
        return f'<{self.__class__.__name__}(id={self.id}, name={self.name})>'

    def __str__(self):
        return f'Комната {self.name}'