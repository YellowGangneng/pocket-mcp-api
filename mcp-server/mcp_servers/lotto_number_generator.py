from fastmcp import FastMCP
import random
from typing import List, Dict, Any, Optional
from datetime import datetime

# FastMCP 서버 인스턴스 생성
mcp = FastMCP("Lotto Number Generator Server")

@mcp.tool()
def generate_numbers(method: str = "random", exclude_numbers: List[int] = None, 
                    include_numbers: List[int] = None, seed: Optional[int] = None) -> Dict[str, Any]:
    """
    로또 번호를 생성합니다 (1~45 중 6개).
    
    Args:
        method: 생성 방법 ("random", "weighted", "balanced")
        exclude_numbers: 제외할 번호들
        include_numbers: 포함할 번호들
        seed: 랜덤 시드 (재현 가능한 결과를 위해)
    
    Returns:
        생성된 로또 번호와 메타데이터
    """
    if seed is not None:
        random.seed(seed)
    
    # 기본 번호 풀 (1~45)
    number_pool = list(range(1, 46))
    
    # 제외할 번호 제거
    if exclude_numbers:
        number_pool = [num for num in number_pool if num not in exclude_numbers]
    
    # 포함할 번호가 있으면 먼저 추가
    selected_numbers = []
    if include_numbers:
        # 포함할 번호 중 유효한 것만 선택
        valid_include = [num for num in include_numbers if 1 <= num <= 45 and num not in exclude_numbers]
        selected_numbers.extend(valid_include[:6])  # 최대 6개까지만
    
    # 나머지 번호 생성
    remaining_count = 6 - len(selected_numbers)
    if remaining_count > 0:
        if method == "random":
            additional_numbers = random.sample(number_pool, min(remaining_count, len(number_pool)))
        elif method == "weighted":
            # 가중치 기반 선택 (최근에 자주 나온 번호는 가중치 낮게)
            additional_numbers = _weighted_selection(number_pool, remaining_count)
        elif method == "balanced":
            # 균형 잡힌 선택 (고/중/저 구간에서 균등하게)
            additional_numbers = _balanced_selection(number_pool, remaining_count)
        else:
            additional_numbers = random.sample(number_pool, min(remaining_count, len(number_pool)))
        
        selected_numbers.extend(additional_numbers)
    
    # 중복 제거 및 정렬
    selected_numbers = sorted(list(set(selected_numbers)))
    
    # 6개가 안 되면 추가 생성
    while len(selected_numbers) < 6:
        available = [num for num in number_pool if num not in selected_numbers]
        if available:
            selected_numbers.append(random.choice(available))
        else:
            break
    
    # 통계 정보 생성
    stats = _generate_number_stats(selected_numbers)
    
    return {
        "numbers": selected_numbers,
        "method": method,
        "generated_at": datetime.now().isoformat(),
        "seed": seed,
        "statistics": stats,
        "excluded": exclude_numbers or [],
        "included": include_numbers or []
    }

@mcp.tool()
def generate_multiple(count: int = 5, method: str = "random", 
                    exclude_numbers: List[int] = None, seed: Optional[int] = None) -> Dict[str, Any]:
    """
    여러 세트의 로또 번호를 동시에 생성합니다.
    
    Args:
        count: 생성할 세트 수 (1~20)
        method: 생성 방법
        exclude_numbers: 제외할 번호들
        seed: 랜덤 시드
    
    Returns:
        여러 세트의 로또 번호와 분석 정보
    """
    if count < 1 or count > 20:
        return {"error": "세트 수는 1~20 사이여야 합니다."}
    
    if seed is not None:
        random.seed(seed)
    
    all_sets = []
    number_frequency = {}
    
    for i in range(count):
        # 각 세트마다 약간 다른 시드 사용
        set_seed = seed + i if seed is not None else None
        if set_seed is not None:
            random.seed(set_seed)
        
        # 번호 생성 로직 직접 구현
        number_pool = list(range(1, 46))
        if exclude_numbers:
            number_pool = [num for num in number_pool if num not in exclude_numbers]
        
        selected_numbers = []
        
        if method == "random":
            selected_numbers = random.sample(number_pool, min(6, len(number_pool)))
        elif method == "weighted":
            selected_numbers = _weighted_selection(number_pool, 6)
        elif method == "balanced":
            selected_numbers = _balanced_selection(number_pool, 6)
        else:
            selected_numbers = random.sample(number_pool, min(6, len(number_pool)))
        
        # 6개가 안 되면 추가 생성
        while len(selected_numbers) < 6:
            available = [num for num in number_pool if num not in selected_numbers]
            if available:
                selected_numbers.append(random.choice(available))
            else:
                break
        
        # 중복 제거 및 정렬
        selected_numbers = sorted(list(set(selected_numbers)))
        
        # 통계 정보 생성
        stats = _generate_number_stats(selected_numbers)
        
        result = {
            "numbers": selected_numbers,
            "method": method,
            "generated_at": datetime.now().isoformat(),
            "seed": set_seed,
            "statistics": stats,
            "excluded": exclude_numbers or [],
            "included": []
        }
        
        all_sets.append(result)
        
        # 번호 빈도 계산
        for num in result["numbers"]:
            number_frequency[num] = number_frequency.get(num, 0) + 1
    
    # 전체 통계
    all_numbers = [num for result in all_sets for num in result["numbers"]]
    overall_stats = _generate_number_stats(all_numbers)
    
    # 가장 자주 나온 번호들
    most_frequent = sorted(number_frequency.items(), key=lambda x: x[1], reverse=True)[:10]
    
    # 중복 세트 확인
    unique_sets = len(set(tuple(sorted(result["numbers"])) for result in all_sets))
    
    return {
        "sets": all_sets,
        "total_sets": count,
        "unique_sets": unique_sets,
        "number_frequency": dict(most_frequent),
        "overall_statistics": overall_stats,
        "generated_at": datetime.now().isoformat()
    }

