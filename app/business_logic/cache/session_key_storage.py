from uuid import UUID
import redis


class SessionKeyStorage:
    """Адаптер для хранения сессионных ключей"""
    def __init__(self, client: redis.Redis):
        self.client = client

    def save(self, user_id: str, session_id: UUID, session_key: bytes) -> bool:
        """Добавление сессионного ключа в кеш"""
        return bool(
            self.client.setex(
                name=f'session:{user_id}:{session_id}',
                time=3600,
                value=session_key.hex()
            )
        )

    def get(self, user_id: str, session_id: UUID) -> bytes | None:
        """Получение сессионного ключа"""
        session_key_hex: bytes | str | None = self.client.get(f'session:{user_id}:{session_id}')
        if not session_key_hex:
            return None
        return bytes.fromhex(session_key_hex)

    def delete(self, user_id: str, session_id: UUID) -> bool:
        """Удаление сессионного ключа"""
        return bool(self.client.delete(f'session:{user_id}:{session_id}'))
