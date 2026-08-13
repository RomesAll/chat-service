from pydantic import BaseModel, SecretStr
from app.shared.dtos import UserDtoGetResponse
from dtos.jwt import JWTRefreshTokenResponse


class LoginDtoRequest(BaseModel):
    user_id: str
    password: SecretStr


class LoginOrRegisterDtoResponse(JWTRefreshTokenResponse):
    user_info: UserDtoGetResponse