from uuid import UUID
from sqlalchemy import select
from sqlalchemy.sql.elements import and_
from app.shared.dtos import RoomDtoGetResponse, RoomDtoPostRequest, UserInRoomResponse, UserInRoomPostRequest
from app.data_access.database.models.room import RoomOrm, UserInRoomOrm
from .base import BaseRepositoryGet, BaseRepositorySave


class RoomRepository(
    BaseRepositoryGet[RoomDtoGetResponse, RoomOrm],
    BaseRepositorySave[RoomDtoGetResponse, RoomDtoPostRequest, RoomOrm]
):
    """Репозиторий для работы с данными комнат"""
    model: type[RoomOrm] = RoomOrm
    dto_response: type[RoomDtoGetResponse] = RoomDtoGetResponse


class UserInRoomRepository(
    BaseRepositoryGet[UserInRoomResponse, UserInRoomOrm],
    BaseRepositorySave[UserInRoomResponse, UserInRoomPostRequest, UserInRoomOrm]
):
    """Репозиторий для работы с пользователями в группе"""
    model: type[UserInRoomOrm] = UserInRoomOrm
    dto_response: type[UserInRoomResponse] = UserInRoomResponse

    def check_exist_user_in_room(self, user_id: str, room_id: UUID) -> bool:
        stmt_exists = select(self.model).where(
            and_(
                self.model.room_id == room_id,
                self.model.user_id == user_id
            )
        )
        result = self.session.execute(stmt_exists).scalar_one_or_none()
        return True if result else False

    def get_users_in_room(self, room_id: UUID) -> list[UserInRoomResponse]:
        stmt = select(self.model).where(self.model.room_id == room_id)
        results = self.session.execute(stmt).scalars().all()
        return [self.dto_response(**result.to_dict()) for result in results ]