from fastapi import Request, status
from starlette.responses import JSONResponse
from app.business_logic.exceptions import VerifyCodeStorageError, VerifyCodeInCorrect
from app.data_access.exceptions import RecordNotFound, UniqueViolationError, NotNullViolationError


async def user_not_found(request: Request, exc: RecordNotFound) -> JSONResponse:
    """Обработка неудачного поиска пользователя"""
    return JSONResponse(
        status_code=status.HTTP_404_NOT_FOUND,
        content={
            'error': 'Пользователь не найден',
            'detail': f'Не удалось найти информацию о пользователе {exc.id}'
        }
    )

async def user_is_exists(request: Request, exc: UniqueViolationError) -> JSONResponse:
    """Обработка нарушений уникальности для пользователя"""
    return JSONResponse(
        status_code=status.HTTP_409_CONFLICT,
        content={
            'error': 'Пользователь уже существует',
            'detail': 'Пользователь с такими данными уже существует'
        }
    )

async def user_missing_info(request: Request, exc: NotNullViolationError) -> JSONResponse:
    """Обработка нарушений обязательных полей"""
    return JSONResponse(
        status_code=status.HTTP_400_BAD_REQUEST,
        content={
            'error': 'Заполните обязательные поля для создания/обновления пользователя',
            'detail': ''
        }
    )

async def user_verify_code_error(request: Request, exc: VerifyCodeStorageError) -> JSONResponse:
    """Ошибка подключения к кешу с кодами"""
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={
            'error': 'Сервис временно недоступен',
            'detail': ''
        }
    )

async def user_verify_code_incorrect(request: Request, exc: VerifyCodeInCorrect) -> JSONResponse:
    """Неверный код доступа"""
    return JSONResponse(
        status_code=status.HTTP_401_UNAUTHORIZED,
        content={
            'error': 'Неверный код доступа',
            'detail': ''
        }
    )