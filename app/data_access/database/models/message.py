from sqlalchemy import Text, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy import UUID as PUUID
from app.shared.dtos import MessageType
from .base import BaseOrm
from uuid import UUID
from models.mixins import IdMixin, TimeStampMixin


class PrivateMessageOrm(BaseOrm, IdMixin, TimeStampMixin):
    """Orm модель для приватных сообщений"""
    __tablename__ = 'private_message'
    sender_id: Mapped[UUID] = mapped_column(PUUID, ForeignKey("user.id", ondelete="CASCADE"))
    recipient_id: Mapped[UUID] = mapped_column(PUUID, ForeignKey("user.id", ondelete="CASCADE"))
    message: Mapped[str] = mapped_column(Text)
    type: Mapped[MessageType] = mapped_column(default=MessageType.PRIVATE)

    def __repr__(self):
        base_repr = super().__repr__()
        result = base_repr.replace(')>', f', sender_id={self.sender_id}, recipient_id={self.recipient_id})>')
        return result


class GroupMessageOrm(BaseOrm, IdMixin, TimeStampMixin):
    """Orm модель для публичных сообщений"""
    __tablename__ = 'group_message'
    sender_id: Mapped[UUID] = mapped_column(PUUID, ForeignKey("user.id", ondelete="CASCADE"))
    chat_id: Mapped[UUID] = mapped_column(PUUID, ForeignKey("room.id", ondelete="CASCADE"))
    message: Mapped[str] = mapped_column(Text)
    type: Mapped[MessageType] = mapped_column(default=MessageType.GROUP)

    def __repr__(self):
        base_repr = super().__repr__()
        result = base_repr.replace(')>', f', sender_id={self.sender_id}, chat_id={self.chat_id})>')
        return result