def _weighted_selection(number_pool: List[int], count: int) -> List[int]:
    """가중치 기반 번호 선택 (최근 자주 나온 번호는 가중치 낮게)"""
    # 실제로는 과거 데이터가 필요하지만, 여기서는 랜덤하게 가중치 생성
    weights = {num: random.random() for num in number_pool}
    
    # 가중치 기반 선택
    weighted_pool = []
    for num in number_pool:
        weight = int(weights[num] * 100) + 1
        weighted_pool.extend([num] * weight)
    
    return random.sample(weighted_pool, min(count, len(set(weighted_pool))))

def _balanced_selection(number_pool: List[int], count: int) -> List[int]:
    """균형 잡힌 번호 선택 (고/중/저 구간에서 균등하게)"""
    low_range = [num for num in number_pool if 1 <= num <= 15]
    mid_range = [num for num in number_pool if 16 <= num <= 30]
    high_range = [num for num in number_pool if 31 <= num <= 45]
    
    selected = []
    ranges = [low_range, mid_range, high_range]
    
    # 각 구간에서 균등하게 선택
    per_range = count // 3
    remainder = count % 3
    
    for i, range_nums in enumerate(ranges):
        take_count = per_range + (1 if i < remainder else 0)
        if range_nums and take_count > 0:
            selected.extend(random.sample(range_nums, min(take_count, len(range_nums))))
    
    return selected

def _generate_number_stats(numbers: List[int]) -> Dict[str, Any]:
    """번호 통계를 생성합니다."""
    if not numbers:
        return {}
    
    # 구간별 분포
    low_count = len([n for n in numbers if 1 <= n <= 15])
    mid_count = len([n for n in numbers if 16 <= n <= 30])
    high_count = len([n for n in numbers if 31 <= n <= 45])
    
    # 홀수/짝수 분포
    odd_count = len([n for n in numbers if n % 2 == 1])
    even_count = len(numbers) - odd_count
    
    # 연속 번호 확인
    sorted_nums = sorted(numbers)
    consecutive_count = 0
    for i in range(len(sorted_nums) - 1):
        if sorted_nums[i+1] - sorted_nums[i] == 1:
            consecutive_count += 1
    
    # 합계
    total_sum = sum(numbers)
    
    return {
        "range_distribution": {
            "low": low_count,
            "mid": mid_count,
            "high": high_count
        },
        "odd_even_distribution": {
            "odd": odd_count,
            "even": even_count
        },
        "consecutive_pairs": consecutive_count,
        "total_sum": total_sum,
        "average": round(total_sum / len(numbers), 2),
        "range": max(numbers) - min(numbers)
    }

@mcp.resource("lotto://statistics")
def get_lotto_statistics() -> str:
    """로또 통계 정보 리소스를 제공합니다."""
    return """
    로또 번호 생성 통계 정보:
    
    1. 번호 분포:
       - 저구간 (1-15): 33.3%
       - 중구간 (16-30): 33.3%
       - 고구간 (31-45): 33.3%
    
    2. 홀수/짝수 분포:
       - 균등한 분포가 일반적
       - 3:3 또는 4:2 비율 권장
    
    3. 연속 번호:
       - 연속 번호 2-3개 포함 가능
       - 너무 많은 연속 번호는 피하는 것이 좋음
    
    4. 합계 범위:
       - 일반적인 합계: 90-200
       - 너무 높거나 낮은 합계는 피하는 것이 좋음
    """

@mcp.prompt()
def lotto_strategy_helper(strategy: str) -> str:
    """
    로또 번호 선택 전략을 위한 프롬프트를 생성합니다.
    
    Args:
        strategy: 사용할 전략 ("random", "balanced", "hot_numbers", "cold_numbers")
    """
    return f"""
    로또 번호 선택 전략: {strategy}
    
    사용 가능한 도구:
    1. generate_numbers: 단일 세트 생성
       - method: "random", "weighted", "balanced"
       - exclude_numbers: 제외할 번호
       - include_numbers: 포함할 번호
    
    2. generate_multiple: 여러 세트 생성
       - count: 생성할 세트 수
       - 다양한 방법으로 여러 세트 생성
    
    전략별 권장사항:
    - random: 완전 랜덤 선택
    - balanced: 고/중/저 구간 균등 분포
    - weighted: 과거 데이터 기반 가중치 적용
    
    번호 생성 후 통계를 확인하여 균형 잡힌 조합인지 검토해주세요.
    """

if __name__ == "__main__":
    # stdio 모드로 서버 실행
    mcp.run(transport="stdio")
