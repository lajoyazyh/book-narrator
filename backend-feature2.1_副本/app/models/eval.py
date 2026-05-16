from __future__ import annotations

import enum
from datetime import datetime

from sqlalchemy import DateTime, Enum, ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base
from app.models.common import TimestampMixin, UUIDPrimaryKeyMixin


class EvalTaskStatus(str, enum.Enum):
    draft = "draft"
    running = "running"
    finished = "finished"
    failed = "failed"


class EvalRunStatus(str, enum.Enum):
    queued = "queued"
    running = "running"
    completed = "completed"
    failed = "failed"
    cancelled = "cancelled"


class EvalTask(Base, UUIDPrimaryKeyMixin, TimestampMixin):
    __tablename__ = "eval_tasks"

    name: Mapped[str] = mapped_column(String(120), nullable=False)
    status: Mapped[EvalTaskStatus] = mapped_column(Enum(EvalTaskStatus), default=EvalTaskStatus.draft)

    agent_version: Mapped[str] = mapped_column(String(120), nullable=False)
    dataset: Mapped[str] = mapped_column(String(120), nullable=False)
    remark: Mapped[str | None] = mapped_column(Text(), nullable=True)

    # JSON array of selected part codes, e.g. '[1,5,6,7]'
    selected_parts_json: Mapped[str] = mapped_column(Text(), default="[]", nullable=False)


class EvalRun(Base, UUIDPrimaryKeyMixin, TimestampMixin):
    __tablename__ = "eval_runs"

    task_id: Mapped[str] = mapped_column(String(36), ForeignKey("eval_tasks.id"), nullable=False, index=True)
    status: Mapped[EvalRunStatus] = mapped_column(Enum(EvalRunStatus), default=EvalRunStatus.queued)

    started_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    finished_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)

    result_json: Mapped[str] = mapped_column(Text(), default="{}", nullable=False)
    error_message: Mapped[str | None] = mapped_column(Text(), nullable=True)

    total_samples: Mapped[int] = mapped_column(Integer(), default=0, nullable=False)
