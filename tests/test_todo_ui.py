from collections.abc import Iterator
from dataclasses import dataclass, field
from html.parser import HTMLParser
from pathlib import Path

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.engine import Engine
from sqlalchemy.orm import Session

from app.core.database import Base, get_session
from app.main import app
from app.models.todos import Todo


@dataclass
class ParsedForm:
    action: str
    method: str
    fields: set[str] = field(default_factory=set)
    dialog_id: str | None = None


@dataclass
class ParsedButton:
    attributes: dict[str, str | None]
    form_action: str | None
    dialog_id: str | None
    text: str = ""


class PageParser(HTMLParser):
    def __init__(self) -> None:
        super().__init__()
        self.forms: list[ParsedForm] = []
        self.buttons: list[ParsedButton] = []
        self.links: set[str] = set()
        self.elements: list[tuple[str, dict[str, str | None]]] = []
        self.current_form: ParsedForm | None = None
        self.current_button: ParsedButton | None = None
        self.current_dialog_id: str | None = None

    def handle_starttag(
        self,
        tag: str,
        attrs: list[tuple[str, str | None]],
    ) -> None:
        attributes = dict(attrs)
        self.elements.append((tag, attributes))

        if tag == "dialog":
            self.current_dialog_id = attributes.get("id")

        if tag == "button":
            self.current_button = ParsedButton(
                attributes=attributes,
                form_action=self.current_form.action if self.current_form else None,
                dialog_id=self.current_dialog_id,
            )

        if tag == "a" and attributes.get("href"):
            self.links.add(attributes["href"])

        if tag == "form":
            self.current_form = ParsedForm(
                action=attributes.get("action") or "",
                method=(attributes.get("method") or "get").lower(),
                dialog_id=self.current_dialog_id,
            )
        elif self.current_form is not None and tag in {"input", "select", "textarea"}:
            name = attributes.get("name")
            if name:
                self.current_form.fields.add(name)

    def handle_endtag(self, tag: str) -> None:
        if tag == "form" and self.current_form is not None:
            self.forms.append(self.current_form)
            self.current_form = None
        elif tag == "button" and self.current_button is not None:
            self.current_button.text = self.current_button.text.strip()
            self.buttons.append(self.current_button)
            self.current_button = None
        elif tag == "dialog":
            self.current_dialog_id = None

    def handle_data(self, data: str) -> None:
        if self.current_button is not None:
            self.current_button.text += data


@pytest.fixture
def ui(tmp_path: Path) -> Iterator[tuple[TestClient, Engine]]:
    test_engine = create_engine(
        f"sqlite:///{tmp_path / 'todo-ui.db'}",
        connect_args={"check_same_thread": False},
    )
    Base.metadata.create_all(bind=test_engine)

    def override_get_session() -> Iterator[Session]:
        with Session(test_engine) as session:
            yield session

    previous_overrides = app.dependency_overrides.copy()
    app.dependency_overrides[get_session] = override_get_session
    client = TestClient(app)

    try:
        yield client, test_engine
    finally:
        client.close()
        app.dependency_overrides.clear()
        app.dependency_overrides.update(previous_overrides)
        test_engine.dispose()


def parse_page(html: str) -> PageParser:
    parser = PageParser()
    parser.feed(html)
    return parser


def assert_form(
    html: str,
    *,
    action: str,
    fields: set[str] | None = None,
) -> None:
    forms = [form for form in parse_page(html).forms if form.action == action]

    assert forms, f"POST form을 찾을 수 없습니다: {action}"
    assert forms[0].method == "post"
    assert (fields or set()) <= forms[0].fields


def create_todo(client: TestClient, *, title: str, description: str) -> int:
    response = client.post(
        "/todos",
        data={"title": title, "description": description},
        follow_redirects=False,
    )

    assert response.status_code == 303
    location = response.headers["location"]
    assert location.startswith("/todos/")
    return int(location.rsplit("/", maxsplit=1)[-1])


def get_stored_todo(engine: Engine, todo_id: int) -> Todo | None:
    with Session(engine) as session:
        todo = session.get(Todo, todo_id)
        if todo is not None:
            session.expunge(todo)
        return todo


def test_home_and_empty_todo_list_render_navigation(
    ui: tuple[TestClient, Engine],
) -> None:
    client, _ = ui

    home_response = client.get("/")

    assert home_response.status_code == 200
    assert "To-do" in home_response.text
    assert {"/todos", "/todos/new"} <= parse_page(home_response.text).links

    list_response = client.get("/todos")

    assert list_response.status_code == 200
    assert "/todos/new" in parse_page(list_response.text).links


