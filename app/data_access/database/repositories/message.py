from models.message import PrivateMessageOrm
from .base import BaseRepositoryGet, BaseRepositorySave
from app.shared.dtos import (
    PrivateMessageDtoGetResponse,
    PrivateMessageDtoPostRequest,
)


class PrivateMessageRepository(
    BaseRepositoryGet[PrivateMessageDtoGetResponse, PrivateMessageOrm],
    BaseRepositorySave[PrivateMessageDtoGetResponse, PrivateMessageDtoPostRequest, PrivateMessageOrm]
):
    """Репозиторий для работы с данными приватных сообщений"""
    model: type[PrivateMessageOrm] = PrivateMessageOrm
    dto_response: type[PrivateMessageDtoGetResponse] = PrivateMessageDtoGetResponse