from uuid import UUID
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy import text
from sqlalchemy.types import UUID as PUUID, DateTime
from datetime import datetime


class IdMixin:
    """Миксин для id"""
    id: Mapped[UUID] = mapped_column(PUUID, primary_key=True, unique=True)


class TimeStampMixin:
    """Миксин для временных меток"""
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=text("TIMEZONE('UTC', now())"),
        nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=text("TIMEZONE('UTC', now())"),
        server_onupdate=text("TIMEZONE('UTC', now())"),
        nullable=False
    )