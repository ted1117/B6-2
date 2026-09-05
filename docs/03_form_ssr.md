# **HTML Form과 서버 사이드 렌더링**

## **학습 목표**

- HTML Form이 브라우저 입력을 HTTP 요청으로 바꾸는 과정을 설명할 수 있다.
- FastAPI에서 `Form()`으로 입력값을 받는 방법을 이해한다.
- Jinja2를 이용한 서버 사이드 렌더링의 흐름을 설명할 수 있다.
- Template 상속과 Context의 역할을 이해한다.
- PRG 패턴이 Form 중복 제출을 방지하는 원리를 설명할 수 있다.

## **1. HTML Form의 역할**

HTML Form은 사용자가 입력한 값을 이름과 값의 쌍으로 만들어 서버에 전달한다.
Form의 `method`는 HTTP Method를, `action`은 요청을 보낼 URL을 결정한다.

```html
<form method="post" action="/todos">
  <label for="title">제목</label>
  <input id="title" name="title" type="text" required>

  <label for="description">상세 내용</label>
  <textarea id="description" name="description"></textarea>

  <button type="submit">생성</button>
</form>
```

사용자가 생성 버튼을 누르면 브라우저는 `name`이 있는 입력 요소만 요청 데이터에
포함한다.

```text
POST /todos
title=입력한 제목
description=입력한 내용
```

`id`는 label과 입력 요소를 연결하는 데 사용하고, `name`은 서버로 전송되는 필드
이름으로 사용한다. 두 속성의 목적은 서로 다르다.

## **2. 주요 Form 속성**

| 속성 | 역할 |
| --- | --- |
| `method` | 요청에 사용할 HTTP Method |
| `action` | 요청을 보낼 URL |
| `name` | 요청 데이터의 필드 이름 |
| `value` | 서버에 전달할 값 |
| `required` | 빈 값 제출을 막는 브라우저 검증 |
| `maxlength` | 입력할 수 있는 최대 문자 수 |
| `checked` | checkbox의 현재 선택 상태 |

브라우저 검증은 빠른 피드백을 제공하지만 서버 검증을 대신하지 않는다. 사용자는
브라우저가 아닌 다른 도구로 직접 요청할 수 있으므로 서버에서도 같은 입력 조건을
검증해야 한다.

## **3. FastAPI에서 Form 데이터 받기**

FastAPI는 `Form()`을 사용해
`application/x-www-form-urlencoded` 또는 `multipart/form-data` 형식의 요청을
읽는다. 이 프로젝트는 Pydantic 모델과 Form을 함께 선언한다.

```python
TodoCreateForm = Annotated[TodoCreate, Form()]

@router.post("/todos")
def create_todo(
    todo_create: TodoCreateForm,
    service: TodoServiceDep,
) -> RedirectResponse:
    ...
```

Form의 `title`과 `description`은 `TodoCreate`의 같은 이름 필드로 변환된다.
Pydantic은 제목의 최소 길이와 최대 길이 같은 조건을 검사한다.

### **3.1 checkbox의 전송 규칙**

HTML checkbox는 선택됐을 때만 이름과 값을 전송한다.

```html
<input name="is_completed" type="checkbox" value="true">
```

- 선택됨: `is_completed=true` 전송
- 선택 안 됨: `is_completed` 필드 자체를 전송하지 않음

따라서 수정 모델에서 `is_completed`의 기본값을 `False`로 설정하면 누락된 값을
체크 해제로 해석할 수 있다.

## **4. 서버 사이드 렌더링**

서버 사이드 렌더링(SSR)은 서버가 데이터를 HTML에 넣어 완성된 문서를 반환하는
방식이다. 브라우저는 별도의 JavaScript API 요청 없이 받은 HTML을 바로 표시할 수
있다.

```text
GET /todos
  → 데이터베이스 목록 조회
  → Jinja2 Template 렌더링
  → 완성된 HTML 반환
  → 브라우저 화면 표시
```

FastAPI에서는 `Jinja2Templates`로 템플릿 디렉터리를 지정한다.

```python
TEMPLATES_DIR = Path(__file__).resolve().parents[1] / "templates"
templates = Jinja2Templates(directory=str(TEMPLATES_DIR))
```

렌더링할 때는 Template 이름과 Context를 전달한다.

```python
return templates.TemplateResponse(
    request=request,
    name="todos/list.html",
    context={"todos": todos},
)
```

Context의 `todos`는 템플릿 안에서 같은 이름으로 사용할 수 있다.

```jinja2
{% for todo in todos %}
  <a href="/todos/{{ todo.id }}">{{ todo.title }}</a>
{% endfor %}
```

## **5. Jinja2 기본 문법**

Jinja2는 값 출력과 제어 구문을 서로 다른 기호로 구분한다.

