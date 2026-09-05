# **SQLite와 SQLAlchemy**

## **학습 목표**

- SQLite와 관계형 데이터베이스의 기본 개념을 설명할 수 있다.
- SQLAlchemy Engine, Session, ORM Model의 역할을 구분할 수 있다.
- SQLAlchemy 2 스타일로 데이터를 조회하고 저장하는 방법을 이해한다.
- commit, refresh, rollback, close의 차이를 설명할 수 있다.
- 요청 단위 Session과 `SessionLocal` 방식의 관계를 이해한다.

## **1. 관계형 데이터베이스**

관계형 데이터베이스는 데이터를 행(Row)과 열(Column)로 구성된 테이블에
저장한다. To-do 한 개가 `todos` 테이블의 한 행이고, 제목이나 완료 여부가 열이다.

```text
todos
├── id
├── title
├── description
├── is_completed
├── completed_at
├── created_at
└── updated_at
```

각 행은 기본 키인 `id`로 구분한다. 상세 조회 URL의 `todo_id`는 이 값을 사용해
하나의 행을 찾는다.

## **2. SQLite**

SQLite는 별도의 데이터베이스 서버 프로세스 없이 파일 하나에 데이터를 저장하는
관계형 데이터베이스이다. 설치와 실행이 간단해 로컬 학습 프로젝트와 소규모
애플리케이션에 적합하다.

현재 연결 주소는 다음과 같다.

```python
DATABASE_URL = "sqlite:///./todo.db"
```

`./todo.db`는 애플리케이션을 실행한 현재 디렉터리를 기준으로 한다. 파일을
삭제하면 저장된 데이터도 함께 사라지므로 실행 파일과 데이터 파일의 역할을
구분해야 한다.

SQLite도 트랜잭션과 SQL을 지원하지만 네트워크 데이터베이스와 동시성 특성이
다르다. 프로젝트 규모와 배포 요구사항이 커지면 PostgreSQL 같은 서버형
데이터베이스를 검토할 수 있다.

## **3. SQLAlchemy의 역할**

SQLAlchemy는 Python 코드와 관계형 데이터베이스 사이를 연결한다. 이 프로젝트는
ORM(Object Relational Mapping)을 사용해 테이블 행을 Python 객체로 다룬다.

```text
Python Todo 객체
  ↕ SQLAlchemy ORM
todos 테이블의 행
```

ORM을 사용해도 데이터베이스의 테이블, 기본 키, 트랜잭션 개념이 없어지는 것은
아니다. SQLAlchemy가 Python 연산을 적절한 SQL과 데이터베이스 작업으로 변환한다.

## **4. Engine**

Engine은 데이터베이스 주소와 드라이버 설정을 보관하고 실제 연결을 관리하는
출입구이다.

```python
engine = create_engine(
    DATABASE_URL,
    connect_args={"check_same_thread": False},
)
```

SQLite의 `check_same_thread=False`는 FastAPI가 요청을 처리하는 실행 환경에서
연결을 사용할 수 있도록 설정한다. 이 옵션이 Session을 전역으로 공유해도 된다는
뜻은 아니다. 각 요청은 별도의 Session을 사용한다.

Engine은 애플리케이션 수준에서 재사용할 수 있지만 Session은 작업 단위마다
생성하고 닫아야 한다.

## **5. Declarative Base와 ORM Model**

`DeclarativeBase`를 상속한 Base는 ORM Model이 공유하는 기준 클래스이다.

```python
class Base(DeclarativeBase):
    pass
```

Model은 `Mapped`와 `mapped_column()`으로 속성과 컬럼을 선언한다.

```python
class Todo(Base):
    __tablename__ = "todos"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    title: Mapped[str] = mapped_column(String(100), nullable=False)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    is_completed: Mapped[bool] = mapped_column(Boolean, default=False)
```

- `Mapped[str]`은 Python 속성 타입을 나타낸다.
- `String(100)`은 데이터베이스 컬럼 길이를 표현한다.
- `nullable=False`는 NULL을 허용하지 않는다.
- `default=False`는 새 객체의 기본 완료 상태를 지정한다.
- `primary_key=True`는 행을 식별하는 기본 키를 지정한다.

## **6. Session**

Session은 ORM 객체를 조회하고 변경하며 하나의 작업 단위를 관리한다.

```python
def get_session():
    with Session(engine) as session:
        yield session
```

FastAPI 의존성으로 요청마다 Session을 하나 만들고 요청이 끝나면 닫는다. 전역
Session 하나를 여러 요청이 공유하면 서로 다른 요청의 변경 상태와 트랜잭션이
섞일 수 있다.

### **6.1 Session과 SessionLocal의 차이**

현재 방식은 Engine을 전달해 Session을 직접 생성한다.

```python
Session(engine)
```

`SessionLocal` 방식은 설정된 Session 팩토리를 먼저 만든다.

```python
SessionLocal = sessionmaker(bind=engine)

with SessionLocal() as session:
    ...
```

두 방식 모두 호출할 때 새로운 Session을 만들 수 있다. `SessionLocal`이라는
이름은 관례일 뿐 자동으로 thread-local 객체가 되지는 않는다. 여러 생성
위치에서 `autoflush`, `expire_on_commit` 같은 옵션을 똑같이 적용해야 할 때
`sessionmaker`가 편리하다.

