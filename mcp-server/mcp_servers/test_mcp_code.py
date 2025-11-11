from fastmcp import FastMCP

# FastMCP 서버 인스턴스 생성
mcp = FastMCP("Simple Calculator Server")

@mcp.tool()
def greet(name: str) -> str:
    """
    사용자에게 인사를 합니다.
    
    Args:
        name: 인사할 사람의 이름
    
    Returns:
        인사 메시지
    """
    return f"안녕하세요, {name}님! fastMCP 서버에 오신 것을 환영합니다."

@mcp.tool()
def add(a: float, b: float) -> float:
    """
    두 숫자를 더합니다.
    
    Args:
        a: 첫 번째 숫자
        b: 두 번째 숫자
    
    Returns:
        두 숫자의 합
    """
    return a + b

@mcp.tool()
def multiply(a: float, b: float) -> float:
    """
    두 숫자를 곱합니다.
    
    Args:
        a: 첫 번째 숫자
        b: 두 번째 숫자
    
    Returns:
        두 숫자의 곱
    """
    return a * b

@mcp.resource("greeting://welcome")
def get_welcome_message() -> str:
    """환영 메시지 리소스를 제공합니다."""
    return """
    Simple Calculator Server에 오신 것을 환영합니다!
    
    이 서버는 다음 기능을 제공합니다:
    - greet: 사용자에게 인사
    - add: 두 숫자 더하기
    - multiply: 두 숫자 곱하기
    """

@mcp.prompt()
def math_problem_solver(problem: str) -> str:
    """
    수학 문제 해결을 위한 프롬프트를 생성합니다.
    
    Args:
        problem: 해결할 수학 문제
    """
    return f"""
    다음 수학 문제를 해결해주세요:
    
    문제: {problem}
    
    사용 가능한 도구:
    - add(a, b): 두 숫자를 더합니다
    - multiply(a, b): 두 숫자를 곱합니다
    
    단계별로 문제를 해결하고 결과를 설명해주세요.
    """

if __name__ == "__main__":
    # stdio 모드로 서버 실행
    mcp.run(transport="stdio")