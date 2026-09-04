from uuid import UUID
from redis import Redis

from business_logic.exceptions import SessionKeyNotFound, SaveSessionKeyError


class SessionKeyStorage:
    """Адаптер для хранения сессионных ключей в redis кеше"""
    def __init__(self, client: Redis, db: int = 1):
        self.client = client
        self.db = db
        self.client.select(db)
        self._prefix = 'session'

    def __len__(self):
        return self.client.dbsize()

    def __setitem__(self, key, value):
        """
        Сохранение сессионного ключа через синтаксис словаря
        :param key: коллекция из user_id, session_id
        :param value: exp время жизни записи в кеше
        :return:
        """
        user_id, session_id = key
        self.save(user_id, session_id, value)

    def __delitem__(self, key):
        """
        Удаление сессионного ключа через синтаксис словаря
        :param key: коллекция из user_id, session_id
        :return:
        """
        user_id, session_id = key
        return self.delete(user_id, session_id)

    def __getitem__(self, item):
        """
        Получение сессионного ключа
        :param item: коллекция из user_id, token_id
        :return:
        """
        user_id, session_id = item
        return self.get(user_id, session_id)

    def save(self, user_id: str, session_id: UUID, session_key: bytes) -> bool:
        """
        Добавление session key в redis кеш
        :param user_id: id пользователя
        :param session_id: id сессии
        :param session_key: сессионный ключ
        :return: True или False
        """
        result = bool(
            self.client.setex(
                name=f'{self._prefix}:{user_id}:{session_id}',
                time=3600,
                value=session_key.hex()
            )
        )
        if not result:
            raise SaveSessionKeyError(user_id, session_id)
        return result

    def get(self, user_id: str, session_id: UUID) -> bytes:
        """
        Получение сессионного ключа из redis кеша, если не найден, то генерируется исключение
        SessionKeyNotFound
        :param user_id: id пользователя
        :param session_id: id сессии
        :return: ключ в виде байтов
        """
        session_key_hex: bytes | str | None = self.client.get(f'{self._prefix}:{user_id}:{session_id}')
        if not session_key_hex:
            raise SessionKeyNotFound(user_id, session_id)
        return bytes.fromhex(session_key_hex)

    def delete(self, user_id: str, session_id: UUID) -> bool:
        """
        Удаление ключа из redis кеша
        :param user_id: id пользователя
        :param session_id: id сессии
        :return: True или False
        """
        return bool(
            self.client.delete(
                f'{self._prefix}:{user_id}:{session_id}'
            )
        )
