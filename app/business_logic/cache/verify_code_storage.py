from functools import wraps
from typing import Self
from cachetools import TTLCache
from redis import Redis, AuthenticationError, ReadOnlyError, BusyLoadingError, ResponseError
from app.shared.log_config import LogMixin
from app.business_logic.exceptions import VerifyCodeStorageError


class VerifyCodeStorage(LogMixin):
    """Адаптер для хранения кодов подтверждения (при логине и регистрации) redis кеше"""
    def __init__(self, client: Redis, db: int = 2):
        self.client = client
        self.db = db
        self.client.select(db)
        self._prefix = 'verify_code'
        self.fallback = TTLCache(
            maxsize=100,
            ttl=3600
        )

    @staticmethod
    def exception_handler(func):
        """Декоратор обработки ошибок (исключений)"""
        @wraps(func)
        def wrapper(self: Self, *args, **kwargs):
            try:
                result = func(self, *args, **kwargs)
                return result
            except ConnectionError as e:
                self.log_error(f"Ошибка подключения к Redis: {e}")
                raise VerifyCodeStorageError()
            except TimeoutError as e:
                self.log_error(f"Таймаут Redis: {e}")
                raise VerifyCodeStorageError()
            except AuthenticationError as e:
                self.log_error(f"Ошибка аутентификации Redis: {e}")
                raise VerifyCodeStorageError()
            except ReadOnlyError as e:
                self.log_error(f"Redis в режиме только для чтения: {e}")
                raise VerifyCodeStorageError()
            except BusyLoadingError as e:
                self.log_error(f"Redis загружается: {e}")
                raise VerifyCodeStorageError()
            except ResponseError as e:
                self.log_error(f"Ошибка команды Redis: {e}")
                raise VerifyCodeStorageError()
            except Exception as e:
                self.log_error(f"Неизвестная ошибка redis: {e}")
                raise VerifyCodeStorageError()
        return wrapper

    @exception_handler
    def save(self, user_id: str, email: str, code: int, ttl: int = 300) -> bool:
        """
        Сохранение кода подтверждения для auth и регистрации.
        user_id - идентификатор пользователя
        email - электронный адрес пользователя
        code - числовой код подтверждения
        ttl - время жизни кода
        """
        name = f'{self._prefix}:{user_id}:{email}'
        try:
            result = bool(self.client.setex(
                name=name,
                time=ttl,
                value=code
            ))
            self.log_debug(f'Код подтверждения для пользователя {user_id} сохранен в кеш')
            return result
        except:
            self.log_warning(f'Код подтверждения для пользователя {user_id} '
                             f'не удалось сохранить в кеш, поэтому он будет сохранен во временном хранилище')
            self.fallback[name] = code
            raise

    @exception_handler
    def validate_code(self, user_id: str, email: str, code: int) -> bool:
        """
        Проверка корректности введенного кода подтверждения
        user_id - идентификатор пользователя
        email - электронный адрес пользователя
        code - числовой код подтверждения
        """
        name = f'{self._prefix}:{user_id}:{email}'
        result = self.client.get(name)
        if type(result) == bytes:
            if result.decode() == str(code):
                self.log_debug(f'Код подтверждения для пользователя {user_id} найден в кеше')
                return True
        if self.fallback.get(name, None) == code:
            self.log_debug(f'Код подтверждения для пользователя {user_id} найден во временном хранилище')
            return True
        self.log_warning(f'Код подтверждения для пользователя {user_id} не был найден')
        return False