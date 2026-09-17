import logging
from functools import wraps
from app.shared.dtos import AuditPostDto
from bootstrap import get_bootstrap
from app.shared.config import config

logger = logging.getLogger(config.log_info.log_name)


def audit_system(func):
    """Декоратор для синхронных функций"""
    @wraps(func)
    def wrapper(self, *args, **kwargs):
        dto_audit = self.__dict__.get('dto_audit')
        try:
            result = func(self, *args, **kwargs)
            if dto_audit:
                dto_audit.result = result
            return result
        except Exception as e:
            if dto_audit:
                dto_audit.successfully = False
                dto_audit.exceptions = str(e)
            raise
        finally:
            if dto_audit:
                _save_audit(dto_audit)
    return wrapper


def audit_system_async(func):
    """Декоратор для асинхронных функций"""
    @wraps(func)
    async def wrapper(self, *args, **kwargs):
        dto_audit = self.__dict__.get('dto_audit')
        try:
            result = await func(self, *args, **kwargs)
            if dto_audit:
                dto_audit.result = result
            return result
        except Exception as e:
            if dto_audit:
                dto_audit.successfully = False
                dto_audit.exceptions = str(e)
            raise
        finally:
            if dto_audit:
                _save_audit(dto_audit)
    return wrapper


def _save_audit(dto_audit: AuditPostDto):
    try:
        get_bootstrap().audit_service.add(dto_audit)
    except Exception as e:
        logger.error(f"Ошибка записи в аудит-сервис: {e}", exc_info=True)