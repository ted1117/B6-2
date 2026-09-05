# **요청과 응답의 전체 흐름**

## **학습 목표**

- 브라우저 요청이 각 계층을 거쳐 응답으로 돌아오는 과정을 설명할 수 있다.
- 조회 요청과 변경 요청의 흐름 차이를 이해한다.
- 생성, 수정, 완료, 삭제의 PRG 흐름을 단계별로 설명할 수 있다.
- 요청 단위 Session의 시작과 종료 시점을 이해한다.
- 문제가 발생한 계층을 요청 흐름을 따라 추적할 수 있다.

## **1. 전체 흐름 한눈에 보기**

웹 요청은 Router에서 시작해 필요한 계층으로 내려가고, 처리 결과는 다시 위로
올라와 HTTP 응답이 된다.

```text
Browser
  │ HTTP Request
  ▼
FastAPI Router
  │ 입력 모델과 Service 호출
  ▼
Service
  │ 업무 규칙과 Repository 호출
  ▼
Repository
  │ SQLAlchemy Session 사용
  ▼
SQLite
  │ 조회 또는 변경 결과
  ▲
Repository
  ▲
Service
  ▲
Router
  │ HTML 또는 303/404 Response
  ▼
Browser
```

모든 요청이 항상 데이터베이스까지 내려가는 것은 아니다. 홈이나 새 To-do Form처럼
고정된 화면을 보여주는 요청은 Template 렌더링만 하고 응답할 수 있다.

## **2. 요청 전 FastAPI의 준비 과정**

개발 서버를 실행하면 다음 준비가 이루어진다.

1. FastAPI CLI가 `app.main:app`을 찾는다.
2. Uvicorn이 ASGI 서버를 시작한다.
3. 애플리케이션 lifespan의 시작 코드가 실행된다.
4. `Base.metadata.create_all()`이 필요한 SQLite 테이블을 만든다.
5. 서버가 지정한 Host와 Port에서 요청을 기다린다.

이후 각 요청마다 URL 라우팅과 의존성 해결이 별도로 진행된다.

## **3. 홈 화면 요청**

```text
GET /
```

홈 화면은 데이터베이스 조회가 필요하지 않다.

```text
브라우저
  → GET /
  → Router.home()
  → home.html 렌더링
  → 200 OK + HTML
  → 브라우저 표시
```

HTML을 받은 브라우저는 문서의 CSS 링크를 발견하고 `GET /static/css/style.css`를
추가로 요청한다. 하나의 웹 페이지가 보이기까지 여러 HTTP 요청이 사용될 수 있다.

## **4. 목록 조회 흐름**

```text
GET /todos
```

1. FastAPI가 GET `/todos`에 연결된 Router 함수를 선택한다.
2. `get_session`이 새 SQLAlchemy Session을 생성한다.
3. `get_todo_service`가 Session으로 Repository와 Service를 만든다.
4. Router가 `service.get_all_todos()`를 호출한다.
5. Service가 Repository의 `get_all()`을 호출한다.
6. Repository가 생성 시각 내림차순으로 Todo를 조회한다.
7. Service가 ORM 객체를 `TodoResponse` 목록으로 변환한다.
8. Router가 목록을 Jinja2 Context에 넣는다.
9. 서버가 `200 OK`와 완성된 HTML을 반환한다.
10. 요청이 끝나면서 Session이 닫힌다.

```text
GET /todos
  → Session 생성
  → Repository.get_all()
  → SELECT todos ORDER BY created_at DESC
  → list[Todo]
  → list[TodoResponse]
  → list.html
  → 200 OK
  → Session 종료
```

## **5. 상세 조회 흐름**

```text
GET /todos/{todo_id}
```

FastAPI는 Path의 값을 정수로 변환해 `todo_id`에 전달한다. Repository는 기본 키로
한 행을 찾고 Service는 응답 모델로 변환한다.

### **5.1 대상이 존재하는 경우**

```text
GET /todos/1
  → Todo(id=1) 조회
  → TodoResponse 변환
  → detail.html 렌더링
  → 200 OK
```

### **5.2 대상이 존재하지 않는 경우**

