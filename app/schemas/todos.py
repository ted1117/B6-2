from pydantic import BaseModel, Field


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
