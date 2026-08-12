from datetime import datetime, timezone
from uuid import UUID
from pydantic import BaseModel, Field
from enum import Enum


class TokenType(str, Enum):
    ACCESS_TOKEN = 'access_token'
    REFRESH_TOKEN = 'refresh_token'


class JWTBaseToken(BaseModel):
    user_id: UUID
    sub: str
    type: TokenType
    exp: int | None = None

    def get_exp_human(self, tz=timezone.utc):
        if not self.exp:
            raise Exception
        return datetime.fromtimestamp(self.exp, tz=tz)


class JWTAccessToken(JWTBaseToken):
    type: TokenType = Field(default=TokenType.ACCESS_TOKEN)


class JWTRefreshToken(JWTBaseToken):
    refresh_id: UUID
    type: TokenType = Field(default=TokenType.REFRESH_TOKEN)
