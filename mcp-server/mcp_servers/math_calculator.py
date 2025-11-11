from fastmcp import FastMCP
import math
import statistics as stats
from typing import List, Dict, Any

# FastMCP 서버 인스턴스 생성
mcp = FastMCP("Math Calculator Server")

@mcp.tool()
def evaluate_expression(expression: str) -> Dict[str, Any]:
    """
    수학 표현식을 계산합니다.

    Args:
        expression: 계산할 수학 표현식 (예: "2 + 3 * 4", "sqrt(16)", "sin(pi/2)")

    Returns:
        계산 결과와 상세 정보
    """
    try:
        # 안전한 수학 함수들만 허용
        safe_dict = {
            "__builtins__": {},
            "abs": abs, "round": round, "min": min, "max": max,
            "sum": sum, "pow": pow, "divmod": divmod,
            "sqrt": math.sqrt, "exp": math.exp, "log": math.log,
            "log10": math.log10, "log2": math.log2,
            "sin": math.sin, "cos": math.cos, "tan": math.tan,
            "asin": math.asin, "acos": math.acos, "atan": math.atan,
            "sinh": math.sinh, "cosh": math.cosh, "tanh": math.tanh,
            "degrees": math.degrees, "radians": math.radians,
            "pi": math.pi, "e": math.e, "tau": math.tau,
            "ceil": math.ceil, "floor": math.floor, "trunc": math.trunc,
            "factorial": math.factorial, "gcd": math.gcd,
            "lcm": lambda a, b: abs(a * b) // math.gcd(a, b) if a and b else 0
        }

        result = eval(expression, safe_dict)

        return {
            "success": True,
            "expression": expression,
            "result": result,
            "type": type(result).__name__
        }

    except ZeroDivisionError:
        return {
            "success": False,
            "error": "0으로 나누기 오류",
            "expression": expression
        }
    except ValueError as e:
        return {
            "success": False,
            "error": f"값 오류: {str(e)}",
            "expression": expression
        }
    except Exception as e:
        return {
            "success": False,
            "error": f"계산 오류: {str(e)}",
            "expression": expression
        }

@mcp.tool()
def calculate_statistics(data: List[float]) -> Dict[str, Any]:
    """
    통계값을 계산합니다 (평균, 중앙값, 표준편차 등).

    Args:
        data: 통계를 계산할 숫자 리스트

    Returns:
        다양한 통계값들
    """
    if not data:
        return {"error": "데이터가 비어있습니다."}

    if len(data) == 1:
        return {
            "mean": data[0],
            "median": data[0],
            "mode": data[0],
            "std_dev": 0.0,
            "variance": 0.0,
            "min": data[0],
            "max": data[0],
            "count": 1
        }

    try:
        return {
            "mean": stats.mean(data),
            "median": stats.median(data),
            "mode": stats.mode(data) if len(set(data)) < len(data) else "No mode",
            "std_dev": stats.stdev(data),
            "variance": stats.variance(data),
            "min": min(data),
            "max": max(data),
            "count": len(data),
            "range": max(data) - min(data)
        }
    except stats.StatisticsError as e:
        return {"error": f"통계 계산 오류: {str(e)}"}

