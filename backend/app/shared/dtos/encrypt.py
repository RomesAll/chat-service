from cryptography.hazmat.primitives.asymmetric.rsa import RSAPublicKey, RSAPrivateKey
from pydantic import BaseModel, ConfigDict


class AsymmetricKeys(BaseModel):
    """
    DTO для хранения объектов приватного и публичного
    ключа из from cryptography.hazmat.primitives.asymmetric.rsa import RSAPublicKey, RSAPrivateKey
    """
    private_key: RSAPrivateKey
    public_key: RSAPublicKey
    model_config = ConfigDict(arbitrary_types_allowed=True)
