# **FastAPI의 기본 구조**

## **학습 목표**

- FastAPI 애플리케이션이 요청을 처리하는 과정을 설명할 수 있다.
- Router와 Path Operation의 역할을 이해한다.
- Path Parameter와 타입 힌트가 어떻게 사용되는지 설명할 수 있다.
- `Depends`와 `Annotated`를 이용한 의존성 주입을 이해한다.
- Response Class와 애플리케이션 lifespan의 역할을 설명할 수 있다.

## **1. FastAPI란 무엇인가**

FastAPI는 Python 타입 힌트를 활용해 웹 API와 웹 애플리케이션을 만드는
프레임워크이다. 요청 데이터 변환과 검증, 라우팅, 의존성 주입, 응답 생성을
하나의 일관된 방식으로 제공한다.

FastAPI 애플리케이션 자체는 요청을 받아 처리하지만 실제 네트워크 연결은 ASGI
서버가 담당한다. `fastapi dev` 명령을 실행하면 개발 환경에서 Uvicorn이 ASGI
서버로 실행된다.

```text
브라우저
  → Uvicorn
  → FastAPI
  → Path Operation 함수
  → Response
```

## **2. 애플리케이션 객체**

FastAPI 프로젝트의 시작점은 `FastAPI` 인스턴스이다.

```python
app = FastAPI(lifespan=lifespan)
```

이 객체에 Router와 정적 파일 경로를 등록하면 하나의 웹 애플리케이션이 된다.

```python
app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")
app.include_router(todos_router)
```

`mount`는 특정 URL 아래에 별도의 ASGI 애플리케이션을 연결한다. 이 프로젝트에서는
CSS 파일을 제공하는 `StaticFiles`를 `/static`에 연결한다. `include_router`는
여러 Path Operation을 가진 Router를 메인 애플리케이션에 포함한다.

## **3. Router와 Path Operation**

Router는 관련된 URL을 한곳에 모으는 역할을 한다.

```python
router = APIRouter(tags=["Todos"])
```

Decorator의 Method와 Path에 함수를 연결하면 Path Operation이 된다.

```python
@router.get("/todos", response_class=HTMLResponse)
def get_all_todos(request: Request, service: TodoServiceDep) -> Response:
    ...
```

이 함수는 GET `/todos` 요청이 들어왔을 때 실행된다. Router는 HTTP 입력을 받고
Service를 호출한 뒤 HTML이나 Redirect를 반환한다. 데이터베이스 쿼리나 완료
시간 계산 같은 로직은 Router에 직접 작성하지 않는다.

## **4. Path Parameter와 타입 변환**

중괄호로 표시한 URL 부분은 Path Parameter이다.

```python
@router.get("/todos/{todo_id}")
def get_todo(todo_id: int, ...):
    ...
```

FastAPI는 URL의 문자열 값을 함수의 타입 힌트에 맞게 변환한다.

- `/todos/1`은 `todo_id=1`인 정수로 전달된다.
- `/todos/abc`는 정수로 변환할 수 없어 함수가 실행되기 전에 검증 오류가 난다.

타입 힌트는 개발자에게 함수 계약을 보여주는 동시에 FastAPI가 입력을 변환하고
검증하는 기준으로도 사용된다.

## **5. 의존성 주입**

의존성 주입은 함수가 필요한 객체를 내부에서 직접 만들지 않고 외부에서 받는
방식이다. FastAPI의 `Depends`는 요청을 처리하기 전에 의존성 함수를 실행하고 그
결과를 Path Operation 함수에 전달한다.

```python
def get_todo_service(session: SessionDep) -> TodoService:
    repository = TodoRepository(session)
    return TodoService(repository)
```

여기서도 의존성이 연속해서 조립된다.

```text
get_session
  → Session
  → TodoRepository
  → TodoService
  → Router 함수
```

반복되는 의존성 선언은 `Annotated` 타입 별칭으로 만들 수 있다.

```python
TodoServiceDep = Annotated[TodoService, Depends(get_todo_service)]
```

