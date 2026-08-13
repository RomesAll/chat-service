from datetime import datetime, timezone
from uuid import UUID
from pydantic import BaseModel, Field
from enum import Enum
from models.user import RoleEnum


class TokenType(str, Enum):
    ACCESS_TOKEN = 'access_token'
    REFRESH_TOKEN = 'refresh_token'


class JWTBaseToken(BaseModel):
    user_id: str
    sub: str
    type: TokenType
    exp: int | None = None

    def get_exp_human(self, tz=timezone.utc):
        if not self.exp:
            raise Exception
        return datetime.fromtimestamp(self.exp, tz=tz)


class JWTAccessToken(JWTBaseToken):
    role: RoleEnum
    type: TokenType = Field(default=TokenType.ACCESS_TOKEN)


class JWTRefreshToken(JWTBaseToken):
    refresh_id: UUID
    type: TokenType = Field(default=TokenType.REFRESH_TOKEN)


class JWTRefreshTokenResponse(BaseModel):
    access_token: str
    refresh_token: str