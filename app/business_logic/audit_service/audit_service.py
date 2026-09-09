from functools import wraps
from typing import Self
from pymongo import MongoClient
from pymongo.errors import ConnectionFailure, PyMongoError
from app.business_logic.singleton import Singleton
from app.shared.dtos import AuditPostDto
from datetime import datetime, timezone
from log_config import LogMixin


class AuditService(Singleton, LogMixin):
    """Класс адаптер для хранения аудита системы в mongodb"""
    def __init__(self, url: str):
        super().__init__()
        with self._lock:
            if hasattr(self, '_is_init'):
                return
            self._is_init = True
            self.url = url
            self._audit_is_active = False
            self.client = MongoClient(url)
            try:
                self._check_connection()
            except PyMongoError:
                self._audit_is_active = False
            if self._audit_is_active:
                self._init_args()

    def _init_args(self):
        self.db = self.client['audit_db']
        self.collection = self.db['audit_collection']
        self.collection.create_index("timestamp", expireAfterSeconds=604800)

    @staticmethod
    def check_audit_active(func):
        """Декоратор для автоматической проверки активности БД перед вызовом метода"""
        @wraps(func)
        def wrapper(self: Self, *args, **kwargs):
            try:
                if not self._audit_is_active:
                    self._check_connection()
                    if self._audit_is_active and not hasattr(self, 'db'):
                        self._init_args()
                return func(self, *args, **kwargs)
            except ConnectionFailure:
                self.log_warning('Не удалось выполнить действие с аудит-сервисом, т.к. он неактивен')
                self._audit_is_active = False
            except Exception as e:
                self.log_warning(f'Не удалось выполнить действие с аудит-сервисом из-за неизвестной ошибки, {e}')
        return wrapper

    def _check_connection(self):
        """Проверка подключения с аудит-сервисом"""
        self.client.admin.command('ping')
        self.log_info('Подключение к аудит сервису mongodb успешно установлено')
        self._audit_is_active = True

    @check_audit_active
    def add(self, dto_request: AuditPostDto, **kwargs):
        """
        Добавление данных в аудит-сервис. Модель данных по умолчанию:\n
        - user_id
        - action
        - target_api
        - timestamp
        - ip
        - user_agent
        - successfully
        - exceptions
        """
        audit_data = dto_request.model_dump(mode='json')
        for key, value in kwargs.items():
            audit_data[key] = value
        audit_data['created_at'] = datetime.now(tz=timezone.utc)
        result = self.collection.insert_one(audit_data)
        self.log_debug(f"ID добавленного документа: {result.inserted_id} в аудит-сервис")

    @check_audit_active
    def clear_one_week(self):
        """(Осторожно!) Очисть документы по прошествию недели"""
        result = self.collection.delete_many({})
        self.log_info(f"Успешно удалено документов: {result.deleted_count}")