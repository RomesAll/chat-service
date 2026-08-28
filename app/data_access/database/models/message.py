from datetime import datetime, timezone
from typing import Any
from uuid import UUID
from sqlalchemy import ForeignKey, DateTime, JSON
from sqlalchemy.orm import Mapped, mapped_column
from .base import BaseOrm
from .mixins import IdMixin


class PrivateMessageOrm(BaseOrm, IdMixin):
    """Orm модель для приватных сообщений"""
    __tablename__ = 'private_message'
    sender_id: Mapped[str] = mapped_column(ForeignKey("user.id", ondelete="CASCADE"))
    recipient_id: Mapped[str] = mapped_column(ForeignKey("user.id", ondelete="CASCADE"))
    message_for_recipient: Mapped[str]
    message_for_sender: Mapped[str]
    recipient_key_version: Mapped[str]
    sender_key_version: Mapped[str]

    def __repr__(self):
        base_repr = super().__repr__()
        result = base_repr.replace(')>', f', id={self.id}, sender_id={self.sender_id}, recipient_id={self.recipient_id})>')
        return result


class RoomMessageOrm(BaseOrm, IdMixin):
    """Orm модель для групповых сообщений"""
    __tablename__ = 'group_message'
    room_id: Mapped[UUID] = mapped_column(ForeignKey('room.id', ondelete='CASCADE'))
    sender_id: Mapped[str] = mapped_column(ForeignKey('user.id', ondelete='CASCADE'))
    payload: Mapped[dict[str, Any]] = mapped_column(JSON, nullable=False)
    time_send: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda : datetime.now(tz=timezone.utc),
        nullable=False
    )

    def __repr__(self):
        base_repr = super().__repr__()
        result = base_repr.replace(')>', f', id={self.id}, room_id={self.room_id}, sender_id={self.sender_id})>')
        return result