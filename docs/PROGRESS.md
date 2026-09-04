# Progress: Todo 응답 DTO 경계 분리

Last updated: 2026-09-05 00:42 KST

## Goal

- SQLAlchemy `Todo` ORM 객체가 Router까지 노출되지 않도록 Service에서
  `TodoResponse`로 변환한다.

## Current Status

- Status: Ready for review
- Current focus: Service와 Router 사이의 응답 타입 분리 완료
- Branch: `feature/todo-crud`
- Related issue/PR: 없음

## Decisions

- 2026-09-05 사용자 지시에 따라 PRD 외 권장사항인 ORM 응답 분리를 적용한다.
- SSR 응답은 기존처럼 Template 또는 Redirect를 사용하고, `TodoResponse`는
  Service와 Router 사이의 DTO로 사용한다.

## Completed

- [x] ORM 속성 기반 검증을 지원하는 `TodoResponse` 스키마 정의
- [x] 조회, 생성, 수정, 완료 결과를 Service에서 `TodoResponse`로 변환
- [x] Router에서 SQLAlchemy `Todo` 의존성 제거
- [x] 메모리 SQLite를 이용한 Service 응답 변환 테스트 작성

## In Progress

- [ ] 없음

## Next Steps

1. 변경 내용 검토
2. 사용자 확인 후 커밋
3. UI 브랜치에서 Jinja2 템플릿 렌더링 검증

## Changed Files

- `app/schemas/todos.py`: `TodoResponse` 스키마 추가
- `app/services/todos.py`: ORM 객체를 `TodoResponse`로 변환
- `app/routers/todos.py`: Router의 ORM 타입 의존성 제거
- `app/repositories/todos.py`: 사용하지 않는 import 제거
- `tests/test_todo_service.py`: Service 응답 변환 테스트 추가
- `pyproject.toml`: 프로젝트 경로를 pytest import 경로로 설정
- `docs/PROGRESS.md`: 현재 작업 상태와 검증 결과 기록

## Commands Run

```text
UV_CACHE_DIR=/private/tmp/b6-2-uv-cache uv run pytest tests/test_todo_service.py -q
2 passed

UV_CACHE_DIR=/private/tmp/b6-2-uv-cache uv run ruff format .
1 file reformatted, 18 files left unchanged

UV_CACHE_DIR=/private/tmp/b6-2-uv-cache uv run ruff check .
All checks passed

UV_CACHE_DIR=/private/tmp/b6-2-uv-cache uv run pytest -q
2 passed
```

## Test Status

- Last passing: 전체 테스트 2개 통과
- Failing: 없음
- Not run: Jinja2 템플릿이 아직 없어 실제 SSR 렌더링은 미검증

## Risks / Open Questions

- `TodoResponse`의 속성 접근은 Jinja2에서 사용할 수 있지만, 템플릿 구현 후
  실제 페이지 렌더링 검증이 필요하다.
s
