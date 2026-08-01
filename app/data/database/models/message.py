from sqlalchemy import Text, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy import UUID as PUUID
from base import BaseOrm, TimeStampMixin, IdMixin
from uuid import UUID


class PrivateMessageOrm(BaseOrm, IdMixin, TimeStampMixin):
    """Orm модель для приватных сообщений"""
    __tablename__ = 'private_message'
    sender_id: Mapped[UUID] = mapped_column(PUUID, ForeignKey("user.id", ondelete="CASCADE"))
    recipient_id: Mapped[UUID] = mapped_column(PUUID, ForeignKey("user.id", ondelete="CASCADE"))
    message: Mapped[str] = mapped_column(Text)


class GroupMessageOrm(BaseOrm, IdMixin, TimeStampMixin):
    """Orm модель для публичных сообщений"""
    __tablename__ = 'group_message'
    sender_id: Mapped[UUID] = mapped_column(PUUID, ForeignKey("user.id", ondelete="CASCADE"))
    chat_id: Mapped[UUID] = mapped_column(PUUID, ForeignKey("room.id", ondelete="CASCADE"))
    message: Mapped[str] = mapped_column(Text)

    def __repr__(self):
        return f'<{self.__class__.__name__}(id={self.id}, sender_id={self.sender_id}, chat_id={self.chat_id})>'

    def __str__(self):
        return f'Сообщение от {self.sender_id} в группу {self.chat_id}'
