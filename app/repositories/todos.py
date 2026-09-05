from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.todos import Todo


class TodoRepository:
    def __init__(self, session: Session) -> None:
        self.session = session

    def get_all(
        self, search_by: str = "title", search_query: str | None = None
    ) -> list[Todo]:
        stmt = select(Todo)
        if search_query:
            if search_by == "title":
                stmt = stmt.filter(Todo.title.like(f"%{search_query}%"))
            elif search_by == "description":
                stmt = stmt.filter(Todo.description.like(f"%{search_query}%"))
        stmt = stmt.order_by(Todo.created_at.desc())
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

    def delete(self, todo: Todo) -> None:
        self.session.delete(todo)
        self.session.commit()
