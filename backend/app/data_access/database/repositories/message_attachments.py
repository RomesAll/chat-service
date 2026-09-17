from typing import Sequence
from uuid import UUID
from sqlalchemy import select
from app.data_access.database.models import MessageAttachments
from .base import BaseRepositoryGet, BaseRepositorySave, BaseRepositoryDelete
from app.shared.dtos import (
    MessageAttachmentsDtoGetResponse,
    MessageAttachmentsDtoPostRequest,
)
from app.data_access.exceptions import RecordNotFound


class MessageAttachmentsRepository(
    BaseRepositoryGet[MessageAttachmentsDtoGetResponse, MessageAttachments],
    BaseRepositorySave[MessageAttachmentsDtoGetResponse, MessageAttachmentsDtoPostRequest, MessageAttachments],
    BaseRepositoryDelete[MessageAttachmentsDtoGetResponse, MessageAttachments]
):
    """Репозиторий для работы с данными файлов"""
    model: type[MessageAttachments] = MessageAttachments
    dto_response: type[MessageAttachmentsDtoGetResponse] = MessageAttachmentsDtoGetResponse

    def get_message_files(self, message_id: UUID) -> list[MessageAttachmentsDtoGetResponse]:
        """Получить все файлы в сообщении"""
        stmt = select(self.model).where(self.model.message_id == message_id)
        files = self.session.execute(stmt).scalars().all()
        if not files:
            raise RecordNotFound(message_id)
        results = []
        for file in files:
            results.append(self.dto_response(**file.to_dict()))
        return results

    def get_message_id_files(self, message_id: UUID) -> Sequence[UUID]:
        """Получить id файлов в сообщении"""
        stmt = select(self.model.id).where(self.model.message_id == message_id)
        result = self.session.execute(stmt).scalars().all()
        return result