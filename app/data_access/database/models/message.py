from sqlalchemy import ForeignKey
from sqlalchemy.orm import Mapped, mapped_column
from app.shared.dtos import MessageType
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