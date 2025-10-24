# Pocket MCP Server Store - API 명세서

## 📋 기본 정보
- **Base URL**: `http://localhost:8000`
- **Content-Type**: `application/json`
- **Swagger UI**: `http://localhost:8000/docs`
- **ReDoc**: `http://localhost:8000/redoc`

---

## 🧩 MCP 서버 관리 API

### 1. MCP 서버 등록
```http
POST /api/mcp_servers
```

**Request Body:**
```json
{
  "title": "OpenAI MCP Server",
  "description": "OpenAI 기반 MCP 서버 등록 예시",
  "status": "ACTIVE",
  "tags": ["AI", "chat"],
  "io_type": "IN",
  "visibility_scope": "ALL",
  "company_code": 1001,
  "user_id": 1,
  "device": "PC"
}
```

**Response (201):**
```json
{
  "message": "MCP 서버가 성공적으로 등록되었습니다.",
  "data": {
    "id": 1,
    "title": "OpenAI MCP Server",
    "description": "OpenAI 기반 MCP 서버 등록 예시",
    "status": "ACTIVE",
    "user_id": 1,
    "tags": ["AI", "chat"],
    "io_type": "IN",
    "usage_count": 0,
    "visibility_scope": "ALL",
    "created_at": "2025-10-23T10:00:00",
    "company_code": 1001
  }
}
```

### 2. MCP 서버 목록 조회
```http
GET /api/mcp_servers
```

**Response (200):**
```json
{
  "data": [
    {
      "id": 1,
      "title": "ChatGPT MCP",
      "description": "OpenAI ChatGPT MCP 연결용 서버",
      "status": "ACTIVE",
      "user_id": 3,
      "tags": ["AI", "chat"],
      "io_type": "IN",
      "usage_count": 5,
      "visibility_scope": "ALL",
      "created_at": "2025-10-22T10:00:00",
      "company_code": 1001
    }
  ]
}
```

### 3. MCP 서버 단건 조회
```http
GET /api/mcp_servers/{id}
```

**Response (200):**
```json
{
  "data": {
    "id": 1,
    "title": "OpenAI MCP Server",
    "description": "OpenAI 기반 MCP 서버",
    "status": "ACTIVE",
    "user_id": 1,
    "tags": ["AI", "chat"],
    "io_type": "IN",
    "usage_count": 10,
    "visibility_scope": "ALL",
    "created_at": "2025-10-23T10:00:00",
    "company_code": 1001
  }
}
```

### 4. MCP 서버 수정
```http
PUT /api/mcp_servers/{id}
```

**Request Body:**
```json
{
  "title": "OpenAI MCP Server (수정됨)",
  "description": "설명 업데이트",
  "status": "ACTIVE",
  "tags": ["AI", "server"],
  "io_type": "IN",
  "visibility_scope": "AUTHORIZED",
  "company_code": 1001,
  "user_id": 1,
  "device": "PC"
}
```

**Response (200):**
```json
{
  "message": "MCP 서버가 수정되었습니다."
}
```

### 5. MCP 서버 삭제
```http
DELETE /api/mcp_servers/{id}
```

**Response (200):**
```json
{
  "message": "MCP 서버가 삭제되었습니다."
}
```

---

## 💙 좋아요 관리 API

### 1. MCP 서버 좋아요 등록
```http
POST /api/mcp_servers/{id}/like?user_id={user_id}
```

**Parameters:**
- `id`: MCP 서버 ID
- `user_id`: 사용자 ID

**Response (201):**
```json
{
  "message": "좋아요가 등록되었습니다."
}
```

**Error (409):**
```json
{
  "detail": "이미 좋아요를 누른 MCP 서버입니다."
}
```

### 2. MCP 서버 좋아요 취소
```http
DELETE /api/mcp_servers/{id}/like?user_id={user_id}
```

**Response (200):**
```json
{
  "message": "좋아요가 취소되었습니다."
}
```

