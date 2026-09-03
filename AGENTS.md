# AGENTS.md

## 기술 스택

- Python 3.12
- FastAPI
- SQLAlchemy 2
- SQLite
- Jinja2

## 문서

기능을 구현하거나 수정하기 전에 아래 문서를 먼저 확인합니다.

- `docs/PROGRESS.md`: 현재 작업 진행 상태를 확인합니다.
- `docs/PRD.md`: 구현 대상 기능의 PRD를 확인합니다.
  - 구현은 지정된 PRD를 최우선 기준으로 합니다.
  - 구현 대상 PRD가 명확하지 않은 경우 사용자에게 확인합니다.

## 작업 원칙

- 요청받은 범위만 구현합니다.
- 요청받지 않은 기능을 추가하지 않습니다.
- 요청받지 않은 리팩토링을 수행하지 않습니다.
- 기존 코드 스타일과 프로젝트 구조를 우선합니다.
- 불필요한 추상화나 과도한 구조화를 피합니다.
- 큰 구조 변경이 필요한 경우 구현 전에 변경 계획을 제시합니다.
- PRD와 사용자의 지시가 상충하는 경우 사용자에게 우선순위를 확인합니다.
- PRD에 정의되지 않은 요구사항이나 엣지 케이스를 발견하면 사용자에게 알리고 PRD 업데이트를 제안합니다.
- 기능 구현이 완료되면 `docs/PROGRESS.md`를 갱신합니다.

## 프로젝트 구조

기본적으로 다음 계층을 사용합니다.

```text
Router
  ↓
Service
  ↓
Repository
  ↓
SQLAlchemy
  ↓
SQLite
```

### Router

- HTTP 요청 및 응답 처리를 담당합니다.
- Form, Path Parameter 등 요청 데이터를 처리합니다.
- FastAPI 의존성을 조립합니다.
- Service를 호출합니다.
- Jinja2 Template 또는 Redirect 응답을 반환합니다.
- 비즈니스 로직을 작성하지 않습니다.
- SQLAlchemy를 통한 직접적인 DB 접근을 수행하지 않습니다.

### Service

- 비즈니스 로직을 담당합니다.
- 필요한 입력값 검증을 수행합니다.
- Repository를 통해 데이터를 조회하거나 변경합니다.
- HTTP 요청/응답이나 Template에 의존하지 않습니다.

### Repository

- SQLAlchemy를 이용한 데이터 접근을 담당합니다.
- 조회, 생성, 수정, 삭제와 관련된 영속성 로직을 처리합니다.
- HTTP 요청/응답이나 Template에 의존하지 않습니다.

## FastAPI

- 의존성 주입은 `Depends()`를 파라미터 기본값으로 직접 작성하기보다 `Annotated`를 우선 사용합니다.
- 반복해서 사용하는 의존성은 타입 별칭으로 정의하여 재사용합니다.
- 의존성 함수의 파라미터와 반환값에 타입 힌트를 작성합니다.
- SSR 페이지는 Jinja2를 이용하여 렌더링합니다.
- 사용자 입력은 HTML Form을 통해 처리합니다.
- 데이터 변경 요청은 POST를 사용합니다.
- Create, Update, Delete 처리 후 PRG(Post-Redirect-Get) 패턴을 적용합니다.
- PRG Redirect에는 `303 See Other`를 사용합니다.

## 데이터베이스

- SQLAlchemy 2 스타일을 사용합니다.
- 데이터베이스는 SQLite를 사용합니다.
- ORM 모델은 `Mapped`와 `mapped_column()`을 사용합니다.
- 조회 쿼리는 `select()` 사용을 우선합니다.
- DB Session은 FastAPI 의존성 주입을 통해 전달합니다.
- Session이나 Connection을 전역 상태로 직접 공유하지 않습니다.
- 요청 단위 Session은 `yield` dependency를 사용하여 관리합니다.
- 반복해서 사용하는 Session dependency는 `Annotated` 타입 별칭으로 정의합니다.
- Router에서 직접 SQLAlchemy 쿼리를 작성하지 않습니다.
- 데이터 접근은 Repository를 통해 수행합니다.
- 트랜잭션 경계가 필요한 경우 명시적으로 관리합니다.

## 타입 힌트

- 함수와 메서드의 파라미터 및 반환값에 타입 힌트를 작성합니다.
- 클래스 속성에도 가능한 경우 타입을 명시합니다.
- `Any` 사용은 필요한 경우로 제한합니다.
- `dict`, `list`, `tuple` 등은 Python 3.12 기본 제네릭 문법을 사용합니다.
- FastAPI DI처럼 타입 정보와 메타데이터를 함께 표현할 때는 `Annotated`를 우선 사용합니다.

## 테스트

- 테스트는 `pytest`를 사용합니다.
- 새로운 기능에는 해당 기능을 검증하는 최소한의 테스트를 작성합니다.
- 기능 구현 또는 수정 후 관련 테스트를 실행합니다.
- 작업 완료 전 전체 테스트를 실행합니다.

```bash
uv run pytest
```

## 코드 스타일

- Python 코드는 `ruff format`으로 포맷팅합니다.
- Ruff를 이용하여 lint 및 import 정렬을 수행합니다.
- import는 절대 경로를 우선 사용합니다.
- 기존 프로젝트의 네이밍과 코드 스타일을 유지합니다.
- 불필요한 주석은 작성하지 않습니다.
- 코드 자체로 의도가 명확하지 않은 경우에만 주석을 작성합니다.
- 함수와 메서드의 파라미터 및 반환값에 타입 힌트를 작성합니다.

작업 완료 전 다음 명령을 실행합니다.

```bash
uv run ruff format .
uv run ruff check .
uv run pytest
```

## 실행 및 패키지 관리

- Python 패키지는 `uv`를 사용하여 관리합니다.

FastAPI 개발 서버 실행:

```bash
uv run fastapi dev
```

## 작업 완료

기능 구현이 완료되면 다음을 수행합니다.

1. 관련 테스트를 실행합니다.
2. Ruff 검사 및 포맷팅을 수행합니다.
3. 전체 테스트를 실행합니다.
4. `docs/PROGRESS.md`에 구현 상태를 반영합니다.
5. 변경한 파일과 구현 내용을 요약하여 보고합니다.