# PRD-B6-2: 게시물 CRUD 웹 서비스

## 개요

FastAPI를 기반으로 단일 도메인을 관리하는 SSR 웹 애플리케이션을 구현합니다.

사용자는 브라우저에서 데이터를 등록하고, 목록을 조회하고, 상세 내용을 확인하며, 수정 및 삭제를 수행할 수 있습니다.

---

## 기술 스택

- Python 3.12
- FastAPI
- SQLAlchemy
- SQLite
- Jinja2

---

## 사용자

### 일반 사용자

브라우저에서 데이터를 관리합니다.

- 데이터 목록 조회
- 데이터 상세 조회
- 데이트 등록
- 데이터 수정
- 데이터 삭제

---

## 사용자 스토리

### US-01: 목록 조회

**As A** 사용자  
**I want to** 등록된 Todo 목록을 확인한다  
**So that** 현재 해야 할 일을 확인할 수 있다.  

### US-02: 상세 조회

**As a** 사용자  
**I want to** 특정 Todo의 상세 내용을 확인한다.  
**So that** 해당 Todo의 전체 정보를 확인한다.  

### US-03: 생성

**As a** 사용자  
**I want to** 새로운 Todo를 등록한다.  
**So that** 해야 할 일을 기록할 수 있다.  

### US-04: 수정

**As a** 사용자  
**I want to** 기존 todo의 내용을 수정한다.  
**So that** 변경된 할 일을 반영할 수 있다.  

### US-05: 삭제

**As a** 사용자  
**I want to** 필요하지 않은 Todo를 삭제한다.  
**So that** 목록에서 불필요한 항목을 삭제할 수 있다.  

### US-06: 완료 상태 관리

**As a** 사용자  
**I want to** Todo의 완료 여부를 설정하고 싶다.  
**So that** 완료한 일과 아직 완료하지 않은 일을 구분할 수 있다.  

### US-07: 제목 검색

**As a** 사용자  
**I want to** 제목 또는 내용을 선택해 검색한다.  
**So that** 원하는 할 일을 빠르게 찾을 수 있다.  

---

## 화면 명세

```
Home
  │
  └── Todo List
        │
        ├── Todo Create
        ├── Todo Complete
        └── Todo Detail
              │
              ├── Todo Edit
              └── Todo Delete
```

### Home

```GET /```

- 애플리케이션 이름 표시
- Todo 목록으로 이동할 수 있는 링크 제공
- Todo 생성 화면으로 이동할 수 있는 링크 제공

### Todo List

```GET /todos```

- 각 Todo를 카드 형식으로 표시
  - 제목
  - 완료 여부
- 각 Todo는 상세 화면으로 이동
- Todo 생성 화면으로 이동할 수 있는 링크 제공
- Form
  - search_by
    - 검색 대상 선택
    - title: 제목, 기본값
    - description: 내용
  - q
    - 검색어
- 버튼 혹은 링크
  - 검색
  - 검색 초기화
- 검색 처리
  - GET 요청의 쿼리 파라미터로 검색 대상과 검색어 전달
  - 선택한 제목 또는 내용에 검색어가 포함된 Todo 조회
  - 검색어 앞뒤 공백 제거
  - 검색어가 없거나 공백뿐이면 전체 목록 표시
  - 검색 결과 화면에서 검색 대상과 검색어 유지
  - 검색 결과가 없으면 “검색 결과가 없습니다.” 표시
  - 검색 초기화 시 `/todos`로 이동하고 검색 대상을 제목으로 설정
  - 기존 생성 일시 내림차순 정렬 유지

### Todo Detail

```GET /todos/{todo_id}```

- 표시 항목
  - 제목
  - 상세 내용
  - 완료 여부
  - 생성 일시
- 제공 기능
  - 수정
  - 삭제
  - 목록으로 이동

### Todo Create

```GET /todos/new```

- Form
  - title
  - description
- 버튼 혹은 링크
  - 생성
  - 취소

### Todo Edit

```GET /todos/{todo_id}/edit```

- Form
  - title
  - description
  - is_completed
- 버튼 혹은 링크
  - 저장
  - 취소

---

## 엔드포인트 명세

| Method | Endpoint | 설명 |
| --- | --- | --- |
| GET | `/` | 홈 |
| GET | `/todos` | Todo 목록 |
| GET | `/todos/new` | Todo 생성 Form |
| POST | `/todos` | Todo 생성 |
| GET | `/todos/{todo_id}` | Todo 상세 |
| GET | `/todos/{todo_id}/edit` | Todo 수정 Form |
| POST | `/todos/{todo_id}/edit` | Todo 수정 |
| POST | `/todos/{todo_id}/complete` | Todo 완료 |
| POST | `/todos/{todo_id}/delete` | Todo 삭제 |


---

## PRG

Create, Update, Delete 요청에는 PRG(Post-Redirect-Get) 패턴을 적용합니다.

### 생성

```
POST /todos
  ↓
Todo 생성
  ↓
303 See Other
  ↓
GET /todos/{todo_id}
```

### 수정

```
POST /todos/{todo_id}/edit
  ↓
Todo 수정
  ↓
303 See Other
  ↓
GET /todos/{todo_id}
```

### 삭제

```
POST /todos/{todo_id}/delete
  ↓
Todo 삭제
  ↓
303 See Other
  ↓
GET /todos
```

### 완료

```
POST /todos/{todo_id}/complete
  ↓
Todo 완료 상태 변경
  ↓
303 See Other
  ↓
GET /todos
```

---

## 아키텍처

```
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

---

## 구현 범위

### 포함

- Todo 생성
- Todo 목록 및 상세 조회
- Todo 수정
- Todo 삭제
- Todo 완료 상태 변경
- Jinja2 기반 SSR
- HTML Form 기반 사용자 입력
- SQLAlchemy ORM을 이용한 SQLite 데이터 저장
- Router / Service / Repository 계층 분리
- POST 요청에 대한 PRG 패턴 적용

### 제외

- 회원가입 및 로그인
- 사용자별 Todo 관리
- REST API
- 검색, 정렬 및 페이지네이션
- 카테고리 및 태그
- 우선순위 및 마감일
- 파일 업로드
- 외부 API 연동
- Docker 및 배포
