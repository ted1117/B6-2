# Progress: 할 일 SSR UI 배치 개선

Last updated: 2026-09-05 13:30 KST

## Goal

- PRD-B6-2의 SSR 화면에서 기존 색상을 유지하며 목록과 상세 배치를 개선한다.
- UI의 `Todo` 표기를 `할 일`로 통일한다.
- 완료와 삭제 확인을 JavaScript 없이 HTML과 기존 POST 엔드포인트로 처리한다.
- 템플릿의 CSS를 `app/static/css/style.css`로 분리한다.

## Current Status

- Status: Ready for review
- Current focus: UI 배치 개선 및 CSS 정적 파일 분리와 검증 완료
- Branch: `feature/todo-ui`
- Related issue/PR: 없음

## Decisions

- 2026-09-05 기존 Router / Service / Repository 구현은 변경하지 않고,
  라우터가 참조하는 Jinja2 템플릿을 추가한다.
- 데이터 변경 기능은 모두 `method="post"` Form으로 연결하고 기존 303 PRG
  동작을 유지한다.
- 공통 레이아웃은 `base.html`에서 재사용한다. 사용자 후속 지시에 따라
  CSS는 `app/static/css/style.css`로 옮기고 `url_for('static', ...)`로 연결한다.
- `app/main.py`에서 `/static`을 마운트한다. 정적 파일 경로는 `__file__`을
  기준으로 지정해 실행 디렉토리에 영향을 받지 않도록 한다.
- 2026-09-05 사용자 후속 지시에 따라 목록 완료 기능은 체크박스 대신 버튼을
  사용하며, 목록과 상세에서 제목 오른쪽에 배치한다. 완료된 항목은 버튼을
  비활성화하고, 목록 제목은 회색 취소선으로 구분한다.
- 상세의 제목/상태, 본문, 생성 일시, 하단 작업 영역을 분리한다.
- 삭제 버튼은 HTML `dialog popover`와 `popovertarget`으로 확인창을 연다.
  취소 또는 Escape는 창만 닫고, 확인창 안의 삭제 버튼이 POST를 전송한다.
- JavaScript, 인라인 이벤트 핸들러, 새 할 일 엔드포인트를 추가하지 않는다.
  라우터 변경은 홈 이름과 사용자에게 표시되는 404 문구의 한국어 표기뿐이다.

## Completed

- [x] 애플리케이션 이름과 할 일 목록/생성 링크가 있는 Home 화면
- [x] 카드 형태의 할 일 목록, 완료 상태, 상세 링크 및 완료 Form
- [x] 목록 상단의 새 할 일 버튼과 각 카드의 완료 버튼 오른쪽 배치
- [x] 기본 글자색의 제목 링크 및 완료된 제목의 회색 취소선
- [x] `title`, `description` 필드를 제공하는 할 일 생성 Form
- [x] 제목, 상세 내용, 완료 여부, 생성 일시와 수정/삭제/목록 기능을 제공하는
      할 일 상세 화면
- [x] 상세 제목/본문/날짜 영역 분리와 완료 버튼 추가
- [x] JavaScript 없는 삭제 확인창 및 취소 동작
- [x] 기존 값을 표시하고 `is_completed`를 변경할 수 있는 할 일 수정 Form
- [x] 공통 레이아웃, 반응형 기본 스타일 및 기본 접근성 보완
- [x] 임시 SQLite를 사용하는 SSR/Form/PRG 통합 테스트
- [x] 임시 서버와 실제 브라우저를 이용한 생성, 수정, 목록 화면 확인
- [x] JavaScript를 끈 Chromium에서 목록/상세 완료와 삭제 확인/취소/삭제 확인
- [x] 데스크톱 및 375px/320px 화면에서 긴 제목의 줄바꿈과 버튼 배치 확인
- [x] 기존 CSS 선언을 유지하며 외부 CSS 파일로 분리하고 공통 템플릿에 연결
- [x] 다른 실행 디렉토리에서도 CSS 링크가 200 응답과 `text/css`를 반환하는지 검증

