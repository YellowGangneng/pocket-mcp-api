from fastmcp import FastMCP
import re
from typing import List, Dict, Any, Optional

# FastMCP 서버 인스턴스 생성
mcp = FastMCP("SQL Query Builder Server")

@mcp.tool()
def build_select(table: str, columns: List[str] = None, where_clause: str = None,
                order_by: str = None, limit: int = None) -> str:
    """
    SELECT 쿼리를 빌드합니다.

    Args:
        table: 테이블명
        columns: 선택할 컬럼 목록 (None이면 모든 컬럼)
        where_clause: WHERE 조건
        order_by: 정렬 기준
        limit: 결과 개수 제한

    Returns:
        완성된 SELECT 쿼리
    """
    if columns is None:
        columns_str = "*"
    else:
        columns_str = ", ".join(columns)

    query = f"SELECT {columns_str} FROM {table}"

    if where_clause:
        query += f" WHERE {where_clause}"

    if order_by:
        query += f" ORDER BY {order_by}"

    if limit:
        query += f" LIMIT {limit}"

    return query

@mcp.tool()
def validate_syntax(query: str) -> Dict[str, Any]:
    """
    SQL 문법을 검증합니다.

    Args:
        query: 검증할 SQL 쿼리

    Returns:
        검증 결과 (유효성, 오류 메시지 등)
    """
    query = query.strip().upper()

    # 기본 SQL 키워드 검증
    sql_keywords = ['SELECT', 'FROM', 'WHERE', 'ORDER', 'BY', 'GROUP', 'HAVING', 'INSERT', 'UPDATE', 'DELETE']

    # 괄호 균형 검사
    if query.count('(') != query.count(')'):
        return {
            "valid": False,
            "error": "괄호가 균형을 이루지 않습니다.",
            "suggestion": "열린 괄호와 닫힌 괄호의 개수를 확인해주세요."
        }

    # 기본 문법 검사
    if not any(keyword in query for keyword in sql_keywords):
        return {
            "valid": False,
            "error": "유효한 SQL 키워드가 없습니다.",
            "suggestion": "SELECT, INSERT, UPDATE, DELETE 등의 키워드를 포함해주세요."
        }

    # SELECT 쿼리 검증
    if query.startswith('SELECT'):
        if 'FROM' not in query:
            return {
                "valid": False,
                "error": "SELECT 쿼리에 FROM 절이 없습니다.",
                "suggestion": "FROM 절을 추가해주세요."
            }

    return {
        "valid": True,
        "message": "SQL 문법이 올바릅니다.",
        "query_type": "SELECT" if query.startswith('SELECT') else "OTHER"
    }

@mcp.tool()
def format_query(query: str, indent_size: int = 2) -> str:
    """
    SQL 쿼리를 읽기 쉽게 포매팅합니다.

    Args:
        query: 포매팅할 SQL 쿼리
        indent_size: 들여쓰기 크기

    Returns:
        포매팅된 SQL 쿼리
    """
    # 기본 키워드들
    keywords = ['SELECT', 'FROM', 'WHERE', 'ORDER BY', 'GROUP BY', 'HAVING', 'INSERT', 'UPDATE', 'DELETE', 'JOIN', 'LEFT JOIN', 'RIGHT JOIN', 'INNER JOIN']

    # 쿼리를 대문자로 변환하고 공백 정리
    formatted = query.strip().upper()

    # 키워드 앞에 줄바꿈 추가
    for keyword in keywords:
        formatted = formatted.replace(f' {keyword}', f'\n{keyword}')

    # 들여쓰기 적용
    lines = formatted.split('\n')
    result_lines = []
    indent_level = 0

    for line in lines:
        line = line.strip()
        if not line:
            continue

        # 들여쓰기 레벨 조정
        if any(keyword in line for keyword in ['WHERE', 'ORDER BY', 'GROUP BY', 'HAVING']):
            indent_level = 1
        elif line.startswith('SELECT') or line.startswith('FROM'):
            indent_level = 0

        # 들여쓰기 적용
        indented_line = ' ' * (indent_level * indent_size) + line
        result_lines.append(indented_line)

    return '\n'.join(result_lines)

@mcp.resource("sql://examples")
def get_sql_examples() -> str:
    """SQL 쿼리 예제 리소스를 제공합니다."""
    return """
    SQL Query Builder Server 예제:

    1. 기본 SELECT 쿼리:
       SELECT * FROM users WHERE age > 18 ORDER BY name

    2. 특정 컬럼 선택:
       SELECT name, email FROM users WHERE status = 'active'

    3. 복잡한 조건:
       SELECT * FROM orders WHERE date >= '2024-01-01' AND total > 1000
    """

@mcp.prompt()
def sql_optimization_helper(query: str) -> str:
    """
    SQL 쿼리 최적화를 위한 프롬프트를 생성합니다.

    Args:
        query: 최적화할 SQL 쿼리
    """
    return f"""
    다음 SQL 쿼리를 분석하고 최적화 방안을 제안해주세요:

    쿼리: {query}

    고려사항:
    1. 인덱스 사용 가능성
    2. JOIN 최적화
    3. WHERE 절 조건 순서
    4. 불필요한 컬럼 제거
    5. 서브쿼리 최적화

    최적화된 쿼리와 개선 사항을 설명해주세요.
    """

if __name__ == "__main__":
    # stdio 모드로 서버 실행
    mcp.run(transport="stdio")
