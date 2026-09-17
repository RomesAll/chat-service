from pydantic import ConfigDict, BaseModel
from .base import BaseDtoGetResponse, BaseDtoPostDeleteRequest


class PublicKeyDtoGet(BaseDtoGetResponse):
    """DTO для хранения публичного ключа с информацией о версии"""
    id: int
    version: str
    public_key: str
    model_config = ConfigDict(extra='ignore')


class PublicKeyDtoCreate(BaseDtoPostDeleteRequest):
    """DTO для добавления нового публичного ключа"""
    id: int | None = None
    user_id: str
    version: str
    public_key: str
    is_current: bool = True


class PrivateKeyDtoGet(BaseDtoGetResponse):
    """DTO для хранения зашифрованной коллекции приватных ключей"""
    id: int
    version: str
    private_key: str
    model_config = ConfigDict(extra='ignore')


class PrivateKeyDtoCreate(BaseDtoPostDeleteRequest):
    """DTO для создания зашифрованной коллекции приватных ключей"""
    id: int | None = None
    user_id: str
    version: str
    private_key: str


class PublicKeyRequest(BaseModel):
    version: str
    public_key: str


class PrivateKeyRequest(BaseModel):
    version: str
    private_key: str