@mcp.tool()
def convert_units(value: float, from_unit: str, to_unit: str, unit_type: str) -> Dict[str, Any]:
    """
    단위를 변환합니다.

    Args:
        value: 변환할 값
        from_unit: 원본 단위
        to_unit: 변환할 단위
        unit_type: 단위 타입 ("length", "weight", "temperature", "area", "volume")

    Returns:
        변환 결과
    """
    # 길이 변환 (미터 기준)
    length_units = {
        "mm": 0.001, "cm": 0.01, "m": 1, "km": 1000,
        "in": 0.0254, "ft": 0.3048, "yd": 0.9144, "mi": 1609.34
    }

    # 무게 변환 (킬로그램 기준)
    weight_units = {
        "mg": 0.000001, "g": 0.001, "kg": 1, "t": 1000,
        "oz": 0.0283495, "lb": 0.453592, "ton": 1000
    }

    # 온도 변환
    def celsius_to_fahrenheit(c):
        return c * 9/5 + 32

    def fahrenheit_to_celsius(f):
        return (f - 32) * 5/9

    # 면적 변환 (제곱미터 기준)
    area_units = {
        "mm²": 0.000001, "cm²": 0.0001, "m²": 1, "km²": 1000000,
        "in²": 0.00064516, "ft²": 0.092903, "yd²": 0.836127, "acre": 4046.86
    }

    # 부피 변환 (리터 기준)
    volume_units = {
        "ml": 0.001, "l": 1, "m³": 1000, "cm³": 0.001,
        "fl_oz": 0.0295735, "cup": 0.236588, "pt": 0.473176, "qt": 0.946353, "gal": 3.78541
    }

    try:
        if unit_type == "length":
            if from_unit not in length_units or to_unit not in length_units:
                return {"error": "지원하지 않는 길이 단위입니다."}
            # 미터로 변환 후 목표 단위로 변환
            meters = value * length_units[from_unit]
            result = meters / length_units[to_unit]

        elif unit_type == "weight":
            if from_unit not in weight_units or to_unit not in weight_units:
                return {"error": "지원하지 않는 무게 단위입니다."}
            # 킬로그램으로 변환 후 목표 단위로 변환
            kg = value * weight_units[from_unit]
            result = kg / weight_units[to_unit]

        elif unit_type == "temperature":
            if from_unit == "c" and to_unit == "f":
                result = celsius_to_fahrenheit(value)
            elif from_unit == "f" and to_unit == "c":
                result = fahrenheit_to_celsius(value)
            elif from_unit == to_unit:
                result = value
            else:
                return {"error": "지원하지 않는 온도 단위입니다. (c: 섭씨, f: 화씨)"}

        elif unit_type == "area":
            if from_unit not in area_units or to_unit not in area_units:
                return {"error": "지원하지 않는 면적 단위입니다."}
            # 제곱미터로 변환 후 목표 단위로 변환
            m2 = value * area_units[from_unit]
            result = m2 / area_units[to_unit]

        elif unit_type == "volume":
            if from_unit not in volume_units or to_unit not in volume_units:
                return {"error": "지원하지 않는 부피 단위입니다."}
            # 리터로 변환 후 목표 단위로 변환
            liters = value * volume_units[from_unit]
            result = liters / volume_units[to_unit]

        else:
            return {"error": "지원하지 않는 단위 타입입니다."}

        return {
            "success": True,
            "value": value,
            "from_unit": from_unit,
            "to_unit": to_unit,
            "result": round(result, 6),
            "unit_type": unit_type
        }

    except Exception as e:
        return {"error": f"변환 오류: {str(e)}"}

@mcp.resource("math://formulas")
def get_math_formulas() -> str:
    """수학 공식 리소스를 제공합니다."""
    return """
    Math Calculator Server 공식 모음:

    기본 연산:
    - 덧셈: a + b
    - 뺄셈: a - b
    - 곱셈: a * b
    - 나눗셈: a / b
    - 거듭제곱: a ** b 또는 pow(a, b)

    삼각함수:
    - sin(x), cos(x), tan(x)
    - asin(x), acos(x), atan(x)

    로그 함수:
    - log(x): 자연로그
    - log10(x): 상용로그
    - log2(x): 이진로그

    기타:
    - sqrt(x): 제곱근
    - abs(x): 절댓값
    - factorial(n): 팩토리얼
    - gcd(a, b): 최대공약수
    - lcm(a, b): 최소공배수
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
    1. evaluate_expression: 수학 표현식 계산
    2. statistics: 통계값 계산 (평균, 중앙값, 표준편차 등)
    3. convert_units: 단위 변환

    단계별로 문제를 분석하고 적절한 도구를 사용하여 해결해주세요.
    """

if __name__ == "__main__":
    # stdio 모드로 서버 실행
    mcp.run(transport="stdio")
