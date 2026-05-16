from typing import Optional
from pydantic import BaseModel


class NarrationTaskUpdate(BaseModel):
    remark: Optional[str] = None
    favorite: Optional[bool] = None


class NarrationTaskOut(BaseModel):
    task_id: str

    book_id: Optional[str] = None
    book_title: Optional[str] = None
    filename: Optional[str] = None

    mode: Optional[str] = None
    style: Optional[str] = None
    voice: Optional[str] = None

    start_page: Optional[int] = None
    end_page: Optional[int] = None
    chapter_number: Optional[int] = None

    task_instruction: Optional[str] = None
    custom_text: Optional[str] = None

    script: Optional[str] = None
    audio_urls: list[str] = []

    status: str = "success"
    error_message: Optional[str] = None

    remark: Optional[str] = None
    favorite: bool = False

    created_at: Optional[str] = None
    updated_at: Optional[str] = None