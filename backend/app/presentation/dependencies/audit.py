from fastapi import Request
from app.shared.dtos import AuditPostDto, ActionType


class AuditDep:
    """Получение DTO для аудита"""
    def __init__(self, action: ActionType | None = None):
        self.action = action

    def __call__(self, request: Request) -> AuditPostDto:
        dto_audit = AuditPostDto(
            user_id=None,
            action=self.action,
            ip=request.client.host,
            user_agent=request.headers.get("user-agent", ''),
            target_api=request.url.path,
        )
        return dto_audit
