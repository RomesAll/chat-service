from uuid import UUID
from models.message_attachments import MimeType
from pathlib import Path
from .base import (
    BaseDtoGetResponse,
    BaseDtoPostDeleteRequest,
)


class MessageAttachmentsDtoGetResponse(BaseDtoGetResponse):
    """User DTO для операции получения (Get) информации о файлах"""
    message_id: UUID
    file_name: str
    file_path: Path
    file_size: int
    mime_type: MimeType


class MessageAttachmentsDtoPostRequest(BaseDtoPostDeleteRequest):
    """User DTO для операции добавления (Post) информации о файлах"""
    message_id: UUID
    file_name: str
    file_path: str
    file_size: int
    mime_type: MimeType


class MessageAttachmentsDeleteRequest(BaseDtoPostDeleteRequest):
    """User DTO для операции удаления (Delete) информации о файлах"""
    pass