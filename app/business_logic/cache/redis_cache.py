from redis import Redis
from app.business_logic.cache.jwt_white_list import JWTWhiteListCache
from app.business_logic.cache.session_key_storage import SessionKeyStorage
from app.business_logic.singleton import Singleton
from .verify_code_storage import VerifyCodeStorage


class RedisCache(Singleton):
    """Потокобезопасный singleton для redis кеша"""
    def __init__(self, url: str):
        super().__init__()
        with self._lock:
            if hasattr(self, '_is_init'):
                return
            self._is_init = True
            self.redis_client = Redis.from_url(url)
            self._jwt_white_list = JWTWhiteListCache(self.redis_client)
            self._session_key_storage = SessionKeyStorage(self.redis_client)
            self._verify_code_storage = VerifyCodeStorage(self.redis_client)

    @property
    def jwt_white_list(self):
        """Получить адаптер для работы с white list"""
        return self._jwt_white_list

    @property
    def session_key_storage(self):
        """Получить адаптер для работы с сессионными ключами"""
        return self._session_key_storage

    @property
    def verify_code_storage(self):
        """Получить адаптер для работы с кодами подтверждения"""
        return self._verify_code_storage