## In Progress

- [ ] 없음

## Next Steps

1. 변경 내용 검토
2. 사용자 확인 후 커밋

## Changed Files

- `app/templates/base.html`: 공통 레이아웃 및 외부 CSS 링크
- `app/static/css/style.css`: 기존 목록/상세 배치, 완료 제목, 확인창과 반응형 스타일
- `app/main.py`: `/static` 경로의 정적 파일 제공 설정
- `app/templates/home.html`: 할 일 목록/생성 문구
- `app/templates/todos/list.html`: 오른쪽 새 할 일/완료 버튼 및 완료 상태 구분
- `app/templates/todos/new.html`: 할 일 생성 문구
- `app/templates/todos/detail.html`: 제목/본문/날짜 영역, 완료 Form, 삭제 확인창
- `app/templates/todos/edit.html`: 할 일 수정 문구
- `app/routers/todos.py`: 홈 이름 및 404 문구의 `할 일` 표기
- `tests/test_todo_ui.py`: 한국어 UI, JavaScript 부재, 완료 버튼 상태와 삭제
  확인창 Form, 정적 CSS 제공 검증 및 기존 CRUD/303/저장 결과 테스트
- `docs/PROGRESS.md`: 현재 UI 구현 상태와 검증 결과 기록

## Commands Run

```text
UV_CACHE_DIR=/private/tmp/b6-2-ui-uv-cache uv run pytest tests/test_todo_ui.py -q
9 passed, 2 warnings

UV_CACHE_DIR=/private/tmp/b6-2-ui-uv-cache uv run ruff format .
20 files left unchanged

UV_CACHE_DIR=/private/tmp/b6-2-ui-uv-cache uv run ruff check .
All checks passed

UV_CACHE_DIR=/private/tmp/b6-2-ui-uv-cache uv run pytest
11 passed, 2 warnings

git diff --check
passed

CSS 분리 전후 선언 내용 동일함을 확인

이전 UI 배치 검증: 임시 SQLite + Chromium 141.0.7390.37 (javaScriptEnabled: false)
생성 Form / 목록 완료 303 / 상세 완료 303 / 완료 후 비활성 버튼 정상
삭제 확인창 열기 / 취소 버튼 초기 포커스 / 취소 / Escape / 삭제 303 정상
제목 링크 색상 / 완료 취소선 / 새 할 일 및 완료 버튼 오른쪽 배치 정상
상세 제목·본문·날짜 영역 분리 / 375px·320px 긴 제목 줄바꿈 정상
```

## Test Status

- Last passing: 전체 테스트 11개 통과
- Failing: 없음
- Browser check (CSS 분리 전): JavaScript 비활성 상태에서 생성, 목록/상세 완료, 삭제 확인과
  취소/Escape/삭제, 데스크톱/모바일 배치 확인. 임시 DB로 검증했다.
- CSS check: 분리 전후 선언 내용 동일, HTML CSS 링크 및 정적 파일 응답 검증 통과
- Not run: CSS 분리 후 브라우저 재확인, 다른 브라우저의 수동 확인

## Risks / Open Questions

- 테스트 경고 2건은 FastAPI TestClient가 사용하는 Starlette/httpx 및 anyio의
  deprecated API에 대한 의존성 경고이며 현재 테스트 실패는 아니다.
- 삭제 확인창은 HTML Popover 지원 브라우저를 전제로 한다. 배경 상호작용을
  차단하는 모달이 아니며, 바깥 클릭 또는 Escape로 닫을 수 있다.
- PRD 반영 제안: 이번 사용자 지시의 세부 배치, 상세 완료 버튼, JavaScript
  없는 삭제 확인창을 화면 명세에 추가한다. `docs/PRD.md`는 수정하지 않았다.
