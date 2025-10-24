# Pocket MCP Server Store API

FastAPI 기반 MCP Server Store 백엔드 서비스입니다. MCP 서버, 활동 로그, 좋아요 리소스에 대한 CRUD API를 제공합니다.

## 요구 사항

- Python 3.11+
- PostgreSQL 13+
- [FastAPI](https://fastapi.tiangolo.com/)

## 로컬 개발 환경 (.venv)

1. 가상환경 생성 및 활성화
   ```bash
   python3 -m venv .venv
   source .venv/bin/activate
   ```
2. 의존성 설치
   ```bash
   pip install --upgrade pip
   pip install -e .
   ```
3. 환경 변수 설정
   - `.env` 파일을 참고하여 `DATABASE_URL` 등을 원하는 값으로 조정합니다.
4. 데이터베이스 준비
   ```bash
   createdb pocket
   ```
5. 애플리케이션 실행
   ```bash
   uvicorn pocket.app.main:app --reload
   ```
6. 문서 확인
   - Swagger UI: http://localhost:8000/docs
   - ReDoc: http://localhost:8000/redoc

## Docker 기반 운영 환경

1. 컨테이너 빌드 및 실행
   ```bash
   docker-compose up --build
   ```
2. 기본 서비스
   - API: http://localhost:8000
   - PostgreSQL: localhost:5432 (user/password: `pocket`)

## 프로젝트 구조

```
pocket/
├── app/
│   ├── api/
│   │   └── v1/
│   │       └── endpoints/
│   ├── core/
│   ├── models/
│   └── schemas/
├── Dockerfile
├── docker-compose.yml
├── main.py
├── pyproject.toml
└── README.md
```

## OpenAPI 문서

FastAPI가 기본 제공하는 Swagger UI에서 전체 API 명세를 확인하고 테스트할 수 있습니다. `/docs` 경로를 사용하면 JSON 스키마, 요청/응답 예제, 쿼리 파라미터 설명 등이 자동으로 노출됩니다.

## 데이터베이스 초기화

`RUN_MIGRATIONS_ON_STARTUP=true` 환경 변수 설정 시 애플리케이션 시작 시점에 SQLAlchemy `create_all`이 실행되어 필요한 테이블이 생성됩니다. 운영 환경에서는 별도의 마이그레이션 도구(Alembic 등)를 활용하는 것을 권장합니다.
