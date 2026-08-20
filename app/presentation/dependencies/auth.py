from fastapi import Depends, HTTPException
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from starlette import status
from business_logic.auth.jwt_manager import JWTAccessManager, JWTRefreshManager
from dtos import JWTBaseToken
import jwt
from dtos.jwt import TokenType, JWTAccessTokenResponse, JWTRefreshTokenResponse
from models.user import RoleEnum

security = HTTPBearer()


class AuthChecker:
    """Проверка существования access токена"""
    def __call__(
            self,
            credentials: HTTPAuthorizationCredentials = Depends(security),
            token_type: TokenType = TokenType.ACCESS_TOKEN
    ) -> JWTBaseToken:
        token = credentials.credentials
        try:
            payload = None
            if token_type == TokenType.ACCESS_TOKEN:
                payload: JWTAccessTokenResponse = JWTAccessManager.decode_token(token)
            elif token_type == TokenType.REFRESH_TOKEN:
                payload: JWTRefreshTokenResponse = JWTRefreshManager.decode_token(token)
            if not payload:
                raise Exception
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

    def __call__(self, current_user: JWTBaseToken = Depends(AuthChecker())) -> JWTBaseToken:
        if current_user.role not in self.allowed_roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="У вас недостаточно прав для выполнения этого действия"
            )
        return current_user