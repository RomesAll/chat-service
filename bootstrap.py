from app.shared.config import BaseConfig
from app.data_access.database.database import Database
from app.business_logic.active_session.active_session_manager import ActiveSessionManager
from app.business_logic.auth.jwt_manager import JWTAccessManager, JWTRefreshManager
from app.business_logic.cache.jwt_white_list import JWTWhiteListCache
from app.business_logic.cache.session_key_storage import SessionKeyStorage
from app.business_logic.encryption.asymmetric import AsymmetricEncrypt
from datetime import timedelta
import redis


class Bootstrap:
    """Bootstrap для инициализации инфраструктуры"""
    def __init__(self, config: BaseConfig):
        self._active_session_manager: ActiveSessionManager | None = None
        self._postgres_db: Database | None = None
        self._jwt_white_list: JWTWhiteListCache | None = None
        self._session_key_storage: SessionKeyStorage | None = None
        self._asymmetric_encrypt: AsymmetricEncrypt | None = None
        self.config = config

    def init_app(self):
        """Инициализация приложения"""
        self._init_cache_config()
        self._init_jwt_tokens()
        self._init_database()
        self._init_active_session()
        self._init_app_keys()

    def _init_cache_config(self):
        """Инициализация кеша"""
        self._jwt_white_list = JWTWhiteListCache(
            client=redis.from_url(self.config.redis.url)
        )
        self._session_key_storage = SessionKeyStorage(
            client=redis.from_url(self.config.redis.url)
        )

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
    def jwt_white_list(self) -> JWTWhiteListCache:
        if not self._jwt_white_list:
            raise Exception
        return self._jwt_white_list

    @property
    def session_key_storage(self) -> SessionKeyStorage:
        if not self._session_key_storage:
            raise Exception
        return self._session_key_storage

    @property
    def asymmetric_encrypt(self) -> AsymmetricEncrypt:
        if not self._asymmetric_encrypt:
            raise Exception
        return self._asymmetric_encrypt


bootstrap: Bootstrap | None = None

def get_bootstrap() -> Bootstrap:
    if not bootstrap:
        raise Exception
    return bootstrap

def set_bootstrap(config: BaseConfig):
    global bootstrap
    bootstrap = Bootstrap(config)
    bootstrap.init_app()
