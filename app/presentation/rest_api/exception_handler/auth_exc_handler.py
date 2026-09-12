from fastapi import Request, status
from starlette.responses import JSONResponse
from app.business_logic.exceptions import CheckPswError, RefreshTokenInActive, CheckMasterPswError


async def psw_error(request: Request, exc: CheckPswError) -> JSONResponse:
    """Обработка неверного ввода пароля"""
    return JSONResponse(
        status_code=status.HTTP_401_UNAUTHORIZED,
        content={
            'error': 'Неверный пароль',
            'detail': f'Для пользователя {exc.user_id} был введен неверный пароль'
        }
    )

async def refresh_token_in_active(request: Request, exc: RefreshTokenInActive) -> JSONResponse:
    """Обработка неактивного токена"""
    return JSONResponse(
        status_code=status.HTTP_400_BAD_REQUEST,
        content={
            'error': 'Токен не активен',
            'detail': f'Для пользователя {exc.user_id} отправлен не активный refresh токен'
        }
    )

async def psw_error_master_key(request: Request, exc: CheckMasterPswError) -> JSONResponse:
    """Обработка неверного ввода мастер пароля"""
    return JSONResponse(
        status_code=status.HTTP_401_UNAUTHORIZED,
        content={
            'error': 'Неверный пароль',
            'detail': 'Был введен неверный мастер пароль'
        }
    )

