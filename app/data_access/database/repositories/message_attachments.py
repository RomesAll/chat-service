from app.data_access.database.models import MessageAttachments
from .base import BaseRepositoryGet, BaseRepositorySave
from app.shared.dtos import (
    MessageAttachmentsDtoGetResponse,
    MessageAttachmentsDtoPostRequest,
)


class MessageAttachmentsRepository(
    BaseRepositoryGet[MessageAttachmentsDtoGetResponse, MessageAttachments],
    BaseRepositorySave[MessageAttachmentsDtoGetResponse, MessageAttachmentsDtoPostRequest, MessageAttachments]
):
    """Репозиторий для работы с данными файлов"""
    model: type[MessageAttachments] = MessageAttachments
    dto_response: type[MessageAttachmentsDtoGetResponse] = MessageAttachmentsDtoGetResponse