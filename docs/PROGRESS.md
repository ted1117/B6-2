# Progress: Todo SSR HTML Form UI

Last updated: 2026-09-05 00:57 KST

## Goal

- PRD-B6-2의 Home, Todo 목록, 생성, 상세, 수정 화면을 Jinja2로 구현한다.
- 생성, 수정, 완료, 삭제 기능을 HTML Form과 기존 POST 엔드포인트로 연결한다.

## Current Status

- Status: Ready for review
- Current focus: SSR 화면 및 HTML Form 구현과 통합 검증 완료
- Branch: `feature/todo-ui`
- Related issue/PR: 없음

## Decisions

- 2026-09-05 기존 Router / Service / Repository 구현은 변경하지 않고,
  라우터가 참조하는 Jinja2 템플릿을 추가한다.
- 데이터 변경 기능은 모두 `method="post"` Form으로 연결하고 기존 303 PRG
  동작을 유지한다.
- 공통 레이아웃과 최소 스타일은 `base.html`에서 재사용하며 별도 정적 파일
  구성은 추가하지 않는다.

## Completed

- [x] 애플리케이션 이름과 Todo 목록/생성 링크가 있는 Home 화면
- [x] 카드 형태의 Todo 목록, 완료 상태, 상세 링크 및 완료 Form
- [x] `title`, `description` 필드를 제공하는 Todo 생성 Form
- [x] 제목, 상세 내용, 완료 여부, 생성 일시와 수정/삭제/목록 기능을 제공하는
      Todo 상세 화면
- [x] 기존 값을 표시하고 `is_completed`를 변경할 수 있는 Todo 수정 Form
- [x] 공통 레이아웃, 반응형 기본 스타일 및 기본 접근성 보완
- [x] 임시 SQLite를 사용하는 SSR/Form/PRG 통합 테스트
- [x] 임시 서버와 실제 브라우저를 이용한 생성, 수정, 목록 화면 확인

## In Progress

- [ ] 없음

## Next Steps

1. 변경 내용 검토
2. 사용자 확인 후 커밋

## Changed Files

- `app/templates/base.html`: 공통 문서 구조, 탐색 메뉴 및 기본 스타일
- `app/templates/home.html`: Home 화면
- `app/templates/todos/list.html`: Todo 목록 및 완료 Form
- `app/templates/todos/new.html`: Todo 생성 Form
- `app/templates/todos/detail.html`: Todo 상세 및 삭제 Form
- `app/templates/todos/edit.html`: Todo 수정 Form
- `tests/test_todo_ui.py`: SSR 화면, Form 구조, PRG 및 저장 결과 통합 테스트
- `docs/PROGRESS.md`: 현재 UI 구현 상태와 검증 결과 기록

## Commands Run

```text
UV_CACHE_DIR=/private/tmp/b6-2-ui-uv-cache uv run pytest tests/test_todo_ui.py -q
7 passed, 2 warnings

UV_CACHE_DIR=/private/tmp/b6-2-ui-uv-cache uv run ruff format .
20 files left unchanged

UV_CACHE_DIR=/private/tmp/b6-2-ui-uv-cache uv run ruff check .
All checks passed

UV_CACHE_DIR=/private/tmp/b6-2-ui-uv-cache uv run pytest -q
9 passed, 2 warnings

git diff --check
passed

임시 SQLite에서 FastAPI 서버 실행 후 실제 브라우저 확인
Home / 생성 Form / 생성 303 / 상세 / 수정 Form / 수정 303 / 목록 모두 정상
```

## Test Status

- Last passing: 전체 테스트 9개 통과
- Failing: 없음
- Browser check: 생성 및 수정 Form, PRG, 상세와 목록 렌더링 확인
- Not run: 없음

## Risks / Open Questions

- 테스트 경고 2건은 FastAPI TestClient가 사용하는 Starlette/httpx 및 anyio의
  deprecated API에 대한 의존성 경고이며 현재 테스트 실패는 아니다.
