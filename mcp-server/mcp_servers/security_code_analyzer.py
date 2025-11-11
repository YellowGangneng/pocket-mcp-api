from fastmcp import FastMCP
import re
import ast
from typing import List, Dict, Any, Optional
from enum import Enum

# FastMCP 서버 인스턴스 생성
mcp = FastMCP("Security Code Analyzer Server")

class VulnerabilityType(Enum):
    SQL_INJECTION = "SQL Injection"
    XSS = "Cross-Site Scripting (XSS)"
    CSRF = "Cross-Site Request Forgery (CSRF)"
    PATH_TRAVERSAL = "Path Traversal"
    COMMAND_INJECTION = "Command Injection"
    INSECURE_DESERIALIZATION = "Insecure Deserialization"
    WEAK_CRYPTO = "Weak Cryptography"
    HARDCODED_SECRETS = "Hardcoded Secrets"
    INSECURE_REDIRECT = "Insecure Redirect"
    MISSING_AUTHENTICATION = "Missing Authentication"

@mcp.tool()
def scan_vulnerabilities(code: str, language: str = "python") -> Dict[str, Any]:
    """
    코드에서 보안 취약점을 스캔합니다.

    Args:
        code: 스캔할 코드
        language: 프로그래밍 언어 ("python", "javascript", "java", "php")

    Returns:
        발견된 취약점 목록과 상세 정보
    """
    vulnerabilities = []

    if language.lower() == "python":
        vulnerabilities = _scan_python_vulnerabilities(code)
    elif language.lower() == "javascript":
        vulnerabilities = _scan_javascript_vulnerabilities(code)
    elif language.lower() == "java":
        vulnerabilities = _scan_java_vulnerabilities(code)
    elif language.lower() == "php":
        vulnerabilities = _scan_php_vulnerabilities(code)
    else:
        return {"error": f"지원하지 않는 언어: {language}"}

    # 심각도별 분류
    severity_counts = {"HIGH": 0, "MEDIUM": 0, "LOW": 0}
    for vuln in vulnerabilities:
        severity_counts[vuln["severity"]] += 1

    return {
        "total_vulnerabilities": len(vulnerabilities),
        "vulnerabilities": vulnerabilities,
        "severity_summary": severity_counts,
        "risk_score": _calculate_risk_score(vulnerabilities),
        "language": language
    }

@mcp.tool()
def check_best_practices(code: str, language: str = "python") -> Dict[str, Any]:
    """
    보안 베스트 프랙티스를 검증합니다.

    Args:
        code: 검증할 코드
        language: 프로그래밍 언어

    Returns:
        베스트 프랙티스 검증 결과
    """
    best_practices = []
    violations = []

    if language.lower() == "python":
        best_practices, violations = _check_python_best_practices(code)
    elif language.lower() == "javascript":
        best_practices, violations = _check_javascript_best_practices(code)
    elif language.lower() == "java":
        best_practices, violations = _check_java_best_practices(code)
    elif language.lower() == "php":
        best_practices, violations = _check_php_best_practices(code)
    else:
        return {"error": f"지원하지 않는 언어: {language}"}

    compliance_score = ((len(best_practices) - len(violations)) / len(best_practices)) * 100 if best_practices else 0

    return {
        "compliance_score": round(compliance_score, 2),
        "total_checks": len(best_practices),
        "violations": len(violations),
        "best_practices": best_practices,
        "violations_detail": violations,
        "language": language
    }

