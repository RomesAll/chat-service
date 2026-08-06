from typing import Iterable
from uuid import UUID
from sqlalchemy import inspect
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from .metaclasses import OrmManagerMeta, DynamicFields
from .mixins import IdMixin, TimeStampMixin


class BaseOrm(DeclarativeBase, IdMixin, TimeStampMixin, metaclass=OrmManagerMeta):
    """Базовый абстрактный класс для orm моделей"""
    __abstract__ = True
    Fields: DynamicFields
    is_deleted: Mapped[bool] = mapped_column(default=False)

    def to_dict(
            self,
            exclude: Iterable[str] | None = None,
            uuid_is_str: bool = False
    ) -> dict:
        """
        Метод для сериализации данных orm моделей
        :param exclude: поля, которые нужно исключить принимает объекты BaseOrm.Fields.<название поля в верхнем регистре>
        :param uuid_is_str: нужно ли преобразовывать uuid в строку
        :return: dict
        """
        serializers_data = {}
        for field in inspect(self.__class__).columns:
            if not field.name.startswith('_'):
                data = getattr(self, field.name)
                if isinstance(data, UUID) and uuid_is_str:
                    data = str(data)
                serializers_data.update({
                    field.name: data
                })

        if not exclude:
            return serializers_data
        exclude_data = {field for field in exclude}
        return {
            field : value
            for field, value in serializers_data.items()
            if field not in exclude_data
        }

    def soft_delete(self) -> bool:
        """Мягкое удаление"""
        self.is_deleted = True
        return bool(self.is_deleted)

    def soft_recovery(self) -> bool:
        """Мягкое восстановление"""
        self.is_deleted = False
        return bool(self.is_deleted)


    @classmethod
    def get_all_models(cls):
        """Получить все зарегистрированные модели (доступно через экземпляр класса)"""
        return cls.__class__.get_all_models()
