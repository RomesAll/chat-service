from datetime import datetime, timezone
from uuid import UUID
from pydantic import BaseModel, Field
from enum import Enum
from models.user import RoleEnum


class TokenType(str, Enum):
    """Перечисления типов токенов"""
    ACCESS_TOKEN = 'access_token'
    REFRESH_TOKEN = 'refresh_token'


class JWTBaseToken(BaseModel):
    """Base DTO для хранения информации о access и refresh токенах"""
    user_id: str
    sub: str
    type: TokenType
    exp: int | None = None
    role: RoleEnum

    def get_exp_human(self, tz=timezone.utc):
        if not self.exp:
            raise Exception
        return datetime.fromtimestamp(self.exp, tz=tz)


class JWTAccessToken(JWTBaseToken):
    """DTO для хранения информации о access токенах"""
    type: TokenType = Field(default=TokenType.ACCESS_TOKEN)


class JWTRefreshToken(JWTBaseToken):
    """DTO для хранения информации о refresh токенах"""
    refresh_id: UUID
    type: TokenType = Field(default=TokenType.REFRESH_TOKEN)


class JWTRefreshTokenResponse(BaseModel):
    """DTO для хранения сгенерированных access и refresh токенах"""
    access_token: str
    refresh_token: str