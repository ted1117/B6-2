# Progress: 존재하지 않는 To-do 조회 안내

Last updated: 2026-09-05 19:18 KST

## Goal

- 존재하지 않는 To-do의 상세 또는 수정 화면을 조회하면 안내 화면을 표시한다.
- 조회 실패 응답은 `404 Not Found` 상태를 유지한다.
- 안내 화면에서 To-do 목록으로 이동할 수 있게 한다.

## Current Status

- Status: Implemented / verification complete
- Current focus: 조회 실패 결과를 404 HTML 응답으로 변환
- Branch: `feature/todo-crud`
- Base: `develop` (`ae53676`)

## Decisions

- 템플릿 파일은 `feature/todo-ui`에서 먼저 구현하고 `develop`에 반영했다.
- `feature/todo-crud`에서는 Router의 조회 실패 처리와 통합 테스트만 변경한다.
- 템플릿 파일은 URL이 아니므로 Redirect하지 않는다.
- `get_todo()`와 `update_todo_form()`이 `todos/not_found.html`을 직접 렌더링한다.
- 브라우저 안내 화면을 제공하면서 HTTP 의미를 유지하도록 상태 코드는 404를
  사용한다.
- POST 수정, 완료, 삭제의 존재하지 않는 대상 처리는 기존 JSON 404 응답을
  유지한다. 이번 범위는 GET 조회 화면이다.

## Completed

- [x] `feature/todo-ui`에 404 안내 템플릿 추가
- [x] 404 안내 템플릿을 `develop`에 fast-forward 머지 및 푸시
- [x] 존재하지 않는 상세 조회에 404 안내 화면 연결
- [x] 존재하지 않는 수정 Form 조회에 404 안내 화면 연결
- [x] 안내 문구와 목록 이동 링크 제공
- [x] 상태 코드, Content-Type, 안내 문구, 목록 링크 통합 테스트 추가

## In Progress

- [ ] 없음

## Next Steps

1. 관련 테스트와 전체 검사 실행
2. `feature/todo-crud` 커밋 및 푸시
3. `develop`에 fast-forward 머지 및 푸시

## Changed Files

- `app/routers/todos.py`: 조회 실패 시 404 안내 템플릿 반환
- `tests/test_todo_ui.py`: 404 HTML 응답과 안내 화면 검증
- `docs/PROGRESS.md`: 현재 브랜치의 구현 및 검증 상태 기록

## Test Status

- Related tests: `2 passed`, 경고 2건
- Ruff format: Python 파일 24개 변경 없음
- Ruff check: 통과
- Full test suite: `2 failed, 9 passed`, 경고 2건
- Diff check: 통과

## Commands Run

```text
UV_CACHE_DIR=/private/tmp/b6-2-not-found-uv-cache uv run pytest tests/test_todo_ui.py::test_missing_todo_pages_return_not_found -q
2 passed, 2 warnings

UV_CACHE_DIR=/private/tmp/b6-2-not-found-uv-cache uv run ruff format .
3 Markdown code examples reformatted; 범위 밖 변경은 원복, Python 파일 변경 없음

UV_CACHE_DIR=/private/tmp/b6-2-not-found-uv-cache uv run ruff check .
All checks passed

UV_CACHE_DIR=/private/tmp/b6-2-not-found-uv-cache uv run pytest -q
2 failed, 9 passed, 2 warnings

git diff --check
passed
```

## Risks / Open Questions

- 전체 테스트의 실패 2건은 공통 화면에서 `To-do` 문자열을 기대하는 기존
  테스트와 현재 `홈`/`작업` 표기가 일치하지 않아 발생한다. 404 안내 화면 관련
  테스트 2건은 통과한다.
