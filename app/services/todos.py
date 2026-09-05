from datetime import datetime

from app.models.todos import Todo
from app.repositories.todos import TodoRepository
from app.schemas.todos import TodoCreate, TodoResponse, TodoUpdate


class TodoService:
    def __init__(self, repository: TodoRepository) -> None:
        self.repository = repository

    def get_all_todos(
        self, search_by: str = "title", search_query: str | None = None
    ) -> list[TodoResponse]:
        return [
            TodoResponse.model_validate(todo)
            for todo in self.repository.get_all(
                search_by=search_by, search_query=search_query
            )
        ]

    def get_todo_by_id(self, todo_id: int) -> TodoResponse | None:
        todo = self.repository.get_by_id(todo_id)
        if todo is None:
            return None

        return TodoResponse.model_validate(todo)

    def create_todo(self, todo_create: TodoCreate) -> TodoResponse:
        todo = Todo(
            title=todo_create.title,
            description=todo_create.description,
        )
        created_todo = self.repository.create(todo)
        return TodoResponse.model_validate(created_todo)

    def update_todo(
        self,
        todo_id: int,
        todo_update: TodoUpdate,
    ) -> TodoResponse | None:
        todo = self.repository.get_by_id(todo_id)
        if todo is None:
            return None

        # 이미 완료된 Todo인지 확인
        was_completed: bool = todo.is_completed

        # Todo 최신화
        todo.title = todo_update.title
        todo.description = todo_update.description
        todo.is_completed = todo_update.is_completed

        # 미완료 Todo
        if not todo.is_completed:
            todo.completed_at = None
        # 이제 완료된 Todo
        elif not was_completed:
            todo.completed_at = datetime.now()

        updated_todo = self.repository.update(todo)
        return TodoResponse.model_validate(updated_todo)

    def complete_todo(self, todo_id: int) -> TodoResponse | None:
        todo = self.repository.get_by_id(todo_id)
        if todo is None:
            return None

        if todo.is_completed:
            return TodoResponse.model_validate(todo)

        todo.is_completed = True
        todo.completed_at = datetime.now()

        updated_todo = self.repository.update(todo)
        return TodoResponse.model_validate(updated_todo)

    def delete_todo(self, todo_id: int) -> bool:
        todo = self.repository.get_by_id(todo_id)
        if todo is None:
            return False

        self.repository.delete(todo)
        return True
