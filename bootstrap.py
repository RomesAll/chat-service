from app.shared.config import BaseConfig
from app.data_access.database.database import Database
from app.business_logic.active_session.active_session_manager import ActiveSessionManager
from app.business_logic.auth.jwt_manager import JWTAccessManager, JWTRefreshManager
from app.business_logic.encryption.asymmetric import AsymmetricEncrypt
from app.business_logic.audit_service import AuditService
from app.business_logic.cache.redis_cache import RedisCache
from datetime import timedelta


class Bootstrap:
    """Bootstrap для инициализации инфраструктуры"""
    def __init__(self, config: BaseConfig):
        self._active_session_manager: ActiveSessionManager | None = None
        self._postgres_db: Database | None = None
        self._redis_cache: RedisCache | None = None
        self._asymmetric_encrypt: AsymmetricEncrypt | None = None
        self._audit_service: AuditService | None = None
        self.config = config

    def init_app(self):
        """Инициализация приложения"""
        self._init_cache_config()
        self._init_jwt_tokens()
        self._init_database()
        self._init_active_session()
        self._init_app_keys()
        self._init_audit_service()

    def _init_audit_service(self):
        """Инициализация аудит-сервиса"""
        self._audit_service = AuditService(url=self.config.mongodb.url)

    def _init_cache_config(self):
        """Инициализация кеша"""
        self._redis_cache = RedisCache(url=self.config.redis.url)

    def _init_jwt_tokens(self):
        """Инициализация jwt токенов"""
        JWTAccessManager.ALGORITHM = self.config.jwtaccess.algorithm
        JWTAccessManager.EXPIRES_DELTA = timedelta(
            minutes=self.config.jwtaccess.expiresdelta
        )
        JWTAccessManager.SECRET_KEY = self.config.jwtaccess.secretkey

        JWTRefreshManager.ALGORITHM = self.config.jwtrefresh.algorithm
        JWTRefreshManager.EXPIRES_DELTA = timedelta(
            days=self.config.jwtrefresh.expiresdelta
        )
        JWTRefreshManager.SECRET_KEY = self.config.jwtrefresh.secretkey

    def _init_database(self):
        """Инициализация базы данных"""
        self._postgres_db = Database(self.config.postgres.url)

    def _init_active_session(self):
        """Инициализация активной сессии"""
        self._active_session_manager = ActiveSessionManager()

    def _init_app_keys(self):
        """Инициализация ключей приложения"""
        self._asymmetric_encrypt = AsymmetricEncrypt()

    @property
    def database(self) -> Database:
        if not self._postgres_db:
            raise Exception
        return self._postgres_db

    @property
    def active_session_manager(self) -> ActiveSessionManager:
        if not self._active_session_manager:
            raise Exception
        return self._active_session_manager

    @property
    def redis_cache(self) -> RedisCache:
        if not self._redis_cache:
            raise Exception
        return self._redis_cache

    @property
    def asymmetric_encrypt(self) -> AsymmetricEncrypt:
        if not self._asymmetric_encrypt:
            raise Exception
        return self._asymmetric_encrypt

    @property
    def audit_service(self):
        if not self._asymmetric_encrypt:
            raise Exception
        return self._audit_service


bootstrap: Bootstrap | None = None

def get_bootstrap() -> Bootstrap:
    if not bootstrap:
        raise Exception
    return bootstrap

def set_bootstrap(config: BaseConfig):
    global bootstrap
    bootstrap = Bootstrap(config)
    bootstrap.init_app()
