from fastmcp import FastMCP
import re
from datetime import datetime
from typing import List, Dict, Any, Optional
from enum import Enum

# FastMCP 서버 인스턴스 생성
mcp = FastMCP("Log Parser Server")

class LogLevel(Enum):
    DEBUG = "DEBUG"
    INFO = "INFO"
    WARNING = "WARNING"
    ERROR = "ERROR"
    CRITICAL = "CRITICAL"
    FATAL = "FATAL"

@mcp.tool()
def parse_log(log_content: str, log_format: str = "auto") -> Dict[str, Any]:
    """
    로그를 파싱하고 구조화합니다.

    Args:
        log_content: 파싱할 로그 내용
        log_format: 로그 형식 ("auto", "apache", "nginx", "json", "syslog")

    Returns:
        파싱된 로그 구조화 데이터
    """
    lines = log_content.strip().split('\n')
    parsed_logs = []

    for line_num, line in enumerate(lines, 1):
        if not line.strip():
            continue

        parsed_entry = {
            "line_number": line_num,
            "raw": line,
            "timestamp": None,
            "level": None,
            "message": None,
            "source": None,
            "pid": None
        }

        if log_format == "auto":
            # 자동 감지
            parsed_entry = _auto_parse_log_line(line, line_num)
        elif log_format == "apache":
            parsed_entry = _parse_apache_log(line, line_num)
        elif log_format == "nginx":
            parsed_entry = _parse_nginx_log(line, line_num)
        elif log_format == "json":
            parsed_entry = _parse_json_log(line, line_num)
        elif log_format == "syslog":
            parsed_entry = _parse_syslog_log(line, line_num)

        parsed_logs.append(parsed_entry)

    # 통계 정보 생성
    stats = _generate_log_stats(parsed_logs)

    return {
        "total_lines": len(parsed_logs),
        "parsed_logs": parsed_logs,
        "statistics": stats,
        "format_detected": log_format
    }

@mcp.tool()
def filter_level(logs: List[Dict[str, Any]], level: str, include_higher: bool = True) -> List[Dict[str, Any]]:
    """
    로그 레벨별로 필터링합니다.

    Args:
        logs: 파싱된 로그 리스트
        level: 필터링할 로그 레벨
        include_higher: 더 높은 레벨의 로그도 포함할지 여부

    Returns:
        필터링된 로그 리스트
    """
    level_priority = {
        "DEBUG": 0, "INFO": 1, "WARNING": 2,
        "ERROR": 3, "CRITICAL": 4, "FATAL": 5
    }

    target_priority = level_priority.get(level.upper(), 0)
    filtered_logs = []

    for log in logs:
        log_level = log.get("level", "").upper()
        log_priority = level_priority.get(log_level, 0)

        if include_higher:
            if log_priority >= target_priority:
                filtered_logs.append(log)
        else:
            if log_priority == target_priority:
                filtered_logs.append(log)

    return filtered_logs

@mcp.tool()
def extract_errors(logs: List[Dict[str, Any]], include_warnings: bool = False) -> Dict[str, Any]:
    """
    에러 로그만 추출합니다.

    Args:
        logs: 파싱된 로그 리스트
        include_warnings: 경고 로그도 포함할지 여부

    Returns:
        에러 로그와 분석 정보
    """
    error_levels = ["ERROR", "CRITICAL", "FATAL"]
    if include_warnings:
        error_levels.append("WARNING")

    error_logs = []
    error_patterns = {}

    for log in logs:
        log_level = log.get("level", "").upper()
        if log_level in error_levels:
            error_logs.append(log)

            # 에러 패턴 분석
            message = log.get("message", "")
            if message:
                # 간단한 에러 패턴 추출
                if "timeout" in message.lower():
                    error_patterns["timeout"] = error_patterns.get("timeout", 0) + 1
                elif "connection" in message.lower():
                    error_patterns["connection"] = error_patterns.get("connection", 0) + 1
                elif "permission" in message.lower():
                    error_patterns["permission"] = error_patterns.get("permission", 0) + 1
                elif "not found" in message.lower():
                    error_patterns["not_found"] = error_patterns.get("not_found", 0) + 1

    # 에러 통계
    error_stats = {
        "total_errors": len(error_logs),
        "error_by_level": {},
        "error_patterns": error_patterns,
        "most_common_error": max(error_patterns.items(), key=lambda x: x[1])[0] if error_patterns else None
    }

    for log in error_logs:
        level = log.get("level", "UNKNOWN")
        error_stats["error_by_level"][level] = error_stats["error_by_level"].get(level, 0) + 1

    return {
        "error_logs": error_logs,
        "statistics": error_stats,
        "summary": f"총 {len(error_logs)}개의 에러가 발견되었습니다."
    }

