import logging
from functools import wraps
from typing import Self
from app.shared.dtos import AuditPostDto
from bootstrap import get_bootstrap
from app.shared.config import config

logger = logging.getLogger(config.log_info.log_name)

def audit_system(func):
    """Декоратор для добавления данных в ауди-сервис"""
    @wraps(func)
    def wrapper(self: Self, *args, **kwargs):
        dto_audit: AuditPostDto | None = self.__dict__.get('dto_audit', None)
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

def _save_audit(dto_audit: AuditPostDto):
    try:
        get_bootstrap().audit_service.add(dto_audit)
    except Exception as e:
        logger.error(f"Ошибка записи в аудит-сервис: {e}", exc_info=True)