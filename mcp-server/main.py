import asyncio
import json
import subprocess
import threading
import os
import shutil
from typing import Dict, List, Any, Optional
from fastapi import FastAPI, HTTPException, Query, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import logging
from pathlib import Path

# 로깅 설정
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# 요청/응답 모델
class ToolCallRequest(BaseModel):
    name: str
    arguments: Dict[str, Any]

class ToolsListResponse(BaseModel):
    tools: List[Dict[str, Any]]

# MCP 클라이언트 클래스 (동적 서버 관리)
class MCPClient:
    def __init__(self, server_file: str):
        self.server_file = server_file
        self.process = None
        self.lock = threading.Lock()
        self.request_id = 0

    def _get_next_id(self) -> int:
        """다음 요청 ID 생성"""
        self.request_id += 1
        return self.request_id

    async def start_mcp_server(self):
        """MCP 서버 프로세스 시작"""
        try:
            # 파일 존재 확인
            if not os.path.exists(self.server_file):
                raise FileNotFoundError(f"MCP 서버 파일을 찾을 수 없습니다: {self.server_file}")

            # 환경 변수에 UTF-8 인코딩 설정
            env = os.environ.copy()
            env['PYTHONIOENCODING'] = 'utf-8'

            self.process = subprocess.Popen(
                ["python", "-u", self.server_file],
                stdin=subprocess.PIPE,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                encoding='utf-8',
                errors='replace',
                bufsize=1,
                universal_newlines=True,
                env=env
            )

            logger.info(f"MCP 서버 시작: {self.server_file}")

            # 초기화 요청
            init_request = {
                "jsonrpc": "2.0",
                "id": self._get_next_id(),
                "method": "initialize",
                "params": {
                    "protocolVersion": "2024-11-05",
                    "capabilities": {
                        "roots": {
                            "listChanged": True
                        },
                        "sampling": {}
                    },
                    "clientInfo": {
                        "name": "fastapi-client",
                        "version": "1.0.0"
                    }
                }
            }

            init_response = await self._send_request(init_request)
            logger.info(f"초기화 완료: {self.server_file}")

            # initialized 알림 전송
            initialized_notification = {
                "jsonrpc": "2.0",
                "method": "notifications/initialized"
            }

            with self.lock:
                notification_json = json.dumps(initialized_notification, ensure_ascii=False) + "\n"
                self.process.stdin.write(notification_json)
                self.process.stdin.flush()

            logger.info(f"MCP 서버 초기화 완료: {self.server_file}")

        except Exception as e:
            logger.error(f"MCP 서버 시작 실패 ({self.server_file}): {e}", exc_info=True)
            if self.process:
                self.process.terminate()
                self.process = None
            raise

    async def _send_request(self, request: Dict[str, Any]) -> Dict[str, Any]:
        """MCP 서버에 요청 전송"""
        with self.lock:
            if not self.process:
                raise HTTPException(status_code=500, detail="MCP 서버가 실행되지 않았습니다")

            try:
                request_json = json.dumps(request, ensure_ascii=False) + "\n"
                logger.debug(f"요청 전송: {request_json.strip()}")

                self.process.stdin.write(request_json)
                self.process.stdin.flush()

                response_line = self.process.stdout.readline()

                if not response_line:
                    error_line = self.process.stderr.readline()
                    if error_line:
                        logger.error(f"MCP 서버 에러: {error_line}")
                    raise HTTPException(status_code=500, detail="MCP 서버 응답 없음")

                logger.debug(f"응답 수신: {response_line.strip()}")

                try:
                    response = json.loads(response_line.strip())
                except json.JSONDecodeError as je:
                    logger.error(f"JSON 파싱 실패. 원본: {repr(response_line)}")
                    raise je

                if "error" in response:
                    error_msg = response['error'].get('message', 'Unknown error')
                    error_code = response['error'].get('code', -1)
                    logger.error(f"MCP 서버 에러 (코드: {error_code}): {error_msg}")
                    raise HTTPException(
                        status_code=500,
                        detail=f"MCP 서버 오류: {error_msg}"
                    )

                return response

            except json.JSONDecodeError as e:
                logger.error(f"JSON 파싱 오류: {e}")
                raise HTTPException(status_code=500, detail=f"JSON 파싱 오류: {str(e)}")
            except HTTPException:
                raise
            except Exception as e:
                logger.error(f"MCP 통신 오류: {e}", exc_info=True)
                raise HTTPException(status_code=500, detail=f"MCP 통신 오류: {str(e)}")

    async def get_tools_list(self) -> List[Dict[str, Any]]:
        """도구 목록 조회"""
        request = {
            "jsonrpc": "2.0",
            "id": self._get_next_id(),
            "method": "tools/list",
            "params": {}
        }

        response = await self._send_request(request)
        return response.get("result", {}).get("tools", [])

    async def call_tool(self, name: str, arguments: Dict[str, Any]) -> str:
        """도구 실행"""
        request = {
            "jsonrpc": "2.0",
            "id": self._get_next_id(),
            "method": "tools/call",
            "params": {
                "name": name,
                "arguments": arguments
            }
        }

        response = await self._send_request(request)
        content = response.get("result", {}).get("content", [])

        result_text = ""
        for item in content:
            if item.get("type") == "text":
                result_text += item.get("text", "")

        return result_text

    def stop_mcp_server(self):
        """MCP 서버 프로세스 종료"""
        if self.process:
            try:
                self.process.terminate()
                self.process.wait(timeout=5)
            except subprocess.TimeoutExpired:
                self.process.kill()
            except Exception as e:
                logger.error(f"MCP 서버 종료 중 오류: {e}")
            finally:
                self.process = None
                logger.info(f"MCP 서버 종료: {self.server_file}")

