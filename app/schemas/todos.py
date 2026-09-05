from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field, field_validator


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


class TodoSearch(BaseModel):
    """Todo 검색 요청 스키마."""

    search_by: str = Field(
        default="title",
        description="검색 기준 필드 (title 또는 description)",
        examples=["title", "description"],
    )
    q: str | None = Field(
        default=None,
        description="검색어",
        examples=["장보기"],
    )

    @field_validator("search_by")
    @classmethod
    def validate_search_by(cls, value: str) -> str:
        if value not in {"title", "description"}:
            return "title"
        return value

    @field_validator("q")
    @classmethod
    def validate_q(cls, value: str | None) -> str | None:
        if value is None:
            return None
        return value.strip() or None


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
