from fastapi import Request, status
from starlette.responses import JSONResponse
from app.business_logic.exceptions import CheckPswError, RefreshTokenInActive, CheckMasterPswError, \
    RefreshTokenIdNotFound, VerifyCodeInCorrect, VerifyCodeStorageError
from app.presentation.rest_api.exception_handler.base import log_api, get_response_content


async def psw_error(request: Request, exc: CheckPswError) -> JSONResponse:
    """Обработка неверного ввода пароля"""
    msg = f'Для пользователя {exc.user_id} был введен неверный пароль'
    log_api(request, exc, msg)
    content = get_response_content(request, msg)
    return JSONResponse(
        status_code=status.HTTP_401_UNAUTHORIZED,
        content=content
    )

async def verify_code_storage_error(request: Request, exc: VerifyCodeStorageError) -> JSONResponse:
    """Обработка ошибок хранилища кодов подтверждения"""
    msg = f'Ошибка в redis кеше хранения кодов подтверждения для входа'
    log_api(request, exc, msg)
    content = get_response_content(request)
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content=content
    )

async def verify_code_incorrect(request: Request, exc: VerifyCodeInCorrect) -> JSONResponse:
    """Обработка ошибок неверного ввода"""
    msg = f'Введен неверный код подтверждения'
    log_api(request, exc, msg)
    content = get_response_content(request)
    return JSONResponse(
        status_code=status.HTTP_401_UNAUTHORIZED,
        content=content
    )

async def refresh_token_in_active(request: Request, exc: RefreshTokenInActive) -> JSONResponse:
    """Обработка неактивного токена"""
    msg = f'Для пользователя {exc.user_id} отправлен не активный refresh токен'
    log_api(request, exc, msg)
    content = get_response_content(request, msg)
    return JSONResponse(
        status_code=status.HTTP_400_BAD_REQUEST,
        content=content
    )

async def refresh_token_not_found(request: Request, exc: RefreshTokenIdNotFound) -> JSONResponse:
    """Id refresh токена не найден в кеше"""
    msg = f'Токен не найден'
    log_api(request, exc, msg)
    content = get_response_content(request, msg)
    return JSONResponse(
        status_code=status.HTTP_400_BAD_REQUEST,
        content=content
    )

async def psw_error_master_key(request: Request, exc: CheckMasterPswError) -> JSONResponse:
    """Обработка неверного ввода мастер пароля"""
    msg = f'Неверный пароль'
    log_api(request, exc, msg)
    content = get_response_content(request, msg)
    return JSONResponse(
        status_code=status.HTTP_401_UNAUTHORIZED,
        content=content
    )