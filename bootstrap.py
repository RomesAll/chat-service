from app.shared.config import BaseConfig
from app.data_access.database.database import Database
from app.business_logic.active_session.active_session_manager import ActiveSessionManager
from app.business_logic.auth.jwt_manager import JWTAccessManager, JWTRefreshManager
from app.business_logic.encryption.asymmetric import AsymmetricEncrypt
from app.business_logic.audit_service import AuditService
from app.business_logic.cache.redis_cache import RedisCache
from datetime import timedelta
from app.business_logic.sender_service import EmailSender, SMSSender
from app.shared.dtos.auth import SendType


class Bootstrap:
    """Bootstrap для инициализации инфраструктуры"""
    def __init__(self, config: BaseConfig):
        self._active_session_manager: ActiveSessionManager | None = None
        self._postgres_db: Database | None = None
        self._redis_cache: RedisCache | None = None
        self._asymmetric_encrypt: AsymmetricEncrypt | None = None
        self._audit_service: AuditService | None = None
        self._smtp_service: EmailSender | None = None
        self._sms_service: SMSSender | None = None
        self.config = config

    def init_app(self):
        """Инициализация приложения"""
        self._init_cache_config()
        self._init_jwt_tokens()
        self._init_database()
        self._init_active_session()
        self._init_app_keys()
        self._init_audit_service()
        self._init_smtp_service()
        self._init_sms_service()

    def _init_smtp_service(self):
        """Инициализация smtp сервиса"""
        self._smtp_service = EmailSender(
            smtp_server=self.config.smtp.server,
            port=self.config.smtp.port,
            sender_email=self.config.smtp.gmail,
            password=self.config.smtp.app_psw
        )

    def _init_sms_service(self):
        """Инициализация sms сервиса"""
        self._sms_service = SMSSender(api_token_id=self.config.sms.api_token_id)

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

    def get_sender_service_by_type(self, send_type: SendType):
        """Получение сервиса отправки по типу"""
        if send_type.EMAIL:
            return self._smtp_service
        elif send_type.PHONE:
            return self._sms_service
        raise Exception

    @property
    def sms_service(self):
        if not self._sms_service:
            raise Exception
        return self._sms_service

    @property
    def smtp_service(self):
        if not self._smtp_service:
            raise Exception
        return self._smtp_service

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
