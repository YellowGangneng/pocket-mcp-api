# Dynamic MCP FastAPI Server

여러 MCP(Model Context Protocol) 서버를 동적으로 실행하고 관리하는 FastAPI 서버입니다. FastMCP를 사용하여 간단하게 MCP 서버를 구현하고, FastAPI를 통해 REST API로 제공할 수 있습니다.

## 프로젝트 구조

```
mcp-server/
├── main.py                    # FastAPI 서버 (동적 MCP 서버 관리)
├── requirements.txt           # 필요한 패키지
├── mcp_servers/              # MCP 서버 파일들이 저장되는 디렉토리
│   └── test_mcp_code.py      # FastMCP로 구현된 예제 MCP 서버
└── README.md                 # 사용 가이드
```

## 주요 기능

### 🚀 동적 MCP 서버 관리
- **여러 MCP 서버 파일을 동적으로 실행**하고 관리
- 각 요청마다 독립적인 MCP 서버 프로세스 생성
- 서버 파일명을 URL 경로로 사용하여 특정 서버에 접근

### 🔧 FastMCP 기반 서버 구현
- **FastMCP**를 사용하여 간단하고 직관적인 MCP 서버 구현
- 데코레이터 기반의 도구, 리소스, 프롬프트 정의
- 자동 타입 검증 및 문서화

### 🌐 REST API 제공
- **CORS 설정** 포함 (웹 클라이언트에서 호출 가능)
- **동시 실행 문제 해결** (threading.Lock 사용)
- Swagger UI를 통한 API 문서 자동 생성

## 설치 및 실행

### 1. 의존성 설치
```bash
pip install -r requirements.txt
```

### 2. FastAPI 서버 실행
```bash
python main.py
```

서버가 `http://localhost:8000`에서 실행됩니다.

### 3. API 문서 확인
- **Swagger UI**: `http://localhost:8000/docs`
- **ReDoc**: `http://localhost:8000/redoc`

## API 엔드포인트

### 기본 정보
- `GET /`: 서버 정보 및 사용법
- `GET /servers`: 사용 가능한 MCP 서버 목록
- `GET /health`: 헬스 체크

### 파일 관리 엔드포인트
- `POST /upload`: MCP 서버 파일 업로드
- `DELETE /servers/{server_file}`: MCP 서버 파일 삭제

### MCP 서버별 엔드포인트
- `GET /{server_file}/tools`: 특정 서버의 도구 목록 조회
- `POST /{server_file}/tools/call`: 특정 서버의 도구 실행
- `GET /{server_file}/tools/{tool_name}`: 특정 도구 정보 조회

## 사용 예제

### 1. 사용 가능한 서버 목록 조회
```bash
curl -X GET "http://localhost:8000/servers"
```

### 2. 특정 서버의 도구 목록 조회
```bash
curl -X GET "http://localhost:8000/test_mcp_code.py/tools"
```

### 3. 파일 관리 예제

#### MCP 서버 파일 업로드
```bash
# curl을 사용한 파일 업로드
curl -X POST "http://localhost:8000/upload" \
  -F "file=@my_server.py"

# PowerShell에서 업로드
curl -X POST "http://localhost:8000/upload" -F "file=@C:\path\to\my_server.py"
```

#### 업로드된 파일 삭제
```bash
curl -X DELETE "http://localhost:8000/servers/my_server.py"
```

### 4. 도구 실행 예제

#### 인사 도구 사용
```bash
curl -X POST "http://localhost:8000/test_mcp_code.py/tools/call" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "greet",
    "arguments": {
      "name": "홍길동"
    }
  }'
```

#### 덧셈 도구 사용
```bash
curl -X POST "http://localhost:8000/test_mcp_code.py/tools/call" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "add",
    "arguments": {
      "a": 10,
      "b": 20
    }
  }'
```

#### 곱셈 도구 사용
```bash
curl -X POST "http://localhost:8000/test_mcp_code.py/tools/call" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "multiply",
    "arguments": {
      "a": 5,
      "b": 6
    }
  }'
```

## FastMCP 서버 구현

### 예제 서버 (`mcp_servers/test_mcp_code.py`)

```python
from fastmcp import FastMCP

# FastMCP 서버 인스턴스 생성
mcp = FastMCP("Simple Calculator Server")

@mcp.tool()
def greet(name: str) -> str:
    """사용자에게 인사를 합니다."""
    return f"안녕하세요, {name}님!"

@mcp.tool()
def add(a: float, b: float) -> float:
    """두 숫자를 더합니다."""
    return a + b

@mcp.tool()
def multiply(a: float, b: float) -> float:
    """두 숫자를 곱합니다."""
    return a * b

@mcp.resource("greeting://welcome")
def get_welcome_message() -> str:
    """환영 메시지 리소스를 제공합니다."""
    return "Simple Calculator Server에 오신 것을 환영합니다!"

@mcp.prompt()
def math_problem_solver(problem: str) -> str:
    """수학 문제 해결을 위한 프롬프트를 생성합니다."""
    return f"다음 수학 문제를 해결해주세요: {problem}"

if __name__ == "__main__":
    mcp.run(transport="stdio")
```

