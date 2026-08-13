from fastapi import Depends, HTTPException
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from starlette import status
from business_logic.auth.jwt_manager import JWTAccessManager
from dtos import JWTAccessToken
import jwt
from models.user import RoleEnum

security = HTTPBearer()


class AuthChecker:
    """Проверка существования access токена"""
    def __call__(self, credentials: HTTPAuthorizationCredentials = Depends(security)) -> JWTAccessToken:
        token = credentials.credentials
        try:
            payload: JWTAccessToken = JWTAccessManager.decode_token(token)
            if not payload.user_id or not payload.role:
                raise HTTPException(status_code=401, detail="Неверные данные в токена")
            return payload
        except jwt.ExpiredSignatureError:
            raise HTTPException(status_code=401, detail="Token expired (Access токен протух)")
        except jwt.InvalidTokenError:
            raise HTTPException(status_code=401, detail="Недействительный токен")


class RoleChecker:
    """Проверка ролей в токене"""
    def __init__(self, allowed_roles: list[RoleEnum]):
        self.allowed_roles = allowed_roles

    def __call__(self, current_user: JWTAccessToken = Depends(AuthChecker())) -> JWTAccessToken:
        if current_user.role not in self.allowed_roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="У вас недостаточно прав для выполнения этого действия"
            )
        return current_user