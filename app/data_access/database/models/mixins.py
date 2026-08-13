from uuid import UUID
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy import func, String
from sqlalchemy.types import UUID as PUUID, DateTime
from datetime import datetime


class IdMixin:
    """Миксин для id с uuid типом"""
    id: Mapped[UUID] = mapped_column(PUUID, primary_key=True, unique=True)

class StringIdMixin:
    """Миксин для id с str типом"""
    id: Mapped[str] = mapped_column(String(40), primary_key=True, unique=True)

class TimeStampMixin:
    """Миксин для временных меток"""
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        server_onupdate=func.now(),
        nullable=False
    )