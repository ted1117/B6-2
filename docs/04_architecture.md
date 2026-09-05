# **웹 애플리케이션 계층 구조**

## **학습 목표**

- 계층을 나누는 이유와 각 계층의 책임을 설명할 수 있다.
- Router, Service, Repository, ORM의 관계를 이해한다.
- 의존성 방향과 데이터 전달 경계를 설명할 수 있다.
- ORM 객체와 응답 모델을 분리하는 이유를 이해한다.
- 기능을 어느 계층에 구현해야 하는지 판단할 수 있다.

## **1. 아키텍처가 필요한 이유**

작은 프로그램은 하나의 함수 안에서 요청 처리, 검증, 데이터베이스 쿼리, HTML
생성을 모두 수행해도 실행될 수 있다. 그러나 기능이 늘어나면 변경 이유가 다른
코드가 한곳에 섞인다.

예를 들어 완료 기능에는 다음 관심사가 함께 존재한다.

- 어떤 URL과 Method로 요청을 받을 것인가
- 요청한 To-do가 존재하는가
- 완료 상태와 완료 시간을 어떻게 변경할 것인가
- 변경 내용을 데이터베이스에 어떻게 저장할 것인가
- 처리 후 어느 페이지로 이동할 것인가

계층 구조는 이 관심사를 역할에 따라 나눈다. 한 계층의 변경이 다른 계층의 세부
구현까지 번지지 않도록 경계를 만드는 것이 목적이다.

## **2. 프로젝트의 계층 구조**

이 프로젝트는 다음 방향으로 요청을 처리한다.

```text
Router
  ↓
Service
  ↓
Repository
  ↓
SQLAlchemy ORM
  ↓
SQLite
```

호출 방향은 위에서 아래로 흐른다. 아래 계층은 자신을 호출한 HTTP URL이나 HTML
Template을 알 필요가 없다.

## **3. Router 계층**

Router는 HTTP 세계와 애플리케이션 내부 로직이 만나는 경계이다.

### **3.1 담당하는 일**

- Method와 URL을 함수에 연결한다.
- Form과 Path Parameter 같은 요청 데이터를 받는다.
- FastAPI 의존성을 조립한다.
- Service를 호출한다.
- TemplateResponse, RedirectResponse, HTTP 오류를 반환한다.

```python
@router.post("/todos/{todo_id}/complete")
def complete_todo(
    todo_id: int,
    service: TodoServiceDep,
) -> RedirectResponse:
    completed = service.complete_todo(todo_id)
    ...
```

### **3.2 담당하지 않는 일**

- SQLAlchemy의 `select()`를 직접 실행하지 않는다.
- Session에 직접 `commit()`하지 않는다.
- 완료 시간을 계산하지 않는다.
- ORM 객체를 직접 생성하거나 수정하지 않는다.

Router가 HTTP 처리에 집중하면 Service를 웹 요청 없이도 테스트할 수 있다.

## **4. Service 계층**

Service는 애플리케이션의 업무 규칙을 표현한다.

### **4.1 담당하는 일**

- Repository를 통해 데이터를 조회한다.
- 생성과 수정에 필요한 도메인 규칙을 적용한다.
- 완료 여부와 `completed_at`의 관계를 관리한다.
- ORM 객체를 Router에 전달할 응답 모델로 변환한다.

```python
if not todo.is_completed:
    todo.completed_at = None
elif not was_completed:
    todo.completed_at = datetime.now()
```

이 코드는 HTTP Method나 Redirect 주소와 관계없는 완료 상태 규칙이다. 따라서
Router가 아니라 Service에 위치한다.

### **4.2 Service가 HTTP를 몰라야 하는 이유**

Service가 `Request`, `RedirectResponse`, Template에 의존하면 같은 로직을 다른
인터페이스에서 재사용하기 어렵다. Service는 Python 값과 모델을 받고 결과를
반환하도록 유지한다.

## **5. Repository 계층**

Repository는 영속성 기술과 애플리케이션 로직 사이의 경계이다.

### **5.1 담당하는 일**

- SQLAlchemy 쿼리를 작성한다.
- ORM 객체를 Session에 추가하거나 삭제한다.
- 저장을 확정하고 최신 값을 다시 읽는다.

```python
def get_by_id(self, todo_id: int) -> Todo | None:
    return self.session.get(Todo, todo_id)

def create(self, todo: Todo) -> Todo:
    self.session.add(todo)
    self.session.commit()
    self.session.refresh(todo)
    return todo
```

Repository는 요청 URL이나 HTML 화면을 알지 못한다. 나중에 저장 방식이 바뀌더라도
Service가 SQL 문법을 직접 다루지 않도록 한다.

## **6. ORM 모델 계층**

ORM 모델은 Python 클래스와 데이터베이스 테이블을 연결한다.

