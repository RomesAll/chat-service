from abc import abstractmethod, ABC
from copy import copy
from datetime import timedelta, datetime, timezone
from typing import TypeVar, Generic
from uuid import uuid4
from app.shared.dtos import JWTAccessToken, JWTRefreshToken, JWTBaseToken, JWTRefreshTokenResponse
import jwt
from models.user import RoleEnum

T = TypeVar('T', bound=JWTBaseToken)

class JWTBaseManager(ABC, Generic[T]):
    """Базовый класс менеджер для выпуска и декодирования токенов доступа, обновления"""

    SECRET_KEY: str = ""
    ALGORITHM: str = "HS256"
    EXPIRES_DELTA: timedelta = timedelta(minutes=15)

    @classmethod
    def create_token(cls, data: T) -> str:
        """Создание токена доступа, обновления"""
        to_encode: T = copy(data)
        to_encode.exp = int((datetime.now(tz=timezone.utc) + cls.EXPIRES_DELTA).timestamp())
        return jwt.encode(to_encode.model_dump(mode='json'), cls.SECRET_KEY, algorithm=cls.ALGORITHM)

    @classmethod
    def decode_token(cls, token: str) -> T:
        """Декодирование токена доступа, обновления"""
        to_decode = jwt.decode(token, cls.SECRET_KEY, algorithms=[cls.ALGORITHM,])
        return cls._create_token_instance(to_decode_token=to_decode)

    @classmethod
    @abstractmethod
    def _create_token_instance(cls, to_decode_token: dict) -> T:
        """Создает экземпляр токена (должен быть переопределен)"""
        pass


class JWTAccessManager(JWTBaseManager[JWTAccessToken]):
    """Менеджер для выпуска и декодирования токенов доступа"""

    SECRET_KEY: str = "access_secret_key_12345678901234567890"
    EXPIRES_DELTA: timedelta = timedelta(minutes=15)

    @classmethod
    def _create_token_instance(cls, to_decode_token: dict) -> JWTAccessToken:
        """Создает экземпляр токена"""
        return JWTAccessToken(**to_decode_token)


class JWTRefreshManager(JWTBaseManager[JWTRefreshToken]):
    """Менеджер для выпуска и декодирования токенов обновления"""

    SECRET_KEY: str = "refresh_secret_key_12345678901234567890"
    EXPIRES_DELTA: timedelta = timedelta(days=7)

    @classmethod
    def _create_token_instance(cls, to_decode_token: dict) -> JWTRefreshToken:
        """Создает экземпляр токена"""
        return JWTRefreshToken(**to_decode_token)


class JWTFacade:
    """Фасадный класс для создания access и refresh токенов"""
    jwt_access_manager = JWTAccessManager
    jwt_refresh_manager = JWTRefreshManager

    @classmethod
    def create_tokens(cls, user_id: str, sub: str, role: RoleEnum) -> JWTRefreshTokenResponse:
        """Создания пары access и refresh токенов"""
        access_token: str = JWTAccessManager.create_token(
            JWTAccessToken(
                user_id=user_id,
                sub=sub,
                role=role
            )
        )
        refresh_token: str = JWTRefreshManager.create_token(
            JWTRefreshToken(
                user_id=user_id,
                sub=sub,
                refresh_id=uuid4(),
            )
        )
        return JWTRefreshTokenResponse(
            access_token=access_token,
            refresh_token=refresh_token
        )