@mcp.tool()
def suggest_fixes(vulnerabilities: List[Dict[str, Any]]) -> Dict[str, Any]:
    """
    취약점별 수정 방법을 제안합니다.

    Args:
        vulnerabilities: 발견된 취약점 목록

    Returns:
        취약점별 수정 제안사항
    """
    fixes = []

    for vuln in vulnerabilities:
        vuln_type = vuln.get("type", "")
        severity = vuln.get("severity", "MEDIUM")
        line = vuln.get("line", 0)

        fix_suggestion = {
            "vulnerability": vuln_type,
            "severity": severity,
            "line": line,
            "description": vuln.get("description", ""),
            "fixes": [],
            "code_examples": []
        }

        if vuln_type == "SQL Injection":
            fix_suggestion["fixes"] = [
                "매개변수화된 쿼리(Prepared Statements) 사용",
                "입력값 검증 및 이스케이핑",
                "ORM 사용 권장"
            ]
            fix_suggestion["code_examples"] = [
                "# 나쁜 예: cursor.execute(f\"SELECT * FROM users WHERE id = {user_id}\")",
                "# 좋은 예: cursor.execute(\"SELECT * FROM users WHERE id = %s\", (user_id,))"
            ]

        elif vuln_type == "XSS":
            fix_suggestion["fixes"] = [
                "출력값 이스케이핑",
                "Content Security Policy (CSP) 설정",
                "입력값 검증 및 필터링"
            ]
            fix_suggestion["code_examples"] = [
                "# 나쁜 예: return f\"<div>{user_input}</div>\"",
                "# 좋은 예: return f\"<div>{html.escape(user_input)}</div>\""
            ]

        elif vuln_type == "Path Traversal":
            fix_suggestion["fixes"] = [
                "경로 검증 및 정규화",
                "화이트리스트 기반 파일 접근",
                "상위 디렉토리 접근 차단"
            ]
            fix_suggestion["code_examples"] = [
                "# 나쁜 예: open(f\"/uploads/{filename}\")",
                "# 좋은 예: safe_filename = os.path.basename(filename); open(f\"/uploads/{safe_filename}\")"
            ]

        elif vuln_type == "Hardcoded Secrets":
            fix_suggestion["fixes"] = [
                "환경 변수 사용",
                "시크릿 관리 도구 활용",
                "설정 파일 분리"
            ]
            fix_suggestion["code_examples"] = [
                "# 나쁜 예: password = \"secret123\"",
                "# 좋은 예: password = os.getenv('DB_PASSWORD')"
            ]

        elif vuln_type == "Weak Cryptography":
            fix_suggestion["fixes"] = [
                "강력한 해시 알고리즘 사용 (bcrypt, scrypt)",
                "적절한 솔트 사용",
                "최신 암호화 라이브러리 활용"
            ]
            fix_suggestion["code_examples"] = [
                "# 나쁜 예: hashlib.md5(password).hexdigest()",
                "# 좋은 예: bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())"
            ]

        fixes.append(fix_suggestion)

    return {
        "total_fixes": len(fixes),
        "fixes": fixes,
        "priority_order": sorted(fixes, key=lambda x: {"HIGH": 3, "MEDIUM": 2, "LOW": 1}[x["severity"]], reverse=True)
    }

def _scan_python_vulnerabilities(code: str) -> List[Dict[str, Any]]:
    """Python 코드의 취약점을 스캔합니다."""
    vulnerabilities = []
    lines = code.split('\n')

    for i, line in enumerate(lines, 1):
        line_lower = line.lower()

        # SQL Injection 패턴
        if re.search(r'execute\s*\(\s*f["\'].*\{.*\}.*["\']', line):
            vulnerabilities.append({
                "type": "SQL Injection",
                "severity": "HIGH",
                "line": i,
                "description": "f-string을 사용한 SQL 쿼리에서 SQL Injection 위험",
                "code": line.strip()
            })

        # XSS 패턴
        if re.search(r'return.*f["\'].*\{.*\}.*["\']', line) and 'escape' not in line_lower:
            vulnerabilities.append({
                "type": "XSS",
                "severity": "MEDIUM",
                "line": i,
                "description": "사용자 입력이 이스케이핑 없이 HTML에 포함됨",
                "code": line.strip()
            })

        # Path Traversal 패턴
        if re.search(r'open\s*\(.*\+.*filename', line) or re.search(r'open\s*\(.*f["\'].*\{.*\}.*["\']', line):
            vulnerabilities.append({
                "type": "Path Traversal",
                "severity": "HIGH",
                "line": i,
                "description": "파일 경로 조작 가능성",
                "code": line.strip()
            })

        # 하드코딩된 시크릿 패턴
        secret_patterns = [
            r'password\s*=\s*["\'][^"\']+["\']',
            r'api_key\s*=\s*["\'][^"\']+["\']',
            r'secret\s*=\s*["\'][^"\']+["\']',
            r'token\s*=\s*["\'][^"\']+["\']'
        ]

        for pattern in secret_patterns:
            if re.search(pattern, line_lower):
                vulnerabilities.append({
                    "type": "Hardcoded Secrets",
                    "severity": "HIGH",
                    "line": i,
                    "description": "하드코딩된 비밀 정보",
                    "code": line.strip()
                })
                break

        # 약한 암호화 패턴
        if re.search(r'md5\s*\(', line_lower) or re.search(r'sha1\s*\(', line_lower):
            vulnerabilities.append({
                "type": "Weak Cryptography",
                "severity": "MEDIUM",
                "line": i,
                "description": "약한 해시 알고리즘 사용",
                "code": line.strip()
            })

        # eval() 사용 패턴
        if 'eval(' in line_lower:
            vulnerabilities.append({
                "type": "Code Injection",
                "severity": "HIGH",
                "line": i,
                "description": "eval() 함수 사용으로 인한 코드 주입 위험",
                "code": line.strip()
            })

    return vulnerabilities

