from pathlib import Path
from typing import Annotated

from fastapi import APIRouter, Depends, Form, HTTPException, Request, status
from fastapi.responses import HTMLResponse, RedirectResponse, Response
from fastapi.templating import Jinja2Templates

from app.core.database import SessionDep
from app.repositories.todos import TodoRepository
from app.schemas.todos import TodoCreate, TodoResponse, TodoUpdate
from app.services.todos import TodoService

router = APIRouter(tags=["Todos"])

TEMPLATES_DIR = Path(__file__).resolve().parents[1] / "templates"
templates = Jinja2Templates(directory=str(TEMPLATES_DIR))


def get_todo_service(session: SessionDep) -> TodoService:
    repository = TodoRepository(session)
    return TodoService(repository)


TodoServiceDep = Annotated[TodoService, Depends(get_todo_service)]
TodoCreateForm = Annotated[TodoCreate, Form()]
TodoUpdateForm = Annotated[TodoUpdate, Form()]


@router.get("/", response_class=HTMLResponse)
def home(request: Request) -> Response:
    return templates.TemplateResponse(
        request=request,
        name="home.html",
        context={"app_name": "홈"},
    )


@router.get("/todos", response_class=HTMLResponse)
def get_all_todos(request: Request, service: TodoServiceDep) -> Response:
    todos: list[TodoResponse] = service.get_all_todos()
    return templates.TemplateResponse(
        request=request,
        name="todos/list.html",
        context={"todos": todos},
    )


@router.get("/todos/new", response_class=HTMLResponse)
def create_todo_form(request: Request) -> Response:
    return templates.TemplateResponse(
        request=request,
        name="todos/new.html",
    )


@router.post(
    "/todos",
    status_code=status.HTTP_303_SEE_OTHER,
    response_class=RedirectResponse,
)
def create_todo(
    todo_create: TodoCreateForm,
    service: TodoServiceDep,
) -> RedirectResponse:
    todo: TodoResponse = service.create_todo(todo_create)
    return RedirectResponse(
        url=f"/todos/{todo.id}",
        status_code=status.HTTP_303_SEE_OTHER,
    )


@router.get("/todos/{todo_id}", response_class=HTMLResponse)
def get_todo(todo_id: int, request: Request, service: TodoServiceDep) -> Response:
    todo: TodoResponse | None = service.get_todo_by_id(todo_id)
    if todo is None:
        return templates.TemplateResponse(
            request=request,
            name="todos/not_found.html",
            status_code=status.HTTP_404_NOT_FOUND,
        )

    return templates.TemplateResponse(
        request=request,
        name="todos/detail.html",
        context={"todo": todo},
    )


@router.get("/todos/{todo_id}/edit", response_class=HTMLResponse)
def update_todo_form(
    todo_id: int,
    request: Request,
    service: TodoServiceDep,
) -> Response:
    todo: TodoResponse | None = service.get_todo_by_id(todo_id)
    if todo is None:
        return templates.TemplateResponse(
            request=request,
            name="todos/not_found.html",
            status_code=status.HTTP_404_NOT_FOUND,
        )

    return templates.TemplateResponse(
        request=request,
        name="todos/edit.html",
        context={"todo": todo},
    )


@router.post(
    "/todos/{todo_id}/edit",
    status_code=status.HTTP_303_SEE_OTHER,
    response_class=RedirectResponse,
)
def update_todo(
    todo_id: int,
    todo_update: TodoUpdateForm,
    service: TodoServiceDep,
) -> RedirectResponse:
    todo: TodoResponse | None = service.update_todo(todo_id, todo_update)
    if todo is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="To-do를 찾을 수 없습니다.",
        )

    return RedirectResponse(
        url=f"/todos/{todo.id}",
        status_code=status.HTTP_303_SEE_OTHER,
    )


@router.post(
    "/todos/{todo_id}/complete",
    status_code=status.HTTP_303_SEE_OTHER,
    response_class=RedirectResponse,
)
def complete_todo(todo_id: int, service: TodoServiceDep) -> RedirectResponse:
    completed: TodoResponse | None = service.complete_todo(todo_id)
    if completed is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="To-do를 찾을 수 없습니다.",
        )

    return RedirectResponse(
        url="/todos",
        status_code=status.HTTP_303_SEE_OTHER,
    )


@router.post(
    "/todos/{todo_id}/delete",
    status_code=status.HTTP_303_SEE_OTHER,
    response_class=RedirectResponse,
)
def delete_todo(todo_id: int, service: TodoServiceDep) -> RedirectResponse:
    deleted: bool = service.delete_todo(todo_id)
    if not deleted:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="To-do를 찾을 수 없습니다.",
        )

    return RedirectResponse(
        url="/todos",
        status_code=status.HTTP_303_SEE_OTHER,
    )