# FastAPI 앱 생성
app = FastAPI(
    title="Dynamic MCP FastAPI Server",
    description="여러 MCP 서버를 동적으로 실행하고 관리하는 FastAPI 서버",
    version="2.0.0"
)

# CORS 설정
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# MCP 서버 파일들이 있는 디렉토리 (설정 가능)
MCP_SERVERS_DIR = os.environ.get("MCP_SERVERS_DIR", "./mcp_servers")

def validate_server_file(filename: str) -> str:
    """서버 파일명 검증 및 전체 경로 반환"""
    # 보안: 상위 디렉토리 접근 방지
    if ".." in filename or "/" in filename or "\\" in filename:
        raise HTTPException(status_code=400, detail="잘못된 파일명입니다")

    # .py 확장자 확인
    if not filename.endswith(".py"):
        filename += ".py"

    # 전체 경로 생성
    full_path = os.path.join(MCP_SERVERS_DIR, filename)

    # 파일 존재 확인
    if not os.path.exists(full_path):
        raise HTTPException(status_code=404, detail=f"MCP 서버 파일을 찾을 수 없습니다: {filename}")

    return full_path

@app.get("/")
async def root():
    """루트 엔드포인트"""
    return {
        "message": "Dynamic MCP FastAPI Server",
        "version": "2.0.0",
        "description": "여러 MCP 서버를 동적으로 실행",
        "endpoints": {
            "tools": "GET /{server_file}/tools",
            "call_tool": "POST /{server_file}/tools/call",
            "servers": "GET /servers",
            "upload": "POST /upload",
            "delete": "DELETE /servers/{server_file}",
            "health": "GET /health"
        },
        "usage": {
            "example": "GET /test_mcp_code.py/tools"
        }
    }

@app.get("/servers")
async def list_servers():
    """사용 가능한 MCP 서버 목록 조회"""
    try:
        if not os.path.exists(MCP_SERVERS_DIR):
            return {"servers": [], "message": f"MCP 서버 디렉토리가 없습니다: {MCP_SERVERS_DIR}"}

        servers = [
            f for f in os.listdir(MCP_SERVERS_DIR)
            if f.endswith(".py") and os.path.isfile(os.path.join(MCP_SERVERS_DIR, f))
        ]

        return {
            "servers": servers,
            "count": len(servers),
            "directory": MCP_SERVERS_DIR
        }
    except Exception as e:
        logger.error(f"서버 목록 조회 실패: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/{server_file}/tools", response_model=ToolsListResponse)
async def get_tools(server_file: str):
    """특정 MCP 서버의 도구 목록 조회"""
    full_path = validate_server_file(server_file)
    client = None

    try:
        # 서버 시작
        client = MCPClient(full_path)
        await client.start_mcp_server()

        # 도구 목록 조회
        tools = await client.get_tools_list()

        return ToolsListResponse(tools=tools)

    except Exception as e:
        logger.error(f"도구 목록 조회 실패 ({server_file}): {e}")
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        # 서버 종료
        if client:
            client.stop_mcp_server()

