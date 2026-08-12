import jwt

class JwtManager:
    """Менеджер для выпуска и декодирования токенов доступа, обновления"""

    @classmethod
    def create_access_token(cls, data: dict) -> str:
        """Создание токена доступа"""
        pass

    @classmethod
    def create_refresh_token(cls, data: dict) -> str:
        """Создание токена обновления"""
        pass

    @classmethod
    def decode_access_token(cls, token: str) -> dict:
        """Декодирование токена доступа"""
        pass

    @classmethod
    def decode_refresh_token(cls, token: str) -> dict:
        """Декодирование токена обновления"""
        pass