import bcrypt
from pydantic import SecretStr


class PasswordManager:
    @classmethod
    def hash_password(cls, psw: SecretStr) -> bytes:
        salt = bcrypt.gensalt()
        hashed_psw = bcrypt.hashpw(psw.get_secret_value().encode(), salt)
        return hashed_psw

    @classmethod
    def check_equal_psw(cls, password: SecretStr, hashed_password: bytes) -> bool:
        result: bool = bcrypt.checkpw(
            password.get_secret_value().encode(),
            hashed_password
        )
        return result