@app.post("/{server_file}/tools/call")
async def call_tool(server_file: str, request: ToolCallRequest):
    """특정 MCP 서버의 도구 실행"""
    full_path = validate_server_file(server_file)
    client = None

    try:
        # 서버 시작
        client = MCPClient(full_path)
        await client.start_mcp_server()

        # 도구 실행
        result = await client.call_tool(request.name, request.arguments)

        return {
            "success": True,
            "result": result,
            "server_file": server_file,
            "tool_name": request.name,
            "arguments": request.arguments
        }

    except Exception as e:
        logger.error(f"도구 실행 실패 ({server_file}/{request.name}): {e}")
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        # 서버 종료
        if client:
            client.stop_mcp_server()

@app.get("/{server_file}/tools/{tool_name}")
async def get_tool_info(server_file: str, tool_name: str):
    """특정 MCP 서버의 특정 도구 정보 조회"""
    full_path = validate_server_file(server_file)
    client = None

    try:
        # 서버 시작
        client = MCPClient(full_path)
        await client.start_mcp_server()

        # 도구 목록에서 검색
        tools = await client.get_tools_list()
        for tool in tools:
            if tool.get("name") == tool_name:
                return tool

        raise HTTPException(
            status_code=404,
            detail=f"도구 '{tool_name}'을 서버 '{server_file}'에서 찾을 수 없습니다"
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"도구 정보 조회 실패 ({server_file}/{tool_name}): {e}")
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        # 서버 종료
        if client:
            client.stop_mcp_server()

@app.get("/health")
async def health_check():
    """헬스 체크"""
    return {
        "status": "healthy",
        "mcp_servers_dir": MCP_SERVERS_DIR,
        "mcp_servers_dir_exists": os.path.exists(MCP_SERVERS_DIR)
    }

@app.post("/upload")
async def upload_mcp_server(file: UploadFile = File(...)):
    """
    MCP 서버 파일 업로드
    """
    try:
        # 파일명 검증
        if not file.filename.endswith(".py"):
            raise HTTPException(
                status_code=400,
                detail="Python 파일(.py)만 업로드 가능합니다"
            )

        # 보안: 파일명 검증 (경로 조작 방지)
        safe_filename = os.path.basename(file.filename)
        if ".." in safe_filename or "/" in safe_filename or "\\" in safe_filename:
            raise HTTPException(status_code=400, detail="잘못된 파일명입니다")

        # 저장 경로
        file_path = os.path.join(MCP_SERVERS_DIR, safe_filename)

        # 디렉토리 생성 (없을 경우)
        os.makedirs(MCP_SERVERS_DIR, exist_ok=True)

        # 파일 저장
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)

        # 파일 정보 반환
        file_size = os.path.getsize(file_path)

        logger.info(f"파일 업로드 완료: {safe_filename} ({file_size} bytes)")

        return {
            "success": True,
            "filename": safe_filename,
            "size": file_size,
            "path": file_path,
            "message": "파일이 성공적으로 업로드되었습니다"
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"파일 업로드 실패: {e}")
        raise HTTPException(status_code=500, detail=f"파일 업로드 실패: {str(e)}")

@app.delete("/servers/{server_file}")
async def delete_mcp_server(server_file: str):
    """
    MCP 서버 파일 삭제
    """
    try:
        full_path = validate_server_file(server_file)

        os.remove(full_path)
        logger.info(f"파일 삭제 완료: {server_file}")

        return {
            "success": True,
            "filename": server_file,
            "message": "파일이 삭제되었습니다"
        }

    except Exception as e:
        logger.error(f"파일 삭제 실패: {e}")
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    import sys

    # UTF-8 인코딩 강제 설정
    if sys.platform == 'win32':
        import codecs
        sys.stdout = codecs.getwriter('utf-8')(sys.stdout.buffer, 'strict')
        sys.stderr = codecs.getwriter('utf-8')(sys.stderr.buffer, 'strict')

    # MCP 서버 디렉토리 생성
    os.makedirs(MCP_SERVERS_DIR, exist_ok=True)
    logger.info(f"MCP 서버 디렉토리: {os.path.abspath(MCP_SERVERS_DIR)}")

    uvicorn.run(app, host="0.0.0.0", port=8001)r