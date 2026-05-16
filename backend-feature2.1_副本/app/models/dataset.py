from __future__ import annotations

from sqlalchemy import String, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base
from app.models.common import TimestampMixin, UUIDPrimaryKeyMixin


class Dataset(Base, UUIDPrimaryKeyMixin, TimestampMixin):
    __tablename__ = "datasets"

    name: Mapped[str] = mapped_column(String(120), nullable=False)
    description: Mapped[str | None] = mapped_column(Text(), nullable=True)

    # for MVP: store JSONL content directly; later can store file path / object storage uri
    jsonl: Mapped[str] = mapped_column(Text(), nullable=False)
