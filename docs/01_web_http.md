# **웹 애플리케이션과 HTTP**

## **학습 목표**

- 웹 애플리케이션에서 클라이언트와 서버의 역할을 설명할 수 있다.
- HTTP 요청과 응답의 기본 구조를 설명할 수 있다.
- GET과 POST의 차이를 설명할 수 있다.
- URL과 라우팅의 관계를 이해한다.
- 주요 HTTP 상태 코드의 의미를 설명할 수 있다.

## **1. 클라이언트와 서버**

웹 애플리케이션은 네트워크를 통해 서로 메시지를 주고받는 클라이언트와 서버로
구성된다. 이 프로젝트에서는 웹 브라우저가 클라이언트이고 FastAPI
애플리케이션이 서버이다.

### **1.1 웹 브라우저의 역할**

브라우저는 사용자가 입력한 주소나 클릭한 링크를 바탕으로 서버에 요청을 보낸다.
서버가 반환한 HTML을 해석해 화면을 그리고, HTML에서 참조하는 CSS와 같은 추가
파일도 다시 요청한다. Form을 제출할 때는 입력값을 HTTP 요청 데이터로 변환한다.

브라우저가 담당하는 주요 작업은 다음과 같다.

- URL을 해석하고 서버에 HTTP 요청을 보낸다.
- HTML 요소를 문서 구조로 변환한다.
- CSS를 적용해 화면을 표시한다.
- 링크 이동이나 Form 제출 같은 사용자 동작을 새로운 요청으로 바꾼다.
- Redirect 응답을 받으면 서버가 알려준 주소로 다시 요청한다.

### **1.2 웹 서버의 역할**

서버는 요청의 Method와 URL을 확인하고 연결된 기능을 실행한다. 필요한 경우
데이터베이스를 조회하거나 변경한 뒤 HTML, Redirect 또는 오류 응답을 반환한다.

이 프로젝트의 서버는 다음 순서로 동작한다.

```text
브라우저 요청
  → FastAPI Router
  → Service
  → Repository
  → SQLite
  → HTML 또는 Redirect 응답
```

### **1.3 요청과 응답**

클라이언트가 서버에 보내는 메시지를 요청(Request), 서버가 처리 결과로 보내는
메시지를 응답(Response)이라고 한다. 서버가 먼저 브라우저 화면을 직접 바꾸는
것이 아니라, 브라우저가 보낸 요청에 응답을 돌려주면 브라우저가 그 응답을
해석해 화면을 바꾼다.

예를 들어 사용자가 `/todos`에 접속하면 다음 과정이 진행된다.

1. 브라우저가 `GET /todos` 요청을 보낸다.
2. FastAPI가 `/todos`와 GET에 연결된 함수를 찾는다.
3. 서버가 SQLite에서 To-do 목록을 조회한다.
4. Jinja2가 조회 결과를 HTML에 넣는다.
5. 서버가 `200 OK`와 HTML 본문을 반환한다.
6. 브라우저가 HTML을 화면에 표시한다.

## **2. HTTP**

HTTP(Hypertext Transfer Protocol)는 클라이언트와 서버가 요청과 응답을 교환하는
규칙이다. 서로 다른 브라우저와 서버가 같은 형식으로 통신할 수 있도록 Method,
URL, Header, Body와 상태 코드의 의미를 정의한다.

### **2.1 HTTP 요청의 기본 구조**

HTTP 요청은 다음 네 요소로 이해할 수 있다.

| 요소 | 의미 | 예시 |
| --- | --- | --- |
| Method | 서버에 원하는 동작 | `GET`, `POST` |
| URL | 요청할 자원의 위치 | `/todos/1` |
| Header | 요청에 관한 부가 정보 | `Content-Type` |
| Body | 서버에 전달할 데이터 | Form의 제목과 상세 내용 |

목록을 조회하는 요청은 개념적으로 다음과 같다.

```http
GET /todos HTTP/1.1
Host: 127.0.0.1:8000
```

새 To-do를 만드는 요청은 Body에 Form 데이터를 포함한다.

```http
POST /todos HTTP/1.1
Host: 127.0.0.1:8000
Content-Type: application/x-www-form-urlencoded

title=HTTP+공부&description=요청과+응답+정리
```

### **2.2 HTTP 응답의 기본 구조**

응답은 상태 코드, Header, Body로 구성된다.

| 요소 | 의미 | 예시 |
| --- | --- | --- |
| Status Code | 요청 처리 결과 | `200`, `303`, `404` |
| Header | 응답에 관한 부가 정보 | `Content-Type`, `Location` |
| Body | 클라이언트가 사용할 결과 | HTML 또는 오류 정보 |

정상적인 HTML 응답은 다음과 같은 형태이다.

```http
HTTP/1.1 200 OK
Content-Type: text/html; charset=utf-8

<!doctype html>
<html lang="ko">...</html>
```

Redirect 응답은 이동할 주소를 `Location` Header에 담는다.

```http
HTTP/1.1 303 See Other
Location: /todos/1
```

## **3. URL과 라우팅**

URL은 클라이언트가 접근하려는 자원의 위치를 표현한다. 이 프로젝트를 로컬에서
실행할 때 `http://127.0.0.1:8000/todos/1`은 다음 부분으로 나눌 수 있다.

