from datetime import datetime, timezone
from uuid import UUID
import redis

from business_logic.auth.jwt_manager import JWTFacade


class JWTWhiteListCache:
    """
    Адаптер для реализации white list для jwt refresh токена в redis кеше.
    В redis хранятся только разрешенные токены для обновления
    """
    def __init__(self, client: redis.Redis):
        self.client = client

    def save_refresh_token(self, user_id: str, token_id: UUID, ex: int) -> bool:
        """Сохранение refresh токена"""
        return bool(self.client.set(f'session:{user_id}:{token_id}', 'active', ex=ex))

    def check_exist(self, user_id: str, token_id: UUID) -> bool:
        """Проверка существования refresh токена"""
        return bool(self.client.exists(f'session:{user_id}:{token_id}'))

    def delete_refresh_token(self, user_id: str, token_id: UUID) -> bool:
        """Удаление refresh токена"""
        return bool(self.client.delete(f'session:{user_id}:{token_id}'))

    def clear_user_token(self, user_id: str) -> bool:
        """Очистка всех refresh токенов пользователя"""
        return bool(self.client.delete(f'session:{user_id}:*'))

    def update_refresh(self, user_id: str, old_refresh_id: UUID, new_refresh_id: UUID):
        """Метод для обновления токенов"""
        if not self.check_exist(
            user_id=user_id,
            token_id=old_refresh_id,
        ):
            raise Exception
        self.delete_refresh_token(
            token_id=old_refresh_id,
            user_id=user_id
        )
        self.save_refresh_token(
            user_id=user_id,
            token_id=new_refresh_id,
            ex=int((datetime.now(tz=timezone.utc) + JWTFacade.jwt_refresh_manager.EXPIRES_DELTA).timestamp())
        )


jwt_white_list = JWTWhiteListCache(
    redis.Redis(host='127.0.0.1', port=6380, db=0, password='qwerty')
)