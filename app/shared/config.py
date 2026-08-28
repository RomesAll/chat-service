from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import BaseModel, SecretStr
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


class BaseConfig(BaseSettings):
    """Базовый конфиг для хранения настроек проекта"""
    postgres: PostgresqlSettings
    redis: RedisSettings
    jwtaccess: JWTSettings
    jwtrefresh: JWTSettings
    upload_file_path: str = f'{BASE_DIR}/user-files'


class DevelopConfig(BaseConfig):
    """Конфиг для разработки"""
    mode: str = 'dev'
    model_config = SettingsConfigDict(
        env_file=f'{BASE_DIR}/.dev.env',
        env_nested_delimiter='_',
        extra='ignore'
    )