## **7. 데이터 조회**

기본 키로 한 행을 찾을 때는 `Session.get()`을 사용할 수 있다.

```python
todo = session.get(Todo, todo_id)
```

조건, 정렬, 여러 행 조회에는 SQLAlchemy 2 스타일의 `select()`를 사용한다.

```python
stmt = select(Todo).order_by(Todo.created_at.desc())
todos = list(session.scalars(stmt).all())
```

`select(Todo)`는 Todo 객체를 조회하는 문장을 만들고, `scalars()`는 결과 행에서
ORM 객체를 꺼낸다. `order_by`는 최신 생성 항목을 먼저 반환하도록 정렬한다.

## **8. 생성, 수정, 삭제**

### **8.1 생성**

```python
session.add(todo)
session.commit()
session.refresh(todo)
```

`add()`는 객체를 Session의 관리 대상으로 등록한다. `commit()`은 트랜잭션의
변경을 데이터베이스에 확정한다. `refresh()`는 데이터베이스가 생성한 id나 기본값
등 최신 값을 다시 읽는다.

### **8.2 수정**

Session이 조회한 ORM 객체의 속성을 변경하면 SQLAlchemy가 변경을 추적한다.

```python
todo.title = todo_update.title
todo.is_completed = todo_update.is_completed
session.commit()
session.refresh(todo)
```

### **8.3 삭제**

```python
session.delete(todo)
session.commit()
```

`delete()` 호출만으로 데이터베이스 변경이 확정되지는 않는다. commit이 성공해야
삭제가 영구 반영된다.

## **9. commit, refresh, rollback, close**

| 메서드 | 역할 |
| --- | --- |
| `commit()` | 현재 트랜잭션의 변경을 확정 |
| `refresh()` | 데이터베이스의 최신 값을 객체에 다시 반영 |
| `rollback()` | 실패한 트랜잭션이나 미확정 변경을 되돌림 |
| `close()` | Session이 사용한 자원을 정리 |

이 네 동작은 서로 대신할 수 없다. close한다고 자동으로 commit되는 것이 아니고,
refresh한다고 변경이 저장되는 것도 아니다.

데이터베이스 오류가 발생한 뒤 같은 Session을 계속 사용해야 한다면 rollback으로
실패 상태를 정리해야 한다. 현재 요청 단위 구조에서는 예외가 요청 밖으로
전파되면 `with` 블록 종료와 함께 Session이 닫히지만, 명시적인 오류 처리나 여러
작업을 묶는 구조에서는 rollback 경계를 분명히 해야 한다.

## **10. 날짜와 상태 값**

Model은 생성, 수정, 완료 시간을 서로 다른 의미로 저장한다.

```text
created_at   최초 생성 시각
updated_at   마지막 수정 시각
completed_at 완료 상태가 된 시각 또는 None
```

`is_completed=False`라면 `completed_at=None`, 완료됐다면 완료 시각이 존재하도록
Service가 상태 관계를 관리한다. 데이터베이스 컬럼 정의만으로 모든 업무 규칙이
자동 보장되는 것은 아니다.

## **11. 테이블 생성과 마이그레이션**

애플리케이션 시작 시 다음 코드가 현재 Model에 없는 테이블을 만든다.

```python
Base.metadata.create_all(bind=engine)
```

`create_all`은 빠른 초기 실행에는 편리하지만 기존 컬럼의 이름이나 타입을 안전하게
변경하는 이력 관리 도구가 아니다. 스키마 변경 이력을 여러 환경에 같은 순서로
적용해야 한다면 Alembic 같은 마이그레이션 도구가 필요하다.

## **12. 테스트 데이터베이스 격리**

테스트는 `tmp_path`에 별도 SQLite 파일을 만들고 Session 의존성을 교체한다.

```text
실행 데이터: 프로젝트 루트/todo.db
테스트 데이터: pytest 임시 디렉터리/todo-ui.db
```

테스트 실행이 실제 데이터를 생성하거나 삭제하지 않게 만드는 것이 핵심이다.
테스트가 끝나면 Engine을 dispose해 사용한 연결도 정리한다.

## **프로젝트에서 확인하기**

- `app/core/database.py`: Engine, Base, Session 의존성
- `app/models/todos.py`: Todo ORM Model
- `app/repositories/todos.py`: 조회, 생성, 수정, 삭제
- `app/services/todos.py`: 완료 상태와 시간 규칙
- `tests/test_todo_ui.py`: 임시 SQLite와 의존성 교체

## **핵심 정리**

Engine은 데이터베이스 연결 설정을 관리하고, Session은 요청의 조회와 변경 작업을
관리하며, ORM Model은 테이블 구조를 Python 클래스로 표현한다. 변경은 commit해야
확정되고 Session은 작업이 끝나면 닫아야 한다. 현재 프로젝트의 직접 Session 생성
방식과 SessionLocal 방식은 모두 요청 단위 Session을 만들 수 있으며, 차이는 세션
생성 설정을 팩토리로 모아 재사용하는지에 있다.
