# src/tools/todo.py

from typing import Optional, Literal, List, Any

from pydantic import BaseModel, Field, model_validator


class TodoItem(BaseModel):
    """待办事项的具体条目"""

    content: str = Field(
        default="",
        description="任务的具体内容"
    )

    status: Literal["pending", "in_progress", "completed"] = Field(
        default="pending",
        description="任务状态"
    )

    active_form: Optional[str] = Field(
        default=None,
        description="可选的现在进行时标签（例如 '正在搜索中...'）"
    )

    @model_validator(mode="before")
    @classmethod
    def normalize_input(cls, data: Any):
        """
        兼容大模型工具调用时可能传入 description 而不是 content 的情况。

        支持：
        {"content": "...", "status": "pending"}
        {"description": "...", "status": "pending"}
        """
        if isinstance(data, dict):
            if not data.get("content") and data.get("description"):
                data["content"] = data["description"]

            if not data.get("status"):
                data["status"] = "pending"

        return data


class TodoState(BaseModel):
    items: List[TodoItem] = Field(default_factory=list)
    rounds_since_update: int = Field(default=0)


class TodoManager:
    def __init__(self):
        self.state = TodoState()

    def update(self, items: list[TodoItem]) -> str:
        if len(items) > 12:
            raise ValueError("Keep the session todo short (max 12 items)")

        normalized = []
        in_progress_count = 0

        for index, raw_item in enumerate(items):
            # 如果工具层传进来的不是 TodoItem，而是 dict，这里也做一次兼容
            if isinstance(raw_item, dict):
                raw_item = TodoItem.model_validate(raw_item)

            content = str(raw_item.content).strip()
            status = str(raw_item.status).lower()
            active_form = (
                str(raw_item.active_form).strip()
                if raw_item.active_form is not None
                else None
            )

            if not content:
                raise ValueError(f"Item {index}: content required")

            if status not in {"pending", "in_progress", "completed"}:
                raise ValueError(f"Item {index}: invalid status '{status}'")

            if status == "in_progress":
                in_progress_count += 1

            normalized.append(
                TodoItem(
                    content=content,
                    status=status,
                    active_form=active_form,
                )
            )

        if in_progress_count > 1:
            raise ValueError("Only one todo item can be in_progress")

        self.state.items = normalized
        self.state.rounds_since_update = 0

        return self.render()

    def note_round_without_update(self) -> None:
        self.state.rounds_since_update += 1

    def reminder(self) -> Optional[str]:
        if not self.state.items:
            return None

        if self.state.rounds_since_update < 3:
            return None

        return "<reminder>Refresh your current todo before continuing.</reminder>"

    def render(self) -> str:
        """渲染当前待办事项列表"""
        if not self.state.items:
            return "No session todo yet."

        lines = ["\n"]

        for item in self.state.items:
            marker = {
                "pending": "[ ]",
                "in_progress": "[>]",
                "completed": "[✓]",
            }[item.status]

            line = f"{marker} {item.content}"

            if item.status == "in_progress" and item.active_form:
                line += f" ({item.active_form})"

            lines.append(line)

        completed = sum(
            1 for item in self.state.items
            if item.status == "completed"
        )

        lines.append(f"\n({completed}/{len(self.state.items)} completed)\n")

        return "\n".join(lines)