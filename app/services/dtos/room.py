from .base import (
    BaseDtoGetResponse,
    BaseDtoPostRequest
)


class RoomDtoGetResponse(BaseDtoGetResponse):
    """Dto модель для хранения полученной информации о группах (комнатах)"""
    name: str


class RoomDtoPostRequest(BaseDtoPostRequest):
    """Dto модель для хранения данных о группах для сохранения"""
    name: str


class RoomDtoUpdateRequest(RoomDtoPostRequest):
    """Dto модель для хранения данных о группах для обновления"""
    is_deleted: bool


class RoomDtoDeleteRequest(BaseDtoPostRequest):
    """Dto модель для хранения данных о группах для удаления"""
    pass