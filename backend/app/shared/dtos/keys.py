from pydantic import ConfigDict, BaseModel
from .base import BaseDtoGetResponse, BaseDtoPostDeleteRequest


class PublicKeyDtoGet(BaseModel):
    """DTO для хранения публичного ключа с информацией о версии"""
    version: str
    public_key: str


class PublicKeyDtoCreate(BaseDtoPostDeleteRequest):
    """DTO для добавления нового публичного ключа"""
    user_id: str
    version: str
    public_key: str
    is_current: bool = True


class PrivateKeyDtoGet(BaseModel):
    """DTO для хранения зашифрованной коллекции приватных ключей"""
    version: str
    private_key: str


class PrivateKeyDtoCreate(BaseDtoPostDeleteRequest):
    """DTO для создания зашифрованной коллекции приватных ключей"""
    user_id: str
    version: str
    private_key: str


class PublicKeyRequest(BaseModel):
    version: str
    public_key: str


class PrivateKeyRequest(BaseModel):
    version: str
    private_key: str