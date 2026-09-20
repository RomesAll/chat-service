from fastapi import Request, status
from starlette.responses import JSONResponse
from app.presentation.rest_api.exception_handler.base import log_api, get_response_content
from app.data_access.exceptions import (
    DataBaseError,
    ConnectionDBError,
    DBTimeoutError,
    RecordNotFound,
    InCorrectStmtError,
    BreachIntegrity,
    UniqueViolationError,
    NotNullViolationError, ForeignKeyViolationError
)
import re


async def db_base_error(request: Request, exc: DataBaseError) -> JSONResponse:
    """Обработка базовой ошибки бд"""
    msg = 'Неизвестная ошибка базы данных'
    log_api(request, exc, msg)
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content=get_response_content(request)
    )

async def connection_db_error(request: Request, exc: ConnectionDBError) -> JSONResponse:
    """Обработка ошибок подключения к бд"""
    msg = 'Ошибка подключения к базе данных'
    log_api(request, exc, msg)
    return JSONResponse(
        status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
        content=get_response_content(request, msg)
    )

async def time_out_db_error(request: Request, exc: DBTimeoutError) -> JSONResponse:
    """Обработка ошибок тайм-аута к бд"""
    msg = 'Время подключения к базе данных превысило ожидания, попробуйте позже'
    log_api(request, exc, msg)
    return JSONResponse(
        status_code=status.HTTP_504_GATEWAY_TIMEOUT,
        content=get_response_content(request, msg)
    )

async def record_not_found_db_error(request: Request, exc: RecordNotFound) -> JSONResponse:
    """Обработка ошибок поиска данных в бд"""
    msg = f'Не удалось найти информацию о {exc.id} в базе данных'
    log_api(request, exc, msg)
    content = get_response_content(request, msg)
    content['query_params'] = dict(request.query_params)
    return JSONResponse(
        status_code=status.HTTP_404_NOT_FOUND,
        content=content
    )

async def incorrect_stmt_error(request: Request, exc: InCorrectStmtError) -> JSONResponse:
    """Обработка ошибок неверного запроса к бд"""
    msg = 'Неверно составлен запрос к базе данных'
    log_api(request, exc, msg)
    content = get_response_content(request)
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content=content
    )

async def breach_integrity_error(request: Request, exc: BreachIntegrity) -> JSONResponse:
    """Обработка ошибок связанных с нарушением целостности"""
    msg = 'Нарушение целостности данных при работе с бд'
    log_api(request, exc, msg)
    content = get_response_content(request, msg)
    return JSONResponse(
        status_code=status.HTTP_400_BAD_REQUEST,
        content=content
    )

async def unique_violation_error(request: Request, exc: UniqueViolationError) -> JSONResponse:
    """Обработка ошибок связанных с уникальностью данных"""
    detail = exc.cause.orig.diag.message_detail
    match = re.search(r'Key \(([^)]+)\)=\(([^)]+)\)', detail)
    if not match:
        return JSONResponse(
            status_code=status.HTTP_409_CONFLICT,
            content='Запись с переданными данными уже существует'
        )
    fields = [f.strip() for f in match.group(1).split(',')]
    values = [v.strip() for v in match.group(2).split(',')]
    fields_result = list(zip(fields, values))

    input_params = ', '.join([': '.join(field) for field in fields_result])
    msg = f'Запись с переданными данными ({input_params}) уже существует'
    log_api(request, exc, msg)
    content = get_response_content(request, msg)
    return JSONResponse(
        status_code=status.HTTP_409_CONFLICT,
        content=content
    )

async def foreignkey_violation_error(request: Request, exc: ForeignKeyViolationError) -> JSONResponse:
    """Обработка ошибок связанных с неверными внешними ключами"""
    msg = 'Неверно передан внешний ключ для бд'
    log_api(request, exc, msg)
    content = get_response_content(request, 'Переданы неверные данные')
    return JSONResponse(
        status_code=status.HTTP_400_BAD_REQUEST,
        content=content
    )

async def not_null_violation_error(request: Request, exc: NotNullViolationError) -> JSONResponse:
    """Обработка ошибок связанных отсутствием данных в обязательных полях"""
    column = exc.cause.diag.column_name
    msg = f'Поле (атрибут) {column} обязательно для заполнения'
    log_api(request, exc, msg)
    content = get_response_content(request, msg)
    return JSONResponse(
        status_code=status.HTTP_400_BAD_REQUEST,
        content=content
    )