### 3. 좋아요 목록 조회
```http
GET /api/likes
```

**Response (200):**
```json
{
  "data": [
    {
      "id": 1,
      "target_id": 1,
      "target_type": "MCP_SERVER",
      "user_id": 3
    }
  ]
}
```

---

## 📊 활동 로그 관리 API

### 1. 활동 로그 목록 조회
```http
GET /api/activity_logs
```

**Response (200):**
```json
{
  "data": [
    {
      "id": 1,
      "user_id": 1,
      "activity_type": "CREATE",
      "target_id": 1,
      "target_type": "MCP_SERVER",
      "ip_address": "127.0.0.1",
      "device": "PC",
      "created_at": "2025-10-23T10:00:00",
      "company_code": 1001
    }
  ]
}
```

### 2. 활동 로그 단건 조회
```http
GET /api/activity_logs/{id}
```

**Response (200):**
```json
{
  "message": "활동 로그 조회에 성공했습니다.",
  "data": {
    "id": 1,
    "user_id": 1,
    "activity_type": "CREATE",
    "target_id": 1,
    "target_type": "MCP_SERVER",
    "ip_address": "127.0.0.1",
    "device": "PC",
    "created_at": "2025-10-23T10:00:00",
    "company_code": 1001
  }
}
```

---

## 🔧 ENUM 값 정의

### Status (상태)
- `ACTIVE`: 활성
- `INACTIVE`: 비활성
- `DELETED`: 삭제됨
- `REVIEW`: 검토중
- `REJECTED`: 거부됨
- `ACCEPT`: 승인됨

### IO Type (입출력 타입)
- `IN`: 입력
- `OUT`: 출력

### Device (기기)
- `PC`: PC
- `MOBILE`: 모바일

### Visibility Scope (공개 범위)
- `ALL`: 전체 공개
- `AUTHORIZED`: 인증된 사용자만
- `PRIVATE`: 비공개

### Activity Type (활동 타입)
- `LOGIN`: 로그인
- `CREATE`: 생성
- `READ`: 조회
- `UPDATE`: 수정
- `DELETE`: 삭제

### Target Type (대상 타입)
- `USER`: 사용자
- `MCP_SERVER`: MCP 서버
- `AGENT`: 에이전트

---

## ⚠️ 에러 응답 형식

**404 Not Found:**
```json
{
  "detail": "MCP 서버를 찾을 수 없습니다."
}
```

**409 Conflict:**
```json
{
  "detail": "이미 좋아요를 누른 MCP 서버입니다."
}
```

**422 Validation Error:**
```json
{
  "detail": [
    {
      "loc": ["body", "user_id"],
      "msg": "field required",
      "type": "value_error.missing"
    }
  ]
}
```

---

## 📝 사용 예시

### JavaScript/Fetch 예시

```javascript
// MCP 서버 등록
const createMCPServer = async (data) => {
  const response = await fetch('http://localhost:8000/api/mcp_servers', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify(data)
  });
  return response.json();
};

// MCP 서버 목록 조회
const getMCPServers = async () => {
  const response = await fetch('http://localhost:8000/api/mcp_servers');
  return response.json();
};

// 좋아요 등록
const likeMCPServer = async (mcpId, userId) => {
  const response = await fetch(`http://localhost:8000/api/mcp_servers/${mcpId}/like?user_id=${userId}`, {
    method: 'POST'
  });
  return response.json();
};
```

### Axios 예시

```javascript
import axios from 'axios';

const api = axios.create({
  baseURL: 'http://localhost:8000/api'
});

// MCP 서버 등록
const createMCPServer = (data) => api.post('/mcp_servers', data);

// MCP 서버 목록 조회
const getMCPServers = () => api.get('/mcp_servers');

// 좋아요 등록
const likeMCPServer = (mcpId, userId) => 
  api.post(`/mcp_servers/${mcpId}/like`, null, { 
    params: { user_id: userId } 
  });
```