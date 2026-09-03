from datetime import datetime

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.todos import Todo


class TodoRepository:
    def __init__(self, session: Session) -> None:
        self.session = session

    def get_all(self) -> list[Todo]:
        stmt = select(Todo).order_by(Todo.created_at.desc())
        return list(self.session.scalars(stmt).all())

    def get_by_id(self, todo_id: int) -> Todo | None:
        return self.session.get(Todo, todo_id)

    def create(self, todo: Todo) -> Todo:
        self.session.add(todo)
        self.session.commit()
        self.session.refresh(todo)
        return todo

    def update(self, todo: Todo) -> Todo:
        self.session.add(todo)
        self.session.commit()
        self.session.refresh(todo)
        return todo

    def complete(self, todo: Todo) -> bool:
        todo.is_completed = True
        todo.completed_at = datetime.now()
        self.session.add(todo)
        self.session.commit()
        self.session.refresh(todo)
        return todo.is_completed

    def delete(self, todo: Todo) -> None:
        self.session.delete(todo)
        self.session.commit()