def _scan_javascript_vulnerabilities(code: str) -> List[Dict[str, Any]]:
    """JavaScript 코드의 취약점을 스캔합니다."""
    vulnerabilities = []
    lines = code.split('\n')

    for i, line in enumerate(lines, 1):
        line_lower = line.lower()

        # XSS 패턴
        if re.search(r'innerHTML\s*=', line) and 'textContent' not in line_lower:
            vulnerabilities.append({
                "type": "XSS",
                "severity": "HIGH",
                "line": i,
                "description": "innerHTML 사용으로 인한 XSS 위험",
                "code": line.strip()
            })

        # eval() 사용
        if 'eval(' in line_lower:
            vulnerabilities.append({
                "type": "Code Injection",
                "severity": "HIGH",
                "line": i,
                "description": "eval() 함수 사용으로 인한 코드 주입 위험",
                "code": line.strip()
            })

        # document.write 사용
        if 'document.write(' in line_lower:
            vulnerabilities.append({
                "type": "XSS",
                "severity": "MEDIUM",
                "line": i,
                "description": "document.write() 사용으로 인한 XSS 위험",
                "code": line.strip()
            })

    return vulnerabilities

def _scan_java_vulnerabilities(code: str) -> List[Dict[str, Any]]:
    """Java 코드의 취약점을 스캔합니다."""
    vulnerabilities = []
    lines = code.split('\n')

    for i, line in enumerate(lines, 1):
        line_lower = line.lower()

        # SQL Injection 패턴
        if re.search(r'statement\.execute\s*\(.*\+', line):
            vulnerabilities.append({
                "type": "SQL Injection",
                "severity": "HIGH",
                "line": i,
                "description": "문자열 연결을 사용한 SQL 쿼리",
                "code": line.strip()
            })

        # 하드코딩된 시크릿
        if re.search(r'password\s*=\s*["\'][^"\']+["\']', line_lower):
            vulnerabilities.append({
                "type": "Hardcoded Secrets",
                "severity": "HIGH",
                "line": i,
                "description": "하드코딩된 비밀 정보",
                "code": line.strip()
            })

    return vulnerabilities

def _scan_php_vulnerabilities(code: str) -> List[Dict[str, Any]]:
    """PHP 코드의 취약점을 스캔합니다."""
    vulnerabilities = []
    lines = code.split('\n')

    for i, line in enumerate(lines, 1):
        line_lower = line.lower()

        # SQL Injection 패턴
        if re.search(r'mysql_query\s*\(.*\$', line) or re.search(r'mysqli_query\s*\(.*\$', line):
            vulnerabilities.append({
                "type": "SQL Injection",
                "severity": "HIGH",
                "line": i,
                "description": "직접 변수 삽입을 사용한 SQL 쿼리",
                "code": line.strip()
            })

        # XSS 패턴
        if re.search(r'echo\s+.*\$', line) and 'htmlspecialchars' not in line_lower:
            vulnerabilities.append({
                "type": "XSS",
                "severity": "MEDIUM",
                "line": i,
                "description": "출력값 이스케이핑 없이 변수 출력",
                "code": line.strip()
            })

    return vulnerabilities

def _check_python_best_practices(code: str) -> tuple:
    """Python 보안 베스트 프랙티스를 검증합니다."""
    best_practices = [
        "입력값 검증",
        "출력값 이스케이핑",
        "안전한 SQL 쿼리",
        "환경 변수 사용",
        "강력한 암호화",
        "에러 처리",
        "로깅 보안"
    ]

    violations = []
    lines = code.split('\n')

    for i, line in enumerate(lines, 1):
        line_lower = line.lower()

        # 입력값 검증 부족
        if re.search(r'input\s*\(', line) and 'validate' not in line_lower and 'check' not in line_lower:
            violations.append({
                "line": i,
                "practice": "입력값 검증",
                "description": "사용자 입력에 대한 검증이 없습니다",
                "code": line.strip()
            })

        # 하드코딩된 시크릿
        if re.search(r'password\s*=\s*["\']', line_lower):
            violations.append({
                "line": i,
                "practice": "환경 변수 사용",
                "description": "하드코딩된 비밀 정보가 있습니다",
                "code": line.strip()
            })

    return best_practices, violations

