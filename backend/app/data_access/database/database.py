from contextlib import contextmanager
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from starlette.middleware.sessions import Session


class Database:
    """Класс для управления подключением к бд"""
    def __init__(self, url: str):
        self.engine = create_engine(url=url)
        self.session_factory = sessionmaker(self.engine)

    @contextmanager
    def get_session(self):
        """Получение сессии в контекстном менеджере"""
        session = self.session_factory()
        try:
            yield session
            session.commit()
        except:
            session.rollback()
            raise
        finally:
            session.close()

    def create_session(self) -> Session:
        """Прямое получение сессии"""
        return self.session_factory()
