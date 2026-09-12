import bcrypt
from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import BaseModel, SecretStr, field_validator
from pathlib import Path

BASE_DIR = Path(__file__).parent.parent.parent.resolve()


class PostgresqlSettings(BaseModel):
    """Конфиг для postgresql"""
    host: str
    port: int
    db: str
    user: str
    password: SecretStr

    @property
    def url(self):
        return (f'postgresql://{self.user}:{self.password.get_secret_value()}'
                f'@{self.host}:{self.port}/{self.db}')


class RedisSettings(BaseModel):
    """Конфиг для redis"""
    host: str
    port: int
    db: int
    password: SecretStr

    @property
    def url(self):
        return (f'redis://:{self.password.get_secret_value()}'
                f'@{self.host}:{self.port}/{self.db}')


class JWTSettings(BaseModel):
    """Базовый конфиг для jwt auth"""
    algorithm: str
    expiresdelta: int
    secretkey: str


class LogLevelInfo(BaseModel):
    """Конфиг для хранения уровня логирования"""
    log_name: str
    base_log: str
    error_file_log: str
    info_file_log: str


class MongoDb(BaseModel):
    """Конфиг для mongodb"""
    host: str
    port: int
    db: str
    password: SecretStr
    username: str

    @property
    def url(self):
        return (f'mongodb://{self.username}:{self.password.get_secret_value()}'
                f'@{self.host}:{self.port}/?authSource=admin')


class SmtpConfig(BaseModel):
    """Конфиг для отправки сообщений по email"""
    server: str
    gmail: str
    app_psw: SecretStr
    port: int


class SmsConfig(BaseModel):
    """Конфиг для отправки сообщений по телефону"""
    api_token_id: SecretStr


class BaseConfig(BaseSettings):
    """Базовый конфиг для хранения настроек проекта"""
    postgres: PostgresqlSettings
    redis: RedisSettings
    jwtaccess: JWTSettings
    jwtrefresh: JWTSettings
    upload_file_path: str = f'{BASE_DIR}/user-files'
    log_info: LogLevelInfo
    mongodb: MongoDb
    smtp: SmtpConfig
    sms: SmsConfig
    app_master_key: bytes
    mode: str = ''

    @field_validator('app_master_key', mode='before')
    @classmethod
    def hash_master_key(cls, v):
        salt = bcrypt.gensalt()
        hashed = bcrypt.hashpw(v.encode(), salt)
        return hashed


class DevelopConfig(BaseConfig):
    """Конфиг для разработки"""
    mode: str = 'dev'
    model_config = SettingsConfigDict(
        env_file=f'{BASE_DIR}/.dev.env',
        env_nested_delimiter='__',
        extra='ignore'
    )

config = DevelopConfig()