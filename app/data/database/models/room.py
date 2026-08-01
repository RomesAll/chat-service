from typing import Iterable
from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy import UUID as PUUID
from base import BaseOrm
from uuid import UUID


class RoomOrm(BaseOrm):
    __tablename__ = 'room'
    id: Mapped[UUID] = mapped_column(PUUID, primary_key=True, unique=True)
    name: Mapped[str] = mapped_column(String(20), unique=True)
    is_deleted: Mapped[bool] = mapped_column(default=False)

    def __repr__(self):
        return f'<{self.__class__.__name__}(id={self.id}, name={self.name})>'

    def __str__(self):
        return f'Комната {self.name}'

    def to_dict(
            self,
            exclude: Iterable[str] | None = None,
            uuid_is_str: bool = False
    ):
        serializers_data = {
            'id': str(self.id) if uuid_is_str else self.id,
            'name': self.name,
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