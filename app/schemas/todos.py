from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class TodoBase(BaseModel):
    title: str = Field(
        min_length=1,
        max_length=100,
        description="Todo 제목",
        examples=["장보기"],
    )
    description: str | None = Field(
        default=None,
        description="Todo 상세 내용",
        examples=["우유와 달걀 구매"],
    )


class TodoCreate(TodoBase):
    """Todo 생성 요청 스키마."""


class TodoUpdate(TodoBase):
    """Todo 수정 요청 스키마."""

    is_completed: bool = Field(
        default=False,
        description="Todo 완료 여부",
    )


class TodoResponse(TodoBase):
    """Todo 응답 스키마."""

    id: int = Field(description="Todo ID")
    is_completed: bool = Field(description="Todo 완료 여부")
    completed_at: datetime | None = Field(description="Todo 완료 시간")
    created_at: datetime = Field(description="Todo 생성 시간")
    updated_at: datetime = Field(description="Todo 수정 시간")

    model_config = ConfigDict(from_attributes=True)
