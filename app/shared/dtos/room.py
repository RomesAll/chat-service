from .base import (
    BaseDtoGetResponse,
    BaseDtoPostRequest,
    BaseDtoUpdateRequest,
    BaseDtoDeleteRequest
)


class RoomDtoGetResponse(BaseDtoGetResponse):
    """Dto модель для хранения полученной информации о группах (комнатах)"""
    name: str


class RoomDtoPostRequest(BaseDtoPostRequest):
    """Dto модель для хранения данных о группах для сохранения"""
    name: str


class RoomDtoUpdateRequest(BaseDtoUpdateRequest):
    """Dto модель для хранения данных о группах для обновления"""
    is_deleted: bool


class RoomDtoDeleteRequest(BaseDtoDeleteRequest):
    """Dto модель для хранения данных о группах для удаления"""
    pass