from typing import Type, TypeVar
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session
from database import Database
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from repositories.base import BaseRepository

R = TypeVar('R', bound='BaseRepository')

class UnitOfWork:
    """
    Класс для реализации паттерна "Unit of Work"
    """
    def __init__(self, db: Database):
        self.db = db
        self.session: Session | None = None
        self._repository: dict[type['BaseRepository'], 'BaseRepository'] = {}

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
            repo_class: Type[R]
    ) -> R:
        """Получить уже зарегистрированный репозиторий"""
        if not self.session:
            raise SQLAlchemyError('В uof не указана сессия SQLAlchemy')
        if repo_class not in self._repository:
            self._repository[repo_class] = repo_class(session=self.session)
        return self._repository[repo_class]