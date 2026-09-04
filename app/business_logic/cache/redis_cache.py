from typing import Self
from redis import Redis
from threading import Lock

from business_logic.cache.jwt_white_list import JWTWhiteListCache
from business_logic.cache.session_key_storage import SessionKeyStorage


class RedisCache:
    """Потокобезопасный singleton для redis кеша"""
    _instance: Self | None = None
    _lock = Lock()

    def __new__(cls, *args, **kwargs) -> Self:
        if not cls._instance:
            with cls._lock:
                if not cls._instance:
                    cls._instance = super().__new__(cls)
        if cls._instance:
            return cls._instance
        else:
            raise Exception('Ошибка создание singleton RedisCache')

    def __init__(self, url: str):
        if hasattr(self, '_is_init'):
            return
        with self._lock:
            if hasattr(self, '_is_init'):
                return
            self._is_init = True
            self.redis_client = Redis.from_url(url)
            self._jwt_white_list = JWTWhiteListCache(self.redis_client)
            self._session_key_storage = SessionKeyStorage(self.redis_client)

    @property
    def jwt_white_list(self):
        """Получить адаптер для работы с white list"""
        return self._jwt_white_list

    @property
    def session_key_storage(self):
        """Получить адаптер для работы с сессионными ключами"""
        return self._session_key_storage