| 부분 | 값 | 의미 |
| --- | --- | --- |
| Scheme | `http` | 사용할 통신 방식 |
| Host | `127.0.0.1` | 서버 주소 |
| Port | `8000` | 서버 프로그램이 기다리는 포트 |
| Path | `/todos/1` | 서버 안에서 요청할 자원 |

라우팅은 Method와 Path의 조합을 처리 함수에 연결하는 작업이다.

```python
@router.get("/todos/{todo_id}")
def get_todo(todo_id: int, ...):
    ...
```

`{todo_id}`는 Path Parameter이다. `/todos/1` 요청에서는 정수 `1`이 함수의
`todo_id`로 전달된다.

같은 Path라도 Method가 다르면 별개의 요청이다.

| Method | Path | 역할 |
| --- | --- | --- |
| `GET` | `/todos` | 목록 조회 |
| `POST` | `/todos` | 새 To-do 생성 |

따라서 URL만 보고 기능을 구분하지 않고 Method까지 함께 확인해야 한다.

## **4. GET과 POST**

HTTP Method는 서버가 자원에 대해 수행할 동작의 성격을 나타낸다. 이 프로젝트는
화면과 데이터를 조회할 때 GET을 사용하고, 데이터를 변경할 때 POST를 사용한다.

### **4.1 GET**

GET은 자원을 조회할 때 사용한다. 일반적으로 요청 데이터는 Path나 Query String에
표현하며, 같은 요청을 반복해도 서버 상태가 바뀌지 않아야 한다.

```text
GET /
GET /todos
GET /todos/new
GET /todos/1
GET /todos/1/edit
```

생성 화면과 수정 화면도 데이터를 변경하지 않고 HTML Form을 보여주기만 하므로
GET을 사용한다.

### **4.2 POST**

POST는 서버의 데이터를 생성하거나 변경할 때 사용한다. Form 입력값은 주로 요청
Body에 담긴다.

```text
POST /todos
POST /todos/1/edit
POST /todos/1/complete
POST /todos/1/delete
```

삭제처럼 중요한 상태 변경을 GET 링크로 구현하면 링크 미리 읽기나 새로고침만으로
데이터가 바뀔 수 있다. 조회와 변경을 Method로 구분하면 요청의 의도가 분명해지고
브라우저 동작도 예측하기 쉬워진다.

## **5. HTTP 상태 코드**

상태 코드는 서버가 요청을 어떻게 처리했는지 세 자리 숫자로 나타낸다. 첫 번째
숫자는 응답의 큰 분류를 의미한다.

| 범위 | 분류 | 의미 |
| --- | --- | --- |
| 2xx | 성공 | 요청을 정상적으로 처리함 |
| 3xx | 리다이렉션 | 다른 위치나 방식으로 후속 요청이 필요함 |
| 4xx | 클라이언트 오류 | 요청 형식이나 대상에 문제가 있음 |
| 5xx | 서버 오류 | 서버가 요청 처리 중 실패함 |

### **5.1 200 OK**

요청이 성공했고 응답 본문을 반환한다는 뜻이다. 홈, 목록, 상세, 생성 Form, 수정
Form을 정상적으로 조회하면 HTML과 함께 `200 OK`가 반환된다.

### **5.2 303 See Other**

현재 요청의 처리가 끝났으며 `Location` Header의 주소를 GET으로 조회하라는
뜻이다. 이 프로젝트는 생성, 수정, 완료, 삭제 후 303을 사용해 PRG 패턴을
구현한다.

### **5.3 404 Not Found**

요청한 자원을 찾을 수 없다는 뜻이다. 존재하지 않는 `todo_id`로 상세 또는 수정
화면을 요청하면 서버는 `404 Not Found`를 반환한다.

### **5.4 함께 알아둘 상태 코드**

- `201 Created`: 새로운 자원을 생성했음을 나타낸다.
- `400 Bad Request`: 서버가 요청을 올바른 형식으로 해석하기 어렵다.
- `401 Unauthorized`: 인증 정보가 필요하다.
- `403 Forbidden`: 인증됐지만 해당 작업을 수행할 권한이 없다.
- `422 Unprocessable Content`: 요청 형식은 읽었지만 입력값 검증에 실패했다.
- `500 Internal Server Error`: 처리하지 못한 서버 내부 오류가 발생했다.

상태 코드만으로 모든 원인을 알 수 있는 것은 아니다. Header와 Body, 서버 로그를
함께 확인해야 구체적인 원인을 판단할 수 있다.

## **프로젝트에서 확인하기**

라우팅과 상태 코드는 다음 파일에서 확인할 수 있다.

- `app/routers/todos.py`: Method, Path, 응답 형식, 303과 404 처리
- `app/templates/`: 200 응답에 포함되는 HTML 템플릿
- `tests/test_todo_ui.py`: 실제 요청과 응답 상태 검증

## **핵심 정리**

브라우저와 FastAPI 서버는 HTTP 요청과 응답을 통해 통신한다. URL과 HTTP Method는
서버에서 수행할 작업을 결정하며, 서버는 처리 결과를 HTTP 상태 코드와 응답
본문으로 반환한다. 이 프로젝트는 조회에 GET, 상태 변경에 POST를 사용하고,
변경이 끝나면 303으로 GET 화면에 이동한다.
