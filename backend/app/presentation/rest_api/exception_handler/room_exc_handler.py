from fastapi import Request, status
from starlette.responses import JSONResponse
from app.business_logic.exceptions import GenerateInviteTokenOnlyOwner


async def generate_invite_url_only_owner(request: Request, exc: GenerateInviteTokenOnlyOwner) -> JSONResponse:
    """Обработка отс. правл для генерации ссылки вступления в кномнату"""
    return JSONResponse(
        status_code=status.HTTP_403_FORBIDDEN,
        content={
            'error': f'У пользователя {exc.user_id} нет прав для создания ссылки вступления в комнату {exc.room_name}',
            'detail': ''
        }
    )
