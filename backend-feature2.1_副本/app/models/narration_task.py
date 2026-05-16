import json
from sqlalchemy import Column, Integer, String, Text, Boolean, DateTime
from sqlalchemy.sql import func

from app.db.base import Base


class NarrationTask(Base):
    __tablename__ = "narration_tasks"

    id = Column(Integer, primary_key=True, index=True)

    task_id = Column(String(64), unique=True, index=True, nullable=False)

    book_id = Column(String(128), index=True, nullable=True)
    book_title = Column(String(255), nullable=True)
    filename = Column(String(255), nullable=True)

    mode = Column(String(32), nullable=False, default="page")
    style = Column(String(64), nullable=True)
    voice = Column(String(64), nullable=True)

    start_page = Column(Integer, nullable=True)
    end_page = Column(Integer, nullable=True)
    chapter_number = Column(Integer, nullable=True)

    task_instruction = Column(Text, nullable=True)
    custom_text = Column(Text, nullable=True)

    script = Column(Text, nullable=True)
    audio_urls_json = Column(Text, nullable=True)

    status = Column(String(32), nullable=False, default="success")
    error_message = Column(Text, nullable=True)

    remark = Column(Text, nullable=True)
    favorite = Column(Boolean, default=False)

    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    def get_audio_urls(self) -> list[str]:
        if not self.audio_urls_json:
            return []
        try:
            return json.loads(self.audio_urls_json)
        except Exception:
            return []