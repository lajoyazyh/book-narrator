from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, Field


class AgentChatRequest(BaseModel):
    bookId: str = Field(min_length=1)
    chapter: str = Field(min_length=1)
    style: Literal["academic", "plain", "sarcastic"]
    question: str = Field(min_length=1)


class ToolCallRecord(BaseModel):
    toolName: str
    args: dict = Field(default_factory=dict)
    status: Literal["success", "failed"]
    input: str = ""
    output: str = ""
    elapsedMs: int | None = None


class AgentTraceStep(BaseModel):
    title: str
    detail: str | None = None


class AgentChatResponse(BaseModel):
    answer: str
    audioUrl: str | None = None
    trace: list[AgentTraceStep] = Field(default_factory=list)
    toolCalls: list[ToolCallRecord] = Field(default_factory=list)
    selfCorrection: list[str] = Field(default_factory=list)
