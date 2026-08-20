from sqlalchemy import update, select, insert
from sqlalchemy.sql.elements import and_
from dtos.keys import PublicKeyDtoCreate, PublicKeyDtoGet, PrivateKeyDtoCreate, PrivateKeyDtoGet
from app.data_access.database.models import UserPublicKey, UserPrivateKey
from exceptions import RecordNotFound
from .base import BaseRepositoryGet, BaseRepositorySave


class PublicKeyRepository(
    BaseRepositoryGet[PublicKeyDtoGet, UserPublicKey],
    BaseRepositorySave[PublicKeyDtoGet, PublicKeyDtoCreate, UserPublicKey],
):
    """Репозиторий для работы с публичными ключами пользователя"""
    model: type[UserPublicKey] = UserPublicKey
    dto_response: type[PublicKeyDtoGet] = PublicKeyDtoGet

    def get_by_id(self, user_id: str) -> PublicKeyDtoGet:
        """Получение текущего публичного ключа пользователя по id пользователя"""
        stmt = (
            select(self.model).
            where(
                and_(
                    self.model.user_id == user_id,
                    self.model.is_current == True
                )
            )
        )
        result: UserPublicKey | None = self.session.execute(stmt).scalar_one_or_none()
        if not result:
            raise RecordNotFound(user_id)
        return self.dto_response(**result.to_dict())

    def save(self, key_info: PublicKeyDtoCreate) -> None:
        """Сохранение нового публичного ключа пользователя"""
        orm_object= self.model(
            user_id = key_info.user_id,
            version = key_info.version,
            public_key = key_info.public_key,
            is_current = True
        )
        stmt = (
            update(self.model).
            where(self.model.user_id == key_info.user_id).
            values(is_current = False)
        )
        self.session.execute(stmt)
        self.session.add(orm_object)
        self.session.flush()


class PrivateKeyRepository(
    BaseRepositoryGet[PrivateKeyDtoGet, UserPrivateKey],
    BaseRepositorySave[PrivateKeyDtoGet, PrivateKeyDtoCreate, UserPrivateKey],
):
    """Репозиторий для работы с приватными ключами пользователя"""
    model: type[UserPrivateKey] = UserPrivateKey
    dto_response: type[PrivateKeyDtoGet] = PrivateKeyDtoGet

    def get_by_id(self, user_id: str) -> PrivateKeyDtoGet:
        """Получение зашифрованной коллекции приватных ключей пользователя по id пользователя"""
        stmt = (
            select(self.model).
            where(self.model.user_id == user_id)
        )
        result: UserPrivateKey | None = self.session.execute(stmt).scalar_one_or_none()
        if not result:
            raise RecordNotFound(user_id)
        return self.dto_response(**result.to_dict())

    def save(self, key_info: PrivateKeyDtoCreate) -> None:
        """Сохранение зашифрованной коллекции приватных ключей пользователя"""
        is_exists = self.check_exist(key_info.user_id)
        if not is_exists:
            stmt_update_or_insert = (
                insert(self.model).
                values(user_id=key_info.user_id, encrypted_private_keys=key_info.encrypted_private_keys)
            )
        else:
            stmt_update_or_insert = (
                update(self.model).
                where(self.model.user_id == key_info.user_id).
                values(encrypted_private_keys=key_info.encrypted_private_keys)
            )
        self.session.execute(stmt_update_or_insert)
