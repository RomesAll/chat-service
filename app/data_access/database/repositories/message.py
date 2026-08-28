from uuid import UUID
from sqlalchemy import select
from sqlalchemy.sql.elements import or_, and_
from app.shared.dtos import GroupMessageDtoResponse, GroupMessageDtoPostRequest
from app.data_access.database.models.message import PrivateMessageOrm, RoomMessageOrm
from .base import (
    BaseRepositoryGet,
    BaseRepositorySave,
    BaseRepositoryDelete
)
from app.shared.dtos import (
    MessageDtoGetResponse,
    PrivateMessageDtoPostRequest,
)


class PrivateMessageRepository(
    BaseRepositoryGet[MessageDtoGetResponse, PrivateMessageOrm],
    BaseRepositorySave[MessageDtoGetResponse, PrivateMessageDtoPostRequest, PrivateMessageOrm],
    BaseRepositoryDelete[MessageDtoGetResponse, PrivateMessageOrm]
):
    """Репозиторий для работы с данными приватных сообщений"""
    model: type[PrivateMessageOrm] = PrivateMessageOrm
    dto_response: type[MessageDtoGetResponse] = MessageDtoGetResponse

    def get_message_by_user(self, user_id_who: str, user_id_whom: str) -> list[MessageDtoGetResponse]:
        """Получить историю сообщений по id пользователям"""
        stmt = select(
            self.model
        ).where(
            or_(and_(
                self.model.sender_id == user_id_who,
                self.model.recipient_id == user_id_whom
            ),
                and_(
                self.model.recipient_id == user_id_who,
                self.model.sender_id == user_id_whom
            ))
        )
        results = self.session.execute(stmt).scalars().all()
        return [self.dto_response(**res.to_dict()) for res in results]


class GroupMessageRepository(
    BaseRepositoryGet[GroupMessageDtoResponse, RoomMessageOrm],
    BaseRepositorySave[GroupMessageDtoResponse, GroupMessageDtoPostRequest, RoomMessageOrm],
    BaseRepositoryDelete[GroupMessageDtoResponse, RoomMessageOrm]
):
    """Репозиторий для работы с данными групповых сообщений"""
    model: type[RoomMessageOrm] = RoomMessageOrm
    dto_response: type[GroupMessageDtoResponse] = GroupMessageDtoResponse

    def get_message_by_room(self, room_id: UUID) -> list[GroupMessageDtoResponse]:
        """Получить сообщение в комнате"""
        stmt = select(self.model).where(self.model.room_id == room_id)
        results = self.session.execute(stmt).scalars().all()
        return [self.dto_response(**res.to_dict()) for res in results]