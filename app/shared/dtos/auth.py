from pydantic import BaseModel, SecretStr
from app.shared.dtos import UserDtoGetResponse
from dtos.jwt import JWTRefreshTokenResponse


class LoginDtoRequest(BaseModel):
    """DTO для входа в систему"""
    user_id: str
    password: SecretStr


class LoginOrRegisterDtoResponse(JWTRefreshTokenResponse):
    """DTO для получения информации о пользователе после входа или регистрации"""
    user_info: UserDtoGetResponse