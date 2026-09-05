# To-do SSR 웹 애플리케이션

FastAPI와 Jinja2로 구현한 서버 사이드 렌더링 방식의 To-do CRUD 웹
애플리케이션입니다. 브라우저에서 작업을 생성하고 조회하며, 내용과 완료 상태를
수정하거나 작업을 삭제할 수 있습니다.

## 실행 환경

| 구분 | 사용 기술 |
| --- | --- |
| Python | 3.12 이상 |
| 패키지 관리 | uv |
| 웹 프레임워크 | FastAPI |
| 템플릿 엔진 | Jinja2 |
| ORM | SQLAlchemy 2 |
| 데이터베이스 | SQLite |

## 실행 방법

먼저 저장소를 내려받고 프로젝트 디렉터리로 이동합니다.

```bash
git clone https://github.com/ted1117/B6-2.git
cd B6-2
```

### 1. 가상환경 생성

Python 3.12를 사용하는 `.venv` 가상환경을 생성합니다.

```bash
uv venv --python 3.12
```

macOS 또는 Linux에서는 다음 명령으로 가상환경을 활성화합니다.

```bash
source .venv/bin/activate
```

Windows PowerShell에서는 다음 명령을 사용합니다.

```powershell
.venv\Scripts\Activate.ps1
```

### 2. 패키지 설치

`pyproject.toml`과 `uv.lock`을 기준으로 필요한 패키지를 설치합니다.

```bash
uv sync
```

### 3. 서버 실행

FastAPI 개발 서버를 실행합니다.

```bash
uv run fastapi dev
```

서버가 시작되면 브라우저에서 다음 주소로 접속합니다.

```text
http://127.0.0.1:8000
```

애플리케이션을 처음 실행하면 프로젝트 루트에 `todo.db` SQLite 데이터베이스
파일이 생성됩니다. 서버를 종료하려면 터미널에서 `Ctrl+C`를 누릅니다.

## 주요 기능

- To-do 목록 및 상세 조회
- To-do 생성과 수정
- 완료 상태 변경
- 삭제 전 확인과 삭제
- HTML Form을 이용한 데이터 입력
- 데이터 변경 후 `303 See Other`로 이동하는 PRG 패턴

## 검사 방법

전체 테스트를 실행합니다.

```bash
uv run pytest
```

코드 스타일과 정적 검사를 실행합니다.

```bash
uv run ruff check .
```

## 관련 문서

- [요구사항](docs/PRD.md)
- [작업 진행 상태](docs/PROGRESS.md)

### 학습 문서

1. [웹 애플리케이션과 HTTP](docs/01_web_http.md)
2. [FastAPI의 기본 구조](docs/02_fastapi.md)
3. [HTML Form과 서버 사이드 렌더링](docs/03_form_ssr.md)
4. [웹 애플리케이션 계층 구조](docs/04_architecture.md)
5. [SQLite와 SQLAlchemy](docs/05_database_sqlalchemy.md)
6. [검증과 오류 처리](docs/06_error_handling.md)
7. [요청과 응답의 전체 흐름](docs/07_request_response_flow.md)
