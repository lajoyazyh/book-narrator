from __future__ import annotations

from typing import Generic, TypeVar

from pydantic import BaseModel

T = TypeVar("T")


class ApiResponse(BaseModel, Generic[T]):
    # per frontend doc: 200 means success
    code: int = 200
    message: str = "ok"
    data: T | None = None
