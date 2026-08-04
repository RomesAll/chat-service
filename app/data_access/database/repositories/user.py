from sqlalchemy.orm import Session
from app.shared.dtos.user import UserDtoGetResponse
from models.user import UserOrm
from .base import BaseRepository


class UserRepository(BaseRepository):
    """Репозиторий для работы с данными пользователей"""
    def __init__(self, session: Session):
        super().__init__(
            dto_response=UserDtoGetResponse,
            session=session,
            model=UserOrm
        )