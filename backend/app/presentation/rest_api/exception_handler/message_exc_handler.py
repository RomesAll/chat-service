from fastapi import Request, status
from starlette.responses import JSONResponse
from app.business_logic.exceptions import PermissionFileDownError, UserNotFoundInRoom
from app.presentation.rest_api.exception_handler.base import log_api, get_response_content


async def permission_file_down_error(request: Request, exc: PermissionFileDownError) -> JSONResponse:
    """Обработка отсутствия разрешения на скачивания файла"""
    msg = f'У пользователя {exc.user_id} нет прав на доступ к файлу {exc.file_id}'
    log_api(request, exc, msg)
    content = get_response_content(request, msg)
    return JSONResponse(
        status_code=status.HTTP_403_FORBIDDEN,
        content=content
    )

async def file_not_found_error(request: Request, exc: FileNotFoundError) -> JSONResponse:
    """Обработка ошибок поиска файлов"""
    msg = f'Не удалось найти файл {exc.filename}'
    log_api(request, exc, msg)
    content = get_response_content(request, msg)
    return JSONResponse(
        status_code=status.HTTP_403_FORBIDDEN,
        content=content
    )

async def user_not_found_in_room(request: Request, exc: UserNotFoundInRoom) -> JSONResponse:
    """Обработка ошибок отсутствия пользователя в комнате"""
    msg = f'Не удалось найти пользователя {exc.user_id} в комнате {exc.room_id}'
    log_api(request, exc, msg)
    content = get_response_content(request, msg)
    return JSONResponse(
        status_code=status.HTTP_404_NOT_FOUND,
        content=content
    )