def _check_javascript_best_practices(code: str) -> tuple:
    """JavaScript 보안 베스트 프랙티스를 검증합니다."""
    best_practices = [
        "XSS 방지",
        "CSRF 보호",
        "입력값 검증",
        "안전한 DOM 조작"
    ]

    violations = []
    lines = code.split('\n')

    for i, line in enumerate(lines, 1):
        line_lower = line.lower()

        # innerHTML 사용
        if 'innerhtml' in line_lower:
            violations.append({
                "line": i,
                "practice": "XSS 방지",
                "description": "innerHTML 대신 textContent 사용 권장",
                "code": line.strip()
            })

    return best_practices, violations

def _check_java_best_practices(code: str) -> tuple:
    """Java 보안 베스트 프랙티스를 검증합니다."""
    best_practices = [
        "PreparedStatement 사용",
        "입력값 검증",
        "시크릿 관리",
        "에러 처리"
    ]

    violations = []
    lines = code.split('\n')

    for i, line in enumerate(lines, 1):
        line_lower = line.lower()

        # Statement 사용
        if 'statement.execute' in line_lower and 'preparedstatement' not in line_lower:
            violations.append({
                "line": i,
                "practice": "PreparedStatement 사용",
                "description": "Statement 대신 PreparedStatement 사용 권장",
                "code": line.strip()
            })

    return best_practices, violations

def _check_php_best_practices(code: str) -> tuple:
    """PHP 보안 베스트 프랙티스를 검증합니다."""
    best_practices = [
        "Prepared Statements 사용",
        "입력값 검증",
        "출력값 이스케이핑",
        "에러 처리"
    ]

    violations = []
    lines = code.split('\n')

    for i, line in enumerate(lines, 1):
        line_lower = line.lower()

        # mysql_query 사용
        if 'mysql_query' in line_lower:
            violations.append({
                "line": i,
                "practice": "Prepared Statements 사용",
                "description": "mysql_query 대신 mysqli_prepare 사용 권장",
                "code": line.strip()
            })

    return best_practices, violations

def _calculate_risk_score(vulnerabilities: List[Dict[str, Any]]) -> int:
    """취약점 기반 위험 점수를 계산합니다."""
    if not vulnerabilities:
        return 0

    high_count = sum(1 for v in vulnerabilities if v.get("severity") == "HIGH")
    medium_count = sum(1 for v in vulnerabilities if v.get("severity") == "MEDIUM")
    low_count = sum(1 for v in vulnerabilities if v.get("severity") == "LOW")

    return (high_count * 10) + (medium_count * 5) + (low_count * 1)

@mcp.resource("security://guidelines")
def get_security_guidelines() -> str:
    """보안 가이드라인 리소스를 제공합니다."""
    return """
    Security Code Analyzer 가이드라인:

    1. 입력값 검증:
       - 모든 사용자 입력 검증
       - 화이트리스트 기반 검증 권장
       - 길이 및 형식 제한

    2. SQL Injection 방지:
       - Prepared Statements 사용
       - 매개변수화된 쿼리
       - ORM 활용

    3. XSS 방지:
       - 출력값 이스케이핑
       - Content Security Policy 설정
       - 안전한 DOM 조작

    4. 시크릿 관리:
       - 환경 변수 사용
       - 시크릿 관리 도구 활용
       - 하드코딩 금지
    """

@mcp.prompt()
def security_review_helper(code: str) -> str:
    """
    보안 코드 리뷰를 위한 프롬프트를 생성합니다.

    Args:
        code: 리뷰할 코드
    """
    return f"""
    다음 코드의 보안을 검토해주세요:

    코드:
    {code}

    검토 항목:
    1. 입력값 검증 및 이스케이핑
    2. SQL Injection 취약점
    3. XSS 취약점
    4. 하드코딩된 시크릿
    5. 암호화 강도
    6. 에러 처리 보안

    사용 가능한 도구:
    - scan_vulnerabilities: 취약점 스캔
    - check_best_practices: 베스트 프랙티스 검증
    - suggest_fixes: 수정 방법 제안
    """

if __name__ == "__main__":
    # stdio 모드로 서버 실행
    mcp.run(transport="stdio")