def test_ui_pages_use_korean_labels_without_javascript(
    ui: tuple[TestClient, Engine],
) -> None:
    client, _ = ui
    todo_id = create_todo(client, title="화면 확인", description="화면에 표시할 내용")

    for path in (
        "/",
        "/todos",
        "/todos/new",
        f"/todos/{todo_id}",
        f"/todos/{todo_id}/edit",
    ):
        response = client.get(path)

        assert response.status_code == 200
        assert "To-do" in response.text
        assert "할 일" not in response.text
        for tag, attributes in parse_page(response.text).elements:
            assert tag != "script"
            assert not any(name.startswith("on") for name in attributes)
            assert not any(
                (value or "").strip().lower().startswith("javascript:")
                for value in attributes.values()
            )


def test_stylesheet_link_serves_css_from_another_working_directory(
    ui: tuple[TestClient, Engine],
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    client, _ = ui
    monkeypatch.chdir(tmp_path)

    response = client.get("/")
    assert response.status_code == 200
    elements = parse_page(response.text).elements
    stylesheets = [
        attributes["href"]
        for tag, attributes in elements
        if tag == "link" and attributes.get("rel") == "stylesheet"
    ]
    assert len(stylesheets) == 1
    assert not any(tag == "style" for tag, _ in elements)

    css_response = client.get(stylesheets[0])
    assert css_response.status_code == 200
    assert css_response.headers["content-type"].startswith("text/css")
    assert css_response.text.strip()


def test_create_form_and_create_prg_render_todo_detail(
    ui: tuple[TestClient, Engine],
) -> None:
    client, engine = ui

    form_response = client.get("/todos/new")

    assert form_response.status_code == 200
    assert_form(
        form_response.text,
        action="/todos",
        fields={"title", "description"},
    )

    todo_id = create_todo(
        client,
        title="통합 테스트 작성",
        description="HTML form과 PRG를 검증한다.",
    )

    stored = get_stored_todo(engine, todo_id)
    assert stored is not None
    assert stored.title == "통합 테스트 작성"
    assert stored.description == "HTML form과 PRG를 검증한다."

    detail_response = client.get(f"/todos/{todo_id}")

    assert detail_response.status_code == 200
    assert "통합 테스트 작성" in detail_response.text
    assert "HTML form과 PRG를 검증한다." in detail_response.text
    detail_page = parse_page(detail_response.text)
    assert {f"/todos/{todo_id}/edit", "/todos"} <= detail_page.links
    assert_form(detail_response.text, action=f"/todos/{todo_id}/delete")

    list_response = client.get("/todos")

    assert "통합 테스트 작성" in list_response.text
    assert f"/todos/{todo_id}" in parse_page(list_response.text).links
    assert_form(list_response.text, action=f"/todos/{todo_id}/complete")


def test_edit_form_and_update_prg_apply_changes(
    ui: tuple[TestClient, Engine],
) -> None:
    client, engine = ui
    todo_id = create_todo(
        client,
        title="수정 전 제목",
        description="수정 전 내용",
    )

    form_response = client.get(f"/todos/{todo_id}/edit")

    assert form_response.status_code == 200
    assert "수정 전 제목" in form_response.text
    assert "수정 전 내용" in form_response.text
    assert_form(
        form_response.text,
        action=f"/todos/{todo_id}/edit",
        fields={"title", "description", "is_completed"},
    )

    update_response = client.post(
        f"/todos/{todo_id}/edit",
        data={
            "title": "수정 후 제목",
            "description": "수정 후 내용",
            "is_completed": "on",
        },
        follow_redirects=False,
    )

    assert update_response.status_code == 303
    assert update_response.headers["location"] == f"/todos/{todo_id}"

    stored = get_stored_todo(engine, todo_id)
    assert stored is not None
    assert stored.title == "수정 후 제목"
    assert stored.description == "수정 후 내용"
    assert stored.is_completed is True
    assert stored.completed_at is not None

    detail_response = client.get(f"/todos/{todo_id}")

    assert detail_response.status_code == 200
    assert "수정 후 제목" in detail_response.text
    assert "수정 후 내용" in detail_response.text


def test_complete_prg_updates_todo_and_list(
    ui: tuple[TestClient, Engine],
) -> None:
    client, engine = ui
    todo_id = create_todo(
        client,
        title="완료할 To-do",
        description="완료 상태 변경 대상",
    )

    for path in ("/todos", f"/todos/{todo_id}"):
        response = client.get(path)

        assert response.status_code == 200
        if path == f"/todos/{todo_id}":
            assert "완료 일시" not in response.text
        assert_form(response.text, action=f"/todos/{todo_id}/complete")
        page = parse_page(response.text)
        complete_buttons = [
            button
            for button in page.buttons
            if button.form_action == f"/todos/{todo_id}/complete"
        ]
        assert len(complete_buttons) == 1
        assert complete_buttons[0].text == "완료"
        assert complete_buttons[0].attributes.get("type") == "submit"
        assert "disabled" not in complete_buttons[0].attributes
        assert not any(
            tag == "input" and attributes.get("type") == "checkbox"
            for tag, attributes in page.elements
        )

    complete_response = client.post(
        f"/todos/{todo_id}/complete",
        follow_redirects=False,
    )

    assert complete_response.status_code == 303
    assert complete_response.headers["location"] == "/todos"

    stored = get_stored_todo(engine, todo_id)
    assert stored is not None
    assert stored.is_completed is True
    assert stored.completed_at is not None

    for path in ("/todos", f"/todos/{todo_id}"):
        response = client.get(path)

        assert response.status_code == 200
        assert "완료할 To-do" in response.text
        if path == f"/todos/{todo_id}":
            assert "완료 일시" in response.text
            assert stored.completed_at.isoformat() in response.text
            assert stored.completed_at.strftime("%Y-%m-%d %H:%M") in response.text
        page = parse_page(response.text)
        assert not any(
            form.action == f"/todos/{todo_id}/complete" for form in page.forms
        )
        complete_buttons = [button for button in page.buttons if button.text == "완료"]
        assert len(complete_buttons) == 1
        assert "disabled" in complete_buttons[0].attributes


def test_delete_prg_removes_todo_from_storage_and_list(
    ui: tuple[TestClient, Engine],
) -> None:
    client, engine = ui
    todo_id = create_todo(
        client,
        title="삭제할 To-do",
        description="삭제 대상",
    )

    detail_response = client.get(f"/todos/{todo_id}")

    assert detail_response.status_code == 200
    page = parse_page(detail_response.text)
    dialogs = [
        attributes
        for tag, attributes in page.elements
        if tag == "dialog" and attributes.get("id") == "delete-confirmation"
    ]
    assert len(dialogs) == 1
    assert "popover" in dialogs[0]
    confirmation_buttons = [
        button
        for button in page.buttons
        if button.attributes.get("popovertarget") == "delete-confirmation"
    ]
    open_buttons = [
        button
        for button in confirmation_buttons
        if button.attributes.get("popovertargetaction") == "show"
    ]
    assert len(open_buttons) == 1
    assert open_buttons[0].attributes.get("type") == "button"
    assert open_buttons[0].form_action is None
    cancel_buttons = [
        button
        for button in confirmation_buttons
        if button.attributes.get("popovertargetaction") == "hide"
    ]
    assert len(cancel_buttons) == 1
    assert cancel_buttons[0].attributes.get("type") == "button"
    assert cancel_buttons[0].dialog_id == "delete-confirmation"
    delete_forms = [
        form for form in page.forms if form.action == f"/todos/{todo_id}/delete"
    ]
    assert len(delete_forms) == 1
    assert delete_forms[0].method == "post"
    assert delete_forms[0].dialog_id == "delete-confirmation"
    delete_buttons = [
        button
        for button in page.buttons
        if button.form_action == f"/todos/{todo_id}/delete"
        and button.attributes.get("type") == "submit"
    ]
    assert len(delete_buttons) == 1
    assert delete_buttons[0].dialog_id == "delete-confirmation"
    assert get_stored_todo(engine, todo_id) is not None

    delete_response = client.post(
        f"/todos/{todo_id}/delete",
        follow_redirects=False,
    )

    assert delete_response.status_code == 303
    assert delete_response.headers["location"] == "/todos"
    assert get_stored_todo(engine, todo_id) is None

    list_response = client.get("/todos")

    assert list_response.status_code == 200
    assert "삭제할 To-do" not in list_response.text
    assert client.get(f"/todos/{todo_id}").status_code == 404


@pytest.mark.parametrize("path", ["/todos/999", "/todos/999/edit"])
def test_missing_todo_pages_return_not_found(
    ui: tuple[TestClient, Engine],
    path: str,
) -> None:
    client, _ = ui

    response = client.get(path)

    assert response.status_code == 404
