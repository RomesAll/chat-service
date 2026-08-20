from dtos import BaseDtoGetResponse, BaseDtoPostDeleteRequest


class PublicKeyDtoGet(BaseDtoGetResponse):
    """DTO для хранения публичного ключа с информацией о версии"""
    id: int
    version: str
    public_key: str


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
    user_id: str
    encrypted_private_keys: str


class PrivateKeyDtoCreate(BaseDtoPostDeleteRequest):
    """DTO для создания зашифрованной коллекции приватных ключей"""
    id: int | None = None
    user_id: str
    encrypted_private_keys: str