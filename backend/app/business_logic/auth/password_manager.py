import bcrypt
from pydantic import SecretStr


class PasswordManager:
    """Класс менеджер для хеширования и проверки паролей"""
    @classmethod
    def hash_password(cls, psw: SecretStr) -> bytes:
        """Хеширование пароля"""
        salt = bcrypt.gensalt()
        hashed_psw = bcrypt.hashpw(psw.get_secret_value().encode(), salt)
        return hashed_psw

    @classmethod
    def check_equal_psw(cls, password: SecretStr, hashed_password: bytes) -> bool:
        """Проверка паролей"""
        result: bool = bcrypt.checkpw(
            password.get_secret_value().encode(),
            hashed_password
        )
        return result