from typing import Iterable
from sqlalchemy import Text, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy import UUID as PUUID
from base import BaseOrm
from uuid import UUID


class PrivateMessageOrm(BaseOrm):
    __tablename__ = 'private_message'

    id: Mapped[UUID] = mapped_column(PUUID, primary_key=True, unique=True)
    sender_id: Mapped[UUID] = mapped_column(PUUID, ForeignKey("user.id", ondelete="CASCADE"))
    recipient_id: Mapped[UUID] = mapped_column(PUUID, ForeignKey("user.id", ondelete="CASCADE"))
    message: Mapped[str] = mapped_column(Text)
    is_deleted: Mapped[bool] = mapped_column(default=False)

    def __repr__(self):
        return f'<{self.__class__.__name__}(id={self.id}, sender_id={self.sender_id}, recipient_id={self.recipient_id})>'

    def __str__(self):
        return f'Сообщение от {self.sender_id} к {self.recipient_id}'

    def to_dict(
            self,
            exclude: Iterable[str] | None = None,
            uuid_is_str: bool = False
    ):
        serializers_data = {
            'id': str(self.id) if uuid_is_str else self.id,
            'sender_id': str(self.sender_id) if uuid_is_str else self.id,
            'recipient_id': str(self.recipient_id) if uuid_is_str else self.id,
            'message': self.message,
            'is_deleted': self.is_deleted
        }
        if not exclude:
            return serializers_data
        exclude_data = {field for field in exclude}
        return {
            field : value
            for field, value in serializers_data.items()
            if field not in exclude_data
        }

    def soft_delete(self) -> bool:
        self.is_deleted = True
        return bool(self.is_deleted)

    def soft_recovery(self) -> bool:
        self.is_deleted = False
        return bool(self.is_deleted)


class GroupMessageOrm(BaseOrm):
    __tablename__ = 'group_message'

    id: Mapped[UUID] = mapped_column(PUUID, primary_key=True, unique=True)
    sender_id: Mapped[UUID] = mapped_column(PUUID, ForeignKey("user.id", ondelete="CASCADE"))
    chat_id: Mapped[UUID] = mapped_column(PUUID, ForeignKey("room.id", ondelete="CASCADE"))
    message: Mapped[str] = mapped_column(Text)
    is_deleted: Mapped[bool] = mapped_column(default=False)

    def __repr__(self):
        return f'<{self.__class__.__name__}(id={self.id}, sender_id={self.sender_id}, chat_id={self.chat_id})>'

    def __str__(self):
        return f'Сообщение от {self.sender_id} в группу {self.chat_id}'

    def to_dict(
            self,
            exclude: Iterable[str] | None = None,
            uuid_is_str: bool = False
    ):
        serializers_data = {
            'id': str(self.id) if uuid_is_str else self.id,
            'sender_id': str(self.sender_id) if uuid_is_str else self.id,
            'chat_id': str(self.chat_id) if uuid_is_str else self.id,
            'message': self.message,
            'is_deleted': self.is_deleted
        }
        if not exclude:
            return serializers_data
        exclude_data = {field for field in exclude}
        return {
            field : value
            for field, value in serializers_data.items()
            if field not in exclude_data
        }

    def soft_delete(self) -> bool:
        self.is_deleted = True
        return bool(self.is_deleted)

    def soft_recovery(self) -> bool:
        self.is_deleted = False
        return bool(self.is_deleted)