from typing import Generic
from fastapi import Depends, HTTPException, status
from app.shared.dtos import ActionType, JWTBaseToken, AuditPostDto, RequestClientDtoHandle
from app.data_access.database.models.user import RoleEnum
from app.shared.dtos.base import TToken
from .audit import AuditDep
from .auth import AuthChecker
from ...shared.dtos.jwt import TokenType


class RequestClientDepends(Generic[TToken]):
    """Базовая зависимость DI для fastapi end-point"""
    def __init__(
            self,
            token_type: TokenType,
            allowed_roles: list[RoleEnum],
            action_type: ActionType
    ):
        self.token_type = token_type
        self.allowed_roles = allowed_roles
        self.action_type = action_type

    def __call__(
            self,
            token_info: JWTBaseToken = Depends(AuthChecker()),
            dto_audit: AuditPostDto = Depends(AuditDep())
    ) -> RequestClientDtoHandle:
        if token_info.role not in self.allowed_roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="У вас недостаточно прав для выполнения этого действия"
            )
        if token_info.type != self.token_type:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Передан неверный тип токена для выполнения дествия"
            )
        dto_audit.user_id = token_info.user_id
        dto_audit.action = self.action_type
        result = RequestClientDtoHandle[TToken](
            dto_audit=dto_audit,
            token_info=token_info
        )
        return result