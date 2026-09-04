from collections.abc import Iterator

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import Session

from app.core.database import Base
from app.repositories.todos import TodoRepository
from app.schemas.todos import TodoCreate, TodoResponse, TodoUpdate
from app.services.todos import TodoService


@pytest.fixture
def service() -> Iterator[TodoService]:
    engine = create_engine("sqlite://")
    Base.metadata.create_all(bind=engine)

    with Session(engine) as session:
        yield TodoService(TodoRepository(session))

    engine.dispose()


def test_service_converts_created_and_queried_todos_to_response_schema(
    service: TodoService,
) -> None:
    created = service.create_todo(
        TodoCreate(title="장보기", description="우유와 달걀 구매")
    )

    assert isinstance(created, TodoResponse)

    found = service.get_todo_by_id(created.id)
    todos = service.get_all_todos()

    assert isinstance(found, TodoResponse)
    assert all(isinstance(todo, TodoResponse) for todo in todos)
    assert [todo.id for todo in todos] == [created.id]


def test_service_converts_updated_and_completed_todos_to_response_schema(
    service: TodoService,
) -> None:
    created = service.create_todo(TodoCreate(title="공부", description=None))

    updated = service.update_todo(
        created.id,
        TodoUpdate(
            title="FastAPI 공부",
            description="Service 계층 정리",
            is_completed=True,
        ),
    )

    assert isinstance(updated, TodoResponse)
    assert updated.is_completed is True
    assert updated.completed_at is not None

    completed = service.complete_todo(created.id)

    assert isinstance(completed, TodoResponse)
    assert completed.completed_at == updated.completed_at
