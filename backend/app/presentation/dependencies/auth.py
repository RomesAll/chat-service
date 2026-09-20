from fastapi import Depends, HTTPException
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from jwt import InvalidSignatureError, DecodeError
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
    ) -> JWTBaseToken:
        token = credentials.credentials
        try:
            payload = None
            try:
                payload: JWTAccessTokenResponse = JWTAccessManager.decode_token(token)
                if payload.type == TokenType.ACCESS_TOKEN:
                    return payload
            except (InvalidSignatureError, DecodeError):
                pass

            try:
                payload: JWTRefreshTokenResponse = JWTRefreshManager.decode_token(token)
                if payload.type == TokenType.REFRESH_TOKEN:
                    return payload
            except (InvalidSignatureError, DecodeError):
                pass

            if not payload:
                raise HTTPException(status_code=401, detail="Не удалось обработать переданный токен")

            if not payload.user_id or not payload.role:
                raise HTTPException(status_code=401, detail="Неверные данные в токене")

            return payload
        except jwt.ExpiredSignatureError:
            raise HTTPException(status_code=401, detail="Время жизни токена истекло")
        except jwt.InvalidTokenError:
            raise HTTPException(status_code=401, detail="Недействительный токен")