| 문법 | 역할 | 예시 |
| --- | --- | --- |
| `{{ ... }}` | 값 출력 | `{{ todo.title }}` |
| `{% ... %}` | 조건, 반복, 상속 | `{% if todos %}` |
| `{# ... #}` | 템플릿 주석 | `{# 설명 #}` |

목록이 비어 있는지에 따라 다른 HTML을 만들 수 있다.

```jinja2
{% if todos %}
  {% for todo in todos %}
    ...
  {% endfor %}
{% else %}
  <p>등록된 작업이 없습니다.</p>
{% endif %}
```

Jinja2의 HTML autoescape는 일반적인 템플릿 변수에 포함된 특수 문자를 이스케이프해
사용자 입력이 곧바로 HTML 요소로 실행되는 위험을 줄인다. 특별한 이유 없이
사용자 입력에 `safe` 처리를 적용해서는 안 된다.

## **6. Template 상속**

여러 페이지에서 반복되는 문서 구조는 `base.html`에 둔다.

```jinja2
<!doctype html>
<html lang="ko">
  <head>
    <title>{% block title %}홈{% endblock %}</title>
  </head>
  <body>
    <main>
      {% block content %}{% endblock %}
    </main>
  </body>
</html>
```

개별 화면은 공통 Template을 상속하고 필요한 Block만 채운다.

```jinja2
{% extends "base.html" %}

{% block title %}작업 목록{% endblock %}

{% block content %}
  <h1>작업 목록</h1>
{% endblock %}
```

공통 내비게이션, CSS 링크, 접근성 요소를 한곳에서 관리할 수 있어 화면마다
구조가 달라지는 문제를 줄인다.

## **7. 생성과 수정 Form**

생성 Form은 빈 입력 요소를 보여주고 `POST /todos`로 전송한다. 수정 Form은 기존
데이터를 `value`와 textarea 내용으로 표시하고 `POST /todos/{todo_id}/edit`로
전송한다.

```jinja2
<input name="title" value="{{ todo.title }}">
<textarea name="description">{{ todo.description or "" }}</textarea>
```

서버에서 전달한 기존 값을 사용하므로 사용자는 현재 내용을 확인하면서 수정할 수
있다. `None`인 상세 내용은 빈 문자열로 표시해 `None`이라는 글자가 Form에
나타나지 않게 한다.

## **8. 데이터 변경과 PRG**

Form 제출로 데이터를 변경한 뒤 HTML을 바로 반환하면 사용자가 새로고침할 때
브라우저가 POST 재전송을 묻게 된다. 같은 생성 요청이 반복되면 중복 데이터가
생길 수도 있다.

PRG(Post-Redirect-Get)는 이 문제를 다음 흐름으로 줄인다.

```text
POST /todos
  → To-do 생성
  → 303 See Other
  → GET /todos/{todo_id}
  → 상세 HTML 표시
```

브라우저 주소와 마지막 요청이 GET으로 바뀌므로 이후 새로고침은 상세 조회만
반복한다. 이 프로젝트의 생성, 수정, 완료, 삭제 요청은 모두 POST 후 303을
반환한다.

## **9. JavaScript 없는 상태 변경 UI**

완료와 삭제도 HTML Form으로 구현할 수 있다.

```jinja2
<form method="post" action="/todos/{{ todo.id }}/complete">
  <button type="submit">완료</button>
</form>
```

삭제 확인 UI는 브라우저의 `popover` 기능과 실제 삭제 POST Form을 조합한다.
확인창을 여는 버튼은 `type="button"`이고, 사용자가 확인창 안의 submit 버튼을
눌러야 삭제 요청이 전송된다.

브라우저 기본 기능을 사용할 때는 지원 범위를 확인해야 한다. 지원되지 않는
브라우저까지 동일한 확인 경험을 제공해야 한다면 별도의 구현 전략이 필요하다.

## **프로젝트에서 확인하기**

- `app/templates/base.html`: 공통 구조와 Template Block
- `app/templates/todos/`: 목록, 상세, 생성, 수정 화면
- `app/routers/todos.py`: Form 입력과 TemplateResponse, RedirectResponse
- `tests/test_todo_ui.py`: Form 구조, 렌더링, PRG 통합 검증

## **핵심 정리**

HTML Form은 브라우저 입력을 HTTP 요청으로 만들고 FastAPI의 `Form()`은 그 값을
Pydantic 모델로 변환하고 검증한다. Jinja2 SSR은 서버 데이터를 완성된 HTML로
만들며, Template 상속은 공통 화면 구조를 재사용하게 한다. 상태 변경 후 303으로
GET 화면에 이동하는 PRG 패턴을 적용하면 Form 재전송과 중복 처리를 줄일 수 있다.
