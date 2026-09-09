from typing import Generic
from fastapi import Depends, HTTPException, status
from app.shared.dtos import ActionType, JWTBaseToken, AuditPostDto, RequestClientDtoHandle
from app.data_access.database.models.user import RoleEnum
from dtos.base import TToken
from .audit import AuditDep
from .auth import AuthChecker


class RequestClientDepends(Generic[TToken]):
    """Базовая зависимость DI для fastapi end-point"""
    def __init__(
            self,
            allowed_roles: list[RoleEnum],
            action_type: ActionType
    ):
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
        dto_audit.user_id = token_info.user_id
        dto_audit.action = self.action_type
        result = RequestClientDtoHandle[TToken](
            dto_audit=dto_audit,
            token_info=token_info
        )
        return result