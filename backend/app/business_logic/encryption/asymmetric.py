from cryptography.hazmat.primitives import serialization, hashes
from cryptography.hazmat.primitives.asymmetric import rsa, padding
from app.shared.dtos.encrypt import AsymmetricKeys
import base64


class AsymmetricEncrypt:
    def __init__(self):
        keys = self._generate_keys()
        self._private_key = keys.private_key
        self._public_key = keys.public_key

    @staticmethod
    def _generate_keys() -> AsymmetricKeys:
        private_key = rsa.generate_private_key(
            public_exponent=65537,
            key_size=2048
        )
        public_key = private_key.public_key()
        return AsymmetricKeys(
            private_key=private_key,
            public_key=public_key
        )

    def get_public_key(self) -> str:
        return self._public_key.public_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PublicFormat.SubjectPublicKeyInfo
        ).decode('utf-8')

    def decoding_session_key(self, encrypt_session_key: str) -> bytes:
        encrypted_bytes = base64.b64decode(encrypt_session_key)
        decrypted = self._private_key.decrypt(
            encrypted_bytes,
            padding.OAEP(
                mgf=padding.MGF1(algorithm=hashes.SHA256()),
                algorithm=hashes.SHA256(),
                label=None
            )
        )
        result = base64.b64decode(decrypted)
        return result