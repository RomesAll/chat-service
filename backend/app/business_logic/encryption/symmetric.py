from cryptography.hazmat.primitives.ciphers.aead import AESGCM
import json
import os


class SymmetricEncode:
    def __init__(self, session_key: bytes):
        self.aesgcm = AESGCM(session_key)

    def encrypt_package(self, package: dict) -> bytes:
        fresh_nonce = os.urandom(12)
        package_bytes = json.dumps(package).encode('utf-8')
        ciphertext = self.aesgcm.encrypt(fresh_nonce, package_bytes, associated_data=None)
        return fresh_nonce + ciphertext

    def decrypt_package(self, package_bytes: bytes) -> bytes:
        nonce = package_bytes[:12]
        ciphertext = package_bytes[12:]
        decrypted_bytes = self.aesgcm.decrypt(nonce, ciphertext, associated_data=None)
        package = json.loads(decrypted_bytes.decode('utf-8'))
        return package