```python
class Todo(Base):
    __tablename__ = "todos"

    id: Mapped[int] = mapped_column(primary_key=True)
    title: Mapped[str] = mapped_column(String(100), nullable=False)
```

`Todo` 객체의 속성을 변경하면 SQLAlchemy가 변경을 추적하고, Repository가
commit할 때 SQL 문으로 변환한다. ORM 모델은 저장 구조를 표현하지만 HTTP 응답
형식을 책임지지는 않는다.

## **7. Schema와 데이터 경계**

Pydantic Schema는 계층 사이에서 전달할 데이터의 형태와 검증 조건을 정의한다.

| Schema | 목적 |
| --- | --- |
| `TodoCreate` | 생성 입력 검증 |
| `TodoUpdate` | 수정 입력과 완료 상태 검증 |
| `TodoResponse` | Service가 Router에 전달할 출력 |

Repository가 반환한 ORM 객체는 Service에서 `TodoResponse`로 변환한다.

```python
return TodoResponse.model_validate(todo)
```

Router가 ORM 객체를 직접 사용하지 않으면 데이터베이스 Session의 생명주기나
지연 로딩 같은 SQLAlchemy 동작이 HTTP 계층으로 새어 나오는 것을 줄일 수 있다.

## **8. 의존성 방향**

현재 객체 조립은 FastAPI 의존성 함수에서 이루어진다.

```text
Session
  → TodoRepository(Session)
  → TodoService(Repository)
  → Router(Service)
```

Router는 Service 인터페이스를 사용하고 Service는 Repository를 사용한다. 반대로
Repository가 Service를 호출하거나 Service가 Router를 import하면 의존성 방향이
뒤섞인다.

의존성 순환을 막기 위해 다음 기준을 사용할 수 있다.

- HTTP와 Template 관련 타입은 Router까지만 사용한다.
- SQLAlchemy Session과 쿼리는 Repository와 데이터베이스 설정에서 사용한다.
- 비즈니스 상태 변화는 Service에서 처리한다.
- 입력과 출력의 데이터 형태는 Schema로 표현한다.

## **9. 기능 위치 판단하기**

새 코드를 작성할 때 다음 질문으로 위치를 정할 수 있다.

| 질문 | 해당 계층 |
| --- | --- |
| 어떤 URL과 상태 코드를 사용할 것인가 | Router |
| 완료 시간을 언제 기록할 것인가 | Service |
| 어떤 순서로 데이터를 조회할 것인가 | Repository |
| 테이블 컬럼 타입은 무엇인가 | ORM Model |
| 입력 길이와 필수 여부는 무엇인가 | Schema |
| 화면에 어떤 HTML을 표시할 것인가 | Template |

## **10. 트랜잭션 경계**

현재 프로젝트는 Repository의 create, update, delete 메서드에서 각각 commit한다.
한 번의 요청이 한 번의 저장 작업으로 끝나는 현재 CRUD 구조에서는 이해하기
쉽다.

여러 Repository 작업이 모두 성공해야 하나의 업무가 완료되는 기능이 생기면
commit 위치를 더 높은 단위에서 관리해야 한다. 중간 작업마다 commit하면 뒤의
작업이 실패했을 때 앞의 변경만 남을 수 있기 때문이다. 트랜잭션 경계는 기능의
원자성 요구사항에 맞춰 명시적으로 정한다.

## **11. 계층 분리와 테스트**

계층이 나뉘면 테스트 범위도 구분할 수 있다.

- Service 테스트는 업무 규칙과 응답 변환에 집중한다.
- Repository 테스트는 실제 저장과 조회를 검증한다.
- UI 통합 테스트는 HTTP 요청부터 임시 SQLite까지 전체 연결을 확인한다.

모든 테스트를 가장 큰 통합 테스트로만 작성하면 실패 원인을 찾기 어렵다. 반대로
작은 단위 테스트만 작성하면 계층 연결 오류를 놓칠 수 있다. 변경 위험에 맞춰 두
종류를 조합한다.

## **프로젝트에서 확인하기**

- `app/routers/todos.py`: Router와 의존성 조립
- `app/services/todos.py`: 완료 상태를 포함한 업무 규칙
- `app/repositories/todos.py`: SQLAlchemy 영속성 처리
- `app/models/todos.py`: ORM 테이블 구조
- `app/schemas/todos.py`: 입력과 출력 데이터 모델

## **핵심 정리**

계층 구조는 코드를 파일로 나누는 형식보다 각 변경 이유를 분리하는 규칙에 가깝다.
Router는 HTTP, Service는 업무 규칙, Repository는 데이터 접근, ORM은 저장 구조를
담당한다. 의존성이 한 방향으로 흐르고 데이터 경계가 명확하면 기능을 변경하고
테스트할 때 영향을 예측하기 쉬워진다.
