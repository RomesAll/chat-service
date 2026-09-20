import secrets
from functools import wraps
from typing import Self, Any
from uuid import UUID
from pymongo import MongoClient
from pymongo.errors import ConnectionFailure
from app.business_logic.singleton import Singleton
from datetime import datetime, timezone, timedelta
from app.shared.log_config import LogMixin


class InviteUrlGenerateService(Singleton, LogMixin):
    """Класс адаптер для генерации и проверки ссылок для добавления в комнату mongodb"""
    def __init__(self, url: str):
        super().__init__()
        with self._lock:
            if hasattr(self, '_is_init'):
                return
            self._is_init = True
            self.url = url
            self.client = MongoClient(url)
            self._init_args()

    def _init_args(self):
        self.db = self.client['invites_db']
        self.collection = self.db['invites_collection']
        self.collection.create_index('token', unique=True)
        self.collection.create_index("expires_at", expireAfterSeconds=0)
        self.collection.create_index("room_id")

    @staticmethod
    def exception_handler(func):
        """Декоратор для обработки ошибок"""
        @wraps(func)
        def wrapper(self: Self, *args, **kwargs):
            try:
                result = func(self, *args, **kwargs)
                return result
            except ConnectionFailure:
                self.log_warning('Не удалось выполнить действие с аудит-сервисом, т.к. он неактивен')
                raise
            except Exception as e:
                self.log_warning(f'Не удалось выполнить действие с аудит-сервисом из-за неизвестной ошибки, {e}')
                raise
        return wrapper

    @exception_handler
    def generate_url(
            self,
            room_id: UUID,
            created_by: str,
            max_uses: int | None = None,
            hours: int = 24
    ) -> tuple[str, Any]:
        token = secrets.token_urlsafe(32)
        invite_doc = {
            "token": token,
            "room_id": str(room_id),
            "created_by": created_by,
            "expires_at": datetime.now(tz=timezone.utc) + timedelta(hours=hours),
            "max_uses": max_uses,
            "uses_count": 0,
            "is_revoked": False
        }
        self.collection.insert_one(invite_doc)
        return token, invite_doc['expires_at'].isoformat()

    @exception_handler
    def check_token_invite_exist(self, token: str) -> tuple[Any, UUID]:
        invite = self.collection.find_one({
            'token': token,
            'is_revoked': False,
            'expires_at': {'$gt': datetime.now(tz=timezone.utc)}
        })
        if not invite:
            raise ValueError("Ссылка недействительна или истекла")
        return invite['_id'], invite['room_id']

    @exception_handler
    def increment_uses_count(self, document_id):
        result = self.collection.update_one(
            {
                "_id": document_id,
                "$or": [
                    {"max_uses": None},
                    {"$expr": {"$lt": ["$uses_count", "$max_uses"]}},
                ],
            },
            {"$inc": {"uses_count": 1}},
        )
        if result.modified_count == 0:
            raise ValueError("Лимит использований исчерпан")
        return result.modified_count