def _auto_parse_log_line(line: str, line_num: int) -> Dict[str, Any]:
    """자동으로 로그 라인을 파싱합니다."""
    parsed = {
        "line_number": line_num,
        "raw": line,
        "timestamp": None,
        "level": None,
        "message": None,
        "source": None,
        "pid": None
    }

    # 타임스탬프 패턴들
    timestamp_patterns = [
        r'(\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2})',
        r'(\d{2}/\w{3}/\d{4}:\d{2}:\d{2}:\d{2})',
        r'(\w{3} \d{2} \d{2}:\d{2}:\d{2})',
        r'(\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2})'
    ]

    # 로그 레벨 패턴
    level_pattern = r'\b(DEBUG|INFO|WARNING|ERROR|CRITICAL|FATAL)\b'

    # 타임스탬프 추출
    for pattern in timestamp_patterns:
        match = re.search(pattern, line)
        if match:
            parsed["timestamp"] = match.group(1)
            break

    # 로그 레벨 추출
    level_match = re.search(level_pattern, line)
    if level_match:
        parsed["level"] = level_match.group(1)

    # 메시지 추출 (타임스탬프와 레벨을 제외한 부분)
    message = line
    if parsed["timestamp"]:
        message = message.replace(parsed["timestamp"], "", 1)
    if parsed["level"]:
        message = message.replace(parsed["level"], "", 1)

    parsed["message"] = message.strip()

    return parsed

def _parse_apache_log(line: str, line_num: int) -> Dict[str, Any]:
    """Apache 로그 형식을 파싱합니다."""
    # Apache Common Log Format 예시
    pattern = r'(\S+) (\S+) (\S+) \[([^\]]+)\] "([^"]*)" (\d+) (\S+)'
    match = re.match(pattern, line)

    if match:
        return {
            "line_number": line_num,
            "raw": line,
            "ip": match.group(1),
            "timestamp": match.group(4),
            "method": match.group(5).split()[0] if match.group(5) else None,
            "status": match.group(6),
            "size": match.group(7),
            "level": "INFO"  # Apache는 기본적으로 INFO 레벨
        }

    return {"line_number": line_num, "raw": line, "level": "UNKNOWN"}

def _parse_nginx_log(line: str, line_num: int) -> Dict[str, Any]:
    """Nginx 로그 형식을 파싱합니다."""
    # Nginx access log 예시
    pattern = r'(\S+) - (\S+) \[([^\]]+)\] "([^"]*)" (\d+) (\d+) "([^"]*)" "([^"]*)"'
    match = re.match(pattern, line)

    if match:
        return {
            "line_number": line_num,
            "raw": line,
            "ip": match.group(1),
            "user": match.group(2),
            "timestamp": match.group(3),
            "request": match.group(4),
            "status": match.group(5),
            "size": match.group(6),
            "referer": match.group(7),
            "user_agent": match.group(8),
            "level": "INFO"
        }

    return {"line_number": line_num, "raw": line, "level": "UNKNOWN"}

