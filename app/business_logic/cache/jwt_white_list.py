from datetime import datetime, timezone
from uuid import UUID
from redis import Redis

from app.business_logic.auth.jwt_manager import JWTFacade
from business_logic.exceptions import RefreshTokenIdNotFound, SaveIdRefreshTokenWhiteListError


class JWTWhiteListCache:
    """
    Адаптер для реализации white list для jwt refresh токена в redis кеше.
    В redis хранятся только разрешенные токены для обновления.
    """
    def __init__(self, redis_client: Redis, db: int = 0):
        self.client = redis_client
        self.db = db
        self.client.select(self.db)
        self._prefix = 'white_list'

    def __contains__(self, item):
        """
        Проверка существования refresh токена с помощью оператора in по id
        в white list, item может быть:
        - кортежем из user_id (id пользователя, например, Sasha) и token_id (id refresh токена в формате UUID)
        """
        try:
            if not isinstance(item, tuple):
                raise TypeError(f'Для проверки сущ. токена нужно передать '
                                f'кортеж (из user_id и token_id), а передан тип: {type(item)}')
            if len(item) != 2:
                raise TypeError(f'Для проверки сущ. токена нужно передать '
                                f'ровно два значения - это user_id и token_id')
            user_id, token_id = item
            return self.check_exist(user_id, token_id)
        except TypeError:
            raise

    def __setitem__(self, key, value):
        """
        Сохранение id refresh токена в white list через синтаксис словаря
        :param key: коллекция из user_id, token_id
        :param value: exp время жизни записи в кеше
        :return:
        """
        user_id, token_id = key
        self.save_refresh_token(user_id, token_id, value)

    def __delitem__(self, key):
        """
        Удаление токена через синтаксис словаря
        :param key: коллекция из user_id, token_id
        :return:
        """
        user_id, token_id = key
        return self.delete_refresh_token(user_id, token_id)

    def __getitem__(self, item):
        """
        Проверка существования id токена
        :param item: коллекция из user_id, token_id
        :return:
        """
        user_id, token_id = item
        return self.check_exist(user_id, token_id)

    def __call__(self, user_id: str, old_refresh_id: UUID, new_refresh_id: UUID):
        """Позволяет вызвать объект как функцию для обновления"""
        self.update_refresh(user_id, old_refresh_id, new_refresh_id)

    def __len__(self):
        return self.client.dbsize()

    def save_refresh_token(self, user_id: str, token_id: UUID, ex: int) -> bool:
        """Сохранение refresh токена"""
        result = bool(self.client.set(f'{self._prefix}:{user_id}:{token_id}', 'active', ex=ex))
        if not result:
            raise SaveIdRefreshTokenWhiteListError(user_id)
        return result

    def check_exist(self, user_id: str, token_id: UUID) -> bool:
        """Проверка существования refresh токена"""
        return bool(self.client.exists(f'{self._prefix}:{user_id}:{token_id}'))

    def delete_refresh_token(self, user_id: str, token_id: UUID) -> bool:
        """Удаление refresh токена"""
        return bool(self.client.delete(f'{self._prefix}:{user_id}:{token_id}'))

    def clear_user_token(self, user_id: str) -> bool:
        """Очистка всех refresh токенов пользователя"""
        return bool(self.client.delete(f'{self._prefix}:{user_id}:*'))

    def update_refresh(self, user_id: str, old_refresh_id: UUID, new_refresh_id: UUID):
        """Метод для обновления токенов"""
        if not (user_id, old_refresh_id) in self:
            raise RefreshTokenIdNotFound(user_id, old_refresh_id)
        del self[user_id, old_refresh_id]
        dt_now = datetime.now(tz=timezone.utc)
        expires_delta = JWTFacade.jwt_refresh_manager.EXPIRES_DELTA
        new_token_ex = int((dt_now + expires_delta).timestamp())
        self[user_id, new_refresh_id] = new_token_ex