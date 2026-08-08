from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session
from business_logic.database import Database
from interfaces.repository import TDtoId, TDtoGetResponse, TDtoPostPutDeleteRequest
from repositories.base import BaseRepository


class UnitOfWork:
    """
    Класс для реализации паттерна "Unit of Work"
    """

    def __init__(self, db: Database):
        self.db = db
        self.session: Session | None = None
        self._repository: dict[type[BaseRepository], BaseRepository] = {}

    def __enter__(self):
        self.session = self.db.create_session()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        if not self.session:
            return
        if exc_type:
            self.session.rollback()
        else:
            self.session.commit()
        self.session.close()

    def get_repository(
            self,
            repo_class: type[BaseRepository],
    ) -> BaseRepository[TDtoId, TDtoGetResponse, TDtoPostPutDeleteRequest]:
        """Получения репозиториев в текущей сессии uow"""
        if not self.session:
            raise SQLAlchemyError('В uof не указана сессия SQLAlchemy')
        if repo_class not in self._repository:
            self._repository[repo_class] = repo_class(session=self.session)
        return self._repository[repo_class]