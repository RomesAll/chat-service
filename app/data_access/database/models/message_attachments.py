from enum import Enum
from uuid import UUID
from sqlalchemy import Enum as SAEnum
from sqlalchemy.orm import Mapped, mapped_column
from .base import BaseOrm
from .mixins import IdMixin
from sqlalchemy.dialects.postgresql import UUID as PG_UUID


class MimeType(str, Enum):
    # ===== Изображения =====
    PNG = "image/png"
    JPEG = "image/jpeg"
    GIF = "image/gif"
    BMP = "image/bmp"
    WEBP = "image/webp"
    SVG = "image/svg+xml"
    TIFF = "image/tiff"
    ICO = "image/vnd.microsoft.icon"
    AVIF = "image/avif"

    # ===== Текст =====
    PLAIN = "text/plain"
    HTML = "text/html"
    CSS = "text/css"
    CSV = "text/csv"
    XML = "text/xml"
    MARKDOWN = "text/markdown"

    # ===== JSON =====
    JSON = "application/json"

    # ===== PDF =====
    PDF = "application/pdf"

    # ===== JavaScript / TypeScript =====
    JS = "application/javascript"
    TS = "application/typescript"

    # ===== Офисные документы =====
    DOC = "application/msword"
    DOCX = "application/vnd.openxmlformats-officedocument.wordprocessingml.document"
    XLS = "application/vnd.ms-excel"
    XLSX = "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    PPT = "application/vnd.ms-powerpoint"
    PPTX = "application/vnd.openxmlformats-officedocument.presentationml.presentation"
    ODT = "application/vnd.oasis.opendocument.text"
    ODS = "application/vnd.oasis.opendocument.spreadsheet"
    ODP = "application/vnd.oasis.opendocument.presentation"

    # ===== Архивы =====
    ZIP = "application/zip"
    RAR = "application/vnd.rar"
    GZIP = "application/gzip"
    TAR = "application/x-tar"
    SEVEN_Z = "application/x-7z-compressed"

    # ===== Видео =====
    MP4 = "video/mp4"
    WEBM = "video/webm"
    OGG_VIDEO = "video/ogg"
    QUICKTIME = "video/quicktime"
    AVI = "video/x-msvideo"
    MPEG = "video/mpeg"

    # ===== Аудио =====
    MP3 = "audio/mpeg"
    WAV = "audio/wav"
    OGG_AUDIO = "audio/ogg"
    FLAC = "audio/flac"
    AAC = "audio/aac"
    MIDI = "audio/midi"


class MessageAttachments(BaseOrm, IdMixin):
    """Orm модель для приватных сообщений"""
    __tablename__ = 'message_attachments'
    message_id: Mapped[UUID] = mapped_column(
        PG_UUID(as_uuid=True),
        # ForeignKey("private_message.id", ondelete="CASCADE"),
        nullable=False
    )
    file_name: Mapped[str]
    file_path: Mapped[str]
    file_size: Mapped[int]
    mime_type: Mapped[MimeType] = mapped_column(
        SAEnum(MimeType),
        nullable=False
    )

    def __repr__(self):
        base_repr = super().__repr__()
        result = base_repr.replace(')>', f', id={self.id}, file_name={self.file_name}, file_size={self.file_size})>')
        return result