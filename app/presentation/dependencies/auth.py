from fastapi import Depends, HTTPException
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from app.business_logic.auth.jwt_manager import JWTAccessManager, JWTRefreshManager
from app.shared.dtos import JWTBaseToken
import jwt
from app.shared.dtos.jwt import TokenType, JWTAccessTokenResponse, JWTRefreshTokenResponse

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