```text
GET /todos/999
  → Repository 결과 None
  → Service 결과 None
  → Router가 HTTPException 발생
  → 404 Not Found
```

404 판단은 데이터베이스에 행이 없다는 Repository 결과를 Router가 HTTP 의미로
변환한 것이다.

## **6. 생성 Form 조회**

```text
GET /todos/new
```

이 요청은 입력 화면만 보여주므로 데이터베이스를 조회하지 않는다.

```text
GET /todos/new
  → new.html 렌더링
  → 200 OK
```

사용자가 Form에 제목과 상세 내용을 입력하고 생성 버튼을 누르면 별도의 POST
요청이 시작된다.

## **7. 생성 요청과 PRG**

```text
POST /todos
```

1. 브라우저가 Form 데이터를 URL encoded Body로 전송한다.
2. FastAPI가 Body를 `TodoCreate`로 변환하고 검증한다.
3. 요청용 Session, Repository, Service가 생성된다.
4. Service가 입력값으로 새 `Todo` ORM 객체를 만든다.
5. Repository가 객체를 Session에 추가하고 commit한다.
6. refresh를 통해 생성된 id와 시간 값을 읽는다.
7. Service가 `TodoResponse`로 변환한다.
8. Router가 `303 See Other`와 `/todos/{id}` Location을 반환한다.
9. 브라우저가 Location 주소로 GET 요청을 보낸다.
10. 상세 화면이 `200 OK` HTML로 표시된다.

```text
POST /todos
  → INSERT + COMMIT
  → 303 Location: /todos/1
  → GET /todos/1
  → 200 OK + 상세 HTML
```

POST 요청과 Redirect 뒤의 GET 요청은 서로 다른 HTTP 요청이므로 Session도 각각
새로 생성되고 종료된다.

## **8. 수정 흐름**

수정은 Form 조회와 변경 요청 두 단계로 나뉜다.

### **8.1 수정 Form 조회**

```text
GET /todos/1/edit
  → 기존 Todo 조회
  → edit.html에 기존 값 표시
  → 200 OK
```

### **8.2 수정 제출**

```text
POST /todos/1/edit
  → TodoUpdate 검증
  → 기존 Todo 조회
  → 제목, 내용, 완료 상태 변경
  → 완료 시간 규칙 적용
  → UPDATE + COMMIT
  → 303 Location: /todos/1
  → GET /todos/1
```

checkbox가 해제되면 Form 요청에 `is_completed`가 없고 Pydantic 기본값 False가
사용된다. Service는 미완료 상태에 맞춰 `completed_at`을 None으로 바꾼다.

## **9. 완료 흐름**

```text
POST /todos/1/complete
```

1. Service가 대상 Todo를 조회한다.
2. 미완료라면 `is_completed=True`와 현재 완료 시간을 설정한다.
3. 이미 완료됐다면 기존 완료 시간을 유지한다.
4. Repository가 변경을 commit한다.
5. Router가 목록 주소로 303을 반환한다.

```text
POST /todos/1/complete
  → 완료 상태 확인
  → 필요한 경우 UPDATE + COMMIT
  → 303 Location: /todos
  → GET /todos
```

동일한 완료 요청을 반복해도 처음 기록된 `completed_at`을 덮어쓰지 않는 동작을
멱등성 관점에서 이해할 수 있다. HTTP Method가 POST이더라도 Service 규칙은 같은
요청의 반복 영향을 줄이도록 설계할 수 있다.

## **10. 삭제 흐름**

사용자가 상세 화면의 삭제 버튼을 누르면 먼저 HTML popover 확인창이 열린다.
이 시점에는 서버 요청이나 데이터 변경이 없다.

```text
삭제 버튼
  → 브라우저가 확인창 표시
  → 취소: 확인창만 닫음
  → 확인: POST /todos/1/delete
```

삭제 확인 후 서버 흐름은 다음과 같다.

```text
POST /todos/1/delete
  → 대상 Todo 조회
  → DELETE + COMMIT
  → 303 Location: /todos
  → GET /todos
```

삭제를 GET 링크가 아니라 POST Form으로 전송하므로 단순 페이지 조회와 데이터
변경을 구분한다.

## **11. 정적 CSS 요청 흐름**

Template의 `url_for('static', path='/css/style.css')`는 마운트 이름을 이용해
CSS URL을 생성한다.

```text
HTML 렌더링
  → /static/css/style.css 링크 포함
  → 브라우저가 GET /static/css/style.css 요청
  → StaticFiles가 파일 조회
  → 200 OK + text/css
```

CSS 경로는 `app/main.py`의 실제 위치를 기준으로 계산하므로 애플리케이션을 어느
작업 디렉터리에서 실행하는지에 덜 의존한다.

## **12. Session 생명주기**

데이터베이스를 사용하는 한 요청의 Session 흐름은 다음과 같다.

```text
요청 시작
  → get_session 실행
  → Session 생성
  → yield session
  → Repository가 Session 사용
  → 응답 생성
  → dependency 정리 재개
  → with 블록 종료
  → Session 닫힘
```

Redirect 뒤의 GET은 새 요청이므로 이전 Session을 다시 사용하지 않는다. 요청
사이에 ORM 객체나 Session을 전역 상태로 보관하지 않는 이유도 여기에 있다.

## **13. 문제 발생 위치 추적하기**

화면이 예상대로 동작하지 않을 때 요청 흐름을 앞에서부터 확인한다.

| 확인 항목 | 의심할 위치 |
| --- | --- |
| 요청 Method나 URL이 다름 | HTML Form, 링크, Router |
| 422 응답 | Form 필드명, Pydantic Schema |
| 404 응답 | Path Parameter, 조회 결과, Router 분기 |
| 저장되지 않음 | Service 상태 변경, Repository commit |
| Redirect 위치가 다름 | Router의 RedirectResponse |
| HTML에 값이 없음 | Context 이름, Jinja2 Template |
| CSS가 적용되지 않음 | static mount, URL, 파일 경로 |

브라우저 개발자 도구의 Network 탭에서는 Method, URL, Status Code, Redirect를
확인할 수 있다. 서버 로그와 테스트 결과를 함께 보면 어느 계층에서 흐름이
끊겼는지 더 빠르게 찾을 수 있다.

## **14. 테스트가 검증하는 흐름**

UI 통합 테스트는 FastAPI TestClient로 실제 HTTP 요청과 유사한 흐름을 만든다.

- GET 화면이 200과 필요한 링크를 반환하는지 확인한다.
- Form의 method, action, field 이름을 확인한다.
- POST 이후 303과 Location을 확인한다.
- 임시 SQLite에서 실제 저장 결과를 확인한다.
- Redirect 대상 GET 화면에 변경된 값이 보이는지 확인한다.
- 존재하지 않는 id가 404인지 확인한다.

응답 HTML만 확인하면 데이터가 실제 저장되지 않는 버그를 놓칠 수 있고,
데이터베이스만 확인하면 잘못된 Redirect나 Form 경로를 놓칠 수 있다. 요청부터
저장과 화면까지 함께 검증해야 전체 흐름을 확인할 수 있다.

## **프로젝트에서 확인하기**

- `app/main.py`: 서버 시작, lifespan, Router와 static 등록
- `app/routers/todos.py`: 모든 HTTP 진입점과 응답
- `app/services/todos.py`: 생성, 수정, 완료, 삭제 규칙
- `app/repositories/todos.py`: 실제 조회와 commit
- `app/templates/`: 브라우저가 받는 HTML
- `tests/test_todo_ui.py`: 요청부터 SQLite까지 통합 흐름

## **핵심 정리**

브라우저의 요청은 Router, Service, Repository를 거쳐 SQLite에 도달하고 결과는
반대 방향으로 돌아와 HTML이나 Redirect 응답이 된다. 조회 요청은 200 HTML로
끝나고, 변경 요청은 commit 후 303을 반환해 새로운 GET 요청으로 이어진다. 각
요청은 독립적인 Session을 사용하며, 전체 흐름을 이해하면 상태 코드나 화면만
보는 것보다 오류 위치를 정확하게 좁힐 수 있다.
