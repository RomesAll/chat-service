from fastapi import Request
import logging, re
from fastapi.encoders import jsonable_encoder
from fastapi.exceptions import RequestValidationError
from starlette import status
from starlette.responses import JSONResponse

api_logger = logging.getLogger('api_logger')

def get_response_content(
        request: Request,
        msg = 'Ошибка сервиса, попробуйте выполнить действие позже'
):
    """Получение данных для ответа на запрос"""
    content = {
        'error': msg,
        'detail': {
            'method': request.method,
            'url': str(request.url),
            'headers': dict(request.headers),
            'client_ip': request.client.host,
            'user_agent': request.headers.get('user-agent')
        }
    }
    return content

def log_api(request: Request, exc: Exception, base_msg: str):
    """Логирование api ошибок"""
    result_message = f'{base_msg} для client_ip: %s (%s) на адрес: %s (метод %s), оригинал: \n %s'
    api_logger.error(
        result_message,
        request.client.host,
        request.headers.get('user-agent'),
        request.url,
        request.method,
        exc
    )


async def validation_exception_handler(request: Request, exc: RequestValidationError):
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content=jsonable_encoder({
            'message': 'Неверный формат переданных данных',
            "detail": exc.errors(),
            "body": exc.body,
        }),
    )