### 새로운 MCP 서버 추가

#### 방법 1: 파일 업로드 사용
1. FastMCP로 서버 구현
2. API를 통해 파일 업로드: `POST /upload`
3. 자동으로 `mcp_servers/` 디렉토리에 저장

#### 방법 2: 직접 파일 생성
1. `mcp_servers/` 디렉토리에 새로운 Python 파일 생성
2. FastMCP를 사용하여 서버 구현
3. `@mcp.tool()`, `@mcp.resource()`, `@mcp.prompt()` 데코레이터 사용
4. `mcp.run(transport="stdio")`로 서버 실행

## 동시 실행 처리

FastAPI 서버는 `threading.Lock`을 사용하여 MCP 서버와의 통신에서 동시 실행 문제를 해결합니다:

- **여러 클라이언트가 동시에 API를 호출해도 안전하게 처리**
- **MCP 서버와의 통신이 순차적으로 이루어짐**
- **각 요청은 독립적인 프로세스로 처리**

## 환경 설정

### MCP 서버 디렉토리 설정
```bash
# 환경 변수로 MCP 서버 디렉토리 변경 가능
export MCP_SERVERS_DIR="/path/to/your/mcp/servers"
python main.py
```

### UTF-8 인코딩 지원
- Windows 환경에서 UTF-8 인코딩 자동 설정
- 한글 및 다국어 문자 지원

## 파일 관리 기능

### 📤 파일 업로드
- **Python 파일만 업로드 가능** (`.py` 확장자 필수)
- **보안 검증**: 경로 조작 방지 (`..`, `/`, `\` 문자 차단)
- **자동 디렉토리 생성**: `mcp_servers/` 디렉토리가 없으면 자동 생성
- **파일 정보 반환**: 파일명, 크기, 저장 경로 등

### 🗑️ 파일 삭제
- **기존 보안 검증 활용**으로 안전한 파일 삭제
- **삭제 결과 반환** 및 로깅

### 🔧 업로드 방법

#### Insomnia 사용
1. **Method**: `POST`
2. **URL**: `http://localhost:8000/upload`
3. **Body**: Form Data
4. **Key**: `file`, **Type**: File, **Value**: Python 파일 선택

#### SSH/명령어 사용
```bash
# 기본 업로드
curl -X POST "http://localhost:8000/upload" -F "file=@my_server.py"

# Windows PowerShell
curl -X POST "http://localhost:8000/upload" -F "file=@C:\path\to\my_server.py"
```

## 보안 고려사항

### 파일 경로 보안
- **상위 디렉토리 접근 방지** (`..`, `/`, `\` 문자 차단)
- **Python 파일만 실행 허용** (`.py` 확장자 필수)
- **파일 존재 여부 검증**

### 업로드 보안
- **파일명 검증**: 경로 조작 방지
- **파일 타입 제한**: Python 파일만 허용
- **자동 디렉토리 생성**: 안전한 저장 경로

### CORS 설정
- 현재는 모든 도메인에서 접근 가능
- **프로덕션 환경에서는 특정 도메인으로 제한 권장**

## 개발 및 확장

### 새로운 도구 추가
1. FastMCP 서버에서 `@mcp.tool()` 데코레이터 사용
2. 함수에 타입 힌트와 독스트링 추가
3. 서버 재시작 없이 자동으로 API에 반영

### 리소스 및 프롬프트 추가
- `@mcp.resource()`: 정적 리소스 제공
- `@mcp.prompt()`: 동적 프롬프트 생성

### MCP 프로토콜 확장
- 현재 구현된 메서드: `initialize`, `tools/list`, `tools/call`
- FastMCP의 추가 기능 활용 가능

## 문제 해결

### MCP 서버 연결 실패
```bash
# Python 경로 확인
which python

# 파일 실행 권한 확인
ls -la mcp_servers/test_mcp_code.py

# 로그 확인
python main.py
```

### 파일 업로드 오류
```bash
# 파일 존재 확인
ls -la my_server.py

# 서버 상태 확인
curl -X GET "http://localhost:8000/health"

# 업로드 테스트
curl -X POST "http://localhost:8000/upload" -F "file=@my_server.py" -v
```

### 동시 실행 오류
- 로그에서 `threading.Lock` 관련 오류 확인
- MCP 서버 프로세스 상태 모니터링
- 메모리 사용량 확인

### UTF-8 인코딩 문제
- Windows 환경에서 자동으로 해결됨
- Linux/Mac에서는 `PYTHONIOENCODING=utf-8` 환경 변수 설정

## 성능 최적화

### 프로세스 관리
- **각 요청마다 새로운 프로세스 생성**으로 격리 보장
- **요청 완료 후 자동 프로세스 정리**
- **타임아웃 설정**으로 무한 대기 방지

### 메모리 관리
- **프로세스별 메모리 격리**
- **자동 가비지 컬렉션**
- **리소스 누수 방지**

## 라이선스

MIT License