def _parse_json_log(line: str, line_num: int) -> Dict[str, Any]:
    """JSON 로그 형식을 파싱합니다."""
    import json
    try:
        data = json.loads(line)
        return {
            "line_number": line_num,
            "raw": line,
            "timestamp": data.get("timestamp"),
            "level": data.get("level"),
            "message": data.get("message"),
            "source": data.get("source"),
            "pid": data.get("pid"),
            "data": data
        }
    except:
        return {"line_number": line_num, "raw": line, "level": "UNKNOWN"}

def _parse_syslog_log(line: str, line_num: int) -> Dict[str, Any]:
    """Syslog 형식을 파싱합니다."""
    # Syslog RFC3164 형식
    pattern = r'<(\d+)>(\w{3} \d{2} \d{2}:\d{2}:\d{2}) (\S+) (.+)'
    match = re.match(pattern, line)

    if match:
        return {
            "line_number": line_num,
            "raw": line,
            "priority": match.group(1),
            "timestamp": match.group(2),
            "hostname": match.group(3),
            "message": match.group(4),
            "level": _priority_to_level(int(match.group(1)))
        }

    return {"line_number": line_num, "raw": line, "level": "UNKNOWN"}

def _priority_to_level(priority: int) -> str:
    """Syslog 우선순위를 로그 레벨로 변환합니다."""
    severity = priority & 0x07
    if severity <= 2:
        return "CRITICAL"
    elif severity == 3:
        return "ERROR"
    elif severity == 4:
        return "WARNING"
    elif severity == 5:
        return "INFO"
    else:
        return "DEBUG"

def _generate_log_stats(logs: List[Dict[str, Any]]) -> Dict[str, Any]:
    """로그 통계를 생성합니다."""
    stats = {
        "total_logs": len(logs),
        "by_level": {},
        "by_hour": {},
        "error_rate": 0
    }

    error_count = 0

    for log in logs:
        level = log.get("level", "UNKNOWN")
        stats["by_level"][level] = stats["by_level"].get(level, 0) + 1

        if level in ["ERROR", "CRITICAL", "FATAL"]:
            error_count += 1

        # 시간별 통계 (타임스탬프가 있는 경우)
        timestamp = log.get("timestamp")
        if timestamp:
            try:
                # 간단한 시간 추출 (HH:MM 형식)
                time_match = re.search(r'(\d{2}):(\d{2})', timestamp)
                if time_match:
                    hour = time_match.group(1)
                    stats["by_hour"][hour] = stats["by_hour"].get(hour, 0) + 1
            except:
                pass

    stats["error_rate"] = (error_count / len(logs)) * 100 if logs else 0

    return stats

@mcp.resource("log://formats")
def get_log_formats() -> str:
    """로그 형식 예제 리소스를 제공합니다."""
    return """
    Log Parser Server 지원 형식:

    1. Apache Common Log Format:
       192.168.1.1 - - [25/Dec/2023:10:30:45 +0000] "GET /index.html HTTP/1.1" 200 1234

    2. JSON Log Format:
       {"timestamp": "2023-12-25T10:30:45Z", "level": "INFO", "message": "User login"}

    3. Syslog Format:
       <34>Dec 25 10:30:45 server app: User authentication failed

    4. 일반 텍스트:
       2023-12-25 10:30:45 [INFO] Application started successfully
    """

@mcp.prompt()
def log_analysis_helper(log_data: str) -> str:
    """
    로그 분석을 위한 프롬프트를 생성합니다.

    Args:
        log_data: 분석할 로그 데이터
    """
    return f"""
    다음 로그 데이터를 분석해주세요:

    로그 데이터:
    {log_data}

    분석 항목:
    1. 로그 형식 자동 감지
    2. 에러 및 경고 로그 식별
    3. 시간대별 로그 분포
    4. 가장 빈번한 에러 패턴
    5. 성능 이슈 지표

    사용 가능한 도구:
    - parse_log: 로그 파싱 및 구조화
    - filter_level: 로그 레벨별 필터링
    - extract_errors: 에러 로그 추출 및 분석
    """

if __name__ == "__main__":
    # stdio 모드로 서버 실행
    mcp.run(transport="stdio")
