from functools import wraps
from typing import Any, Self
from pymongo import MongoClient
from pymongo.errors import ConnectionFailure
from app.business_logic.singleton import Singleton
from app.shared.dtos import AuditPostDto
from log_config import LogMixin
from datetime import datetime, timezone


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
            self.check_connection()
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
        def wrapper(self, *args, **kwargs):
            inst: Self = args[0]
            inst.check_connection()
            if self._audit_is_active and not hasattr(self, 'db'):
                inst._init_args()
            if not self._audit_is_active:
                self.log_warning('Не удалось выполнить действие с аудит-сервисом, т.к. он неактивен')
                return None
            return func(self, *args, **kwargs)
        return wrapper

    def check_connection(self):
        """Проверка подключения с аудит-сервисом"""
        try:
            self.client.admin.command('ping')
            self.log_info('Подключение к аудит сервису mongodb успешно установлено')
            self._audit_is_active = True
        except ConnectionFailure:
            self.log_warning('Ошибка подключение к аудит сервису')
            self._audit_is_active = False

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
        """
        audit_data = dto_request.model_dump()
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