Router의 `service: TodoServiceDep`에는 타입 정보와 의존성 정보가 함께 들어 있다.
함수 본문은 객체 생성 방법을 몰라도 `TodoService`를 사용할 수 있다.

### **5.1 의존성 주입이 테스트에 주는 이점**

테스트에서는 실제 `get_session` 대신 임시 SQLite Session을 반환하는 함수로
교체할 수 있다.

```python
app.dependency_overrides[get_session] = override_get_session
```

애플리케이션 코드를 수정하지 않고 저장소만 격리할 수 있으므로 실제 `todo.db`에
테스트 데이터가 섞이지 않는다.

## **6. 요청 객체와 응답 클래스**

`Request`는 Method, URL, Header 등 현재 HTTP 요청의 정보를 제공한다. Jinja2
TemplateResponse에서 `url_for` 같은 요청 기반 기능을 사용하기 위해 템플릿
렌더링에도 전달한다.

`response_class`는 해당 Path Operation이 주로 반환할 응답의 종류를 나타낸다.

| 응답 클래스 | 사용 목적 |
| --- | --- |
| `HTMLResponse` | 렌더링한 HTML 반환 |
| `RedirectResponse` | 다른 URL로 이동 지시 |
| `Response` | 여러 응답 타입을 포괄하는 기본 타입 |

Redirect는 상태 코드와 이동할 URL을 함께 지정한다.

```python
return RedirectResponse(
    url=f"/todos/{todo.id}",
    status_code=status.HTTP_303_SEE_OTHER,
)
```

## **7. 예외와 HTTP 응답**

Path Operation에서 `HTTPException`을 발생시키면 FastAPI가 이를 HTTP 오류 응답으로
변환한다.

```python
if todo is None:
    raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail="To-do를 찾을 수 없습니다.",
    )
```

함수의 일반적인 반환 흐름과 오류 흐름을 분리할 수 있고, 상태 코드를 상수로
작성해 의미도 명확하게 표현할 수 있다.

## **8. 애플리케이션 lifespan**

lifespan은 애플리케이션 시작과 종료 시점에 실행할 작업을 정의한다.

```python
@asynccontextmanager
async def lifespan(app: FastAPI):
    Base.metadata.create_all(bind=engine)
    try:
        yield
    finally:
        engine.dispose()
```

`yield` 앞은 시작 단계, 뒤는 종료 단계이다. 현재 프로젝트는 시작할 때 필요한
테이블을 만들고 종료할 때 Engine의 연결 자원을 정리한다.

개발 편의를 위한 `create_all`은 존재하지 않는 테이블을 만드는 기능이다. 이미
운영 중인 테이블 구조를 단계적으로 변경하는 마이그레이션 도구와는 목적이 다르다.

## **9. 동기 함수와 비동기 함수**

FastAPI는 `def`와 `async def` Path Operation을 모두 지원한다. 이 프로젝트는
동기 SQLAlchemy Session을 사용하므로 Router와 Service도 일반 `def` 함수로
작성한다. 단순히 FastAPI를 사용한다는 이유만으로 모든 함수를 `async def`로
바꿀 필요는 없다. 사용하는 데이터베이스 드라이버와 호출 방식에 맞춰 일관되게
선택해야 한다.

## **프로젝트에서 확인하기**

- `app/main.py`: FastAPI 인스턴스, lifespan, 정적 파일, Router 등록
- `app/routers/todos.py`: Path Operation과 의존성 조립
- `app/core/database.py`: 요청 단위 Session 의존성
- `tests/test_todo_ui.py`: 의존성 override를 이용한 통합 테스트

## **핵심 정리**

FastAPI는 Method와 Path를 Python 함수에 연결하고 타입 힌트로 입력을 변환한다.
의존성 주입은 Session, Repository, Service를 요청마다 조립하며, Router가 객체
생성과 데이터베이스 세부 구현에서 벗어나 HTTP 처리에 집중하게 한다. 응답 클래스,
HTTPException, lifespan을 함께 사용하면 애플리케이션의 시작부터 요청 처리와
종료까지 명확하게 구성할 수 있다.
