from fastapi import Request, status
from starlette.responses import JSONResponse
from app.data_access.exceptions import RecordNotFound, UniqueViolationError, NotNullViolationError


async def room_not_found(request: Request, exc: RecordNotFound) -> JSONResponse:
    """Обработка неудачного поиска комнаты"""
    return JSONResponse(
        status_code=status.HTTP_404_NOT_FOUND,
        content={
            'error': 'Комната не найден',
            'detail': f'Не удалось найти информацию о комнате {exc.id}'
        }
    )

async def room_is_exists(request: Request, exc: UniqueViolationError) -> JSONResponse:
    """Обработка нарушений уникальности для комнаты"""
    return JSONResponse(
        status_code=status.HTTP_409_CONFLICT,
        content={
            'error': 'Комната уже существует',
            'detail': 'Комната с такими данными уже существует'
        }
    )

async def room_missing_info(request: Request, exc: NotNullViolationError) -> JSONResponse:
    """Обработка нарушений обязательных полей"""
    return JSONResponse(
        status_code=status.HTTP_400_BAD_REQUEST,
        content={
            'error': 'Заполните обязательные поля для создания/обновления комнаты',
            'detail': ''
        }
    )