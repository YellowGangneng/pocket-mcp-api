"""
MCP Schedule Server - Schedule CRUD MCP Server using FastMCP
"""
from fastmcp import FastMCP
from datetime import datetime
from typing import List, Optional
import uuid

mcp = FastMCP("Schedule MCP Server")

# Schedule storage
schedule_storage = []

# Initialize with sample schedule
def init_sample_schedules():
    sample_schedule = {
        "schedule_id": "SCH-20240201-0001",
        "title": "프로젝트 킥오프 회의",
        "user_id": "USR-10023",
        "start_time": "2024-02-01T10:00:00+09:00",
        "end_time": "2024-02-01T11:00:00+09:00",
        "participants": ["USR-10023", "USR-10045"],
        "description": "회의 안건: 프로젝트 범위 확정",
        "location": "서울 본사 3층 회의실",
        "created_at": "2024-01-25T09:15:00+09:00"
    }
    schedule_storage.append(sample_schedule)

init_sample_schedules()


def generate_schedule_id() -> str:
    """Generate unique schedule ID"""
    now = datetime.now()
    date_str = now.strftime("%Y%m%d")
    unique_id = str(uuid.uuid4())[:8].upper()
    return f"SCH-{date_str}-{unique_id}"


@mcp.tool()
def create_schedule(
    title: str,
    user_id: str,
    start_time: str,
    end_time: str,
    participants: Optional[List[str]] = None,
    description: Optional[str] = None,
    location: Optional[str] = None
) -> dict:
    """
    새로운 일정을 생성합니다.

    Args:
        title: 일정 제목
        user_id: 일정 소유자(작성자) ID
        start_time: 시작 시간 (ISO 8601 format)
        end_time: 종료 시간 (ISO 8601 format)
        participants: 참석자 ID 목록
        description: 일정 상세 내용
        location: 장소

    Returns:
        생성된 일정 정보
    """
    try:
        # Parse datetime strings
        start_dt = datetime.fromisoformat(start_time.replace("Z", "+00:00"))
        end_dt = datetime.fromisoformat(end_time.replace("Z", "+00:00"))

        # Validate time range
        if start_dt >= end_dt:
            return {
                "success": False,
                "error": "시작 시간은 종료 시간보다 빨라야 합니다."
            }

        # Create new schedule
        schedule = {
            "schedule_id": generate_schedule_id(),
            "title": title,
            "user_id": user_id,
            "start_time": start_dt.isoformat(),
            "end_time": end_dt.isoformat(),
            "participants": participants or [],
            "description": description,
            "location": location,
            "created_at": datetime.now().isoformat()
        }

        schedule_storage.append(schedule)

        return {
            "success": True,
            "message": "일정이 성공적으로 생성되었습니다.",
            "schedule": schedule
        }

    except Exception as e:
        return {
            "success": False,
            "error": f"일정 생성 중 오류가 발생했습니다: {str(e)}"
        }


@mcp.tool()
def read_schedule(
    schedule_id: Optional[str] = None,
    user_id: Optional[str] = None,
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
    limit: int = 50
) -> dict:
    """
    일정을 조회합니다. 특정 ID로 조회하거나 사용자별, 날짜별로 필터링할 수 있습니다.

    Args:
        schedule_id: 조회할 일정의 고유 ID
        user_id: 특정 사용자의 일정만 조회
        start_date: 조회 시작 날짜 (YYYY-MM-DD)
        end_date: 조회 종료 날짜 (YYYY-MM-DD)
        limit: 최대 조회 개수

    Returns:
        조회된 일정 목록
    """
    try:
        filtered_schedules = []

        for schedule in schedule_storage:
            # Filter by schedule_id
            if schedule_id and schedule["schedule_id"] != schedule_id:
                continue

            # Filter by user_id
            if user_id and schedule["user_id"] != user_id:
                continue

            # Filter by date range
            if start_date:
                start_dt = datetime.fromisoformat(f"{start_date}T00:00:00")
                schedule_start = datetime.fromisoformat(schedule["start_time"])
                if schedule_start.date() < start_dt.date():
                    continue

            if end_date:
                end_dt = datetime.fromisoformat(f"{end_date}T23:59:59")
                schedule_start = datetime.fromisoformat(schedule["start_time"])
                if schedule_start.date() > end_dt.date():
                    continue

            filtered_schedules.append(schedule)

        # Apply limit
        filtered_schedules = filtered_schedules[:limit]

        return {
            "success": True,
            "count": len(filtered_schedules),
            "schedules": filtered_schedules
        }

    except Exception as e:
        return {
            "success": False,
            "error": f"일정 조회 중 오류가 발생했습니다: {str(e)}"
        }


@mcp.tool()
def update_schedule(
    schedule_id: str,
    title: Optional[str] = None,
    start_time: Optional[str] = None,
    end_time: Optional[str] = None,
    participants: Optional[List[str]] = None,
    description: Optional[str] = None,
    location: Optional[str] = None
) -> dict:
    """
    기존 일정을 수정합니다.

    Args:
        schedule_id: 수정할 일정의 고유 ID
        title: 일정 제목
        start_time: 시작 시간 (ISO 8601 format)
        end_time: 종료 시간 (ISO 8601 format)
        participants: 참석자 ID 목록
        description: 일정 상세 내용
        location: 장소

    Returns:
        수정된 일정 정보
    """
    try:
        # Find schedule
        schedule = None
        for s in schedule_storage:
            if s["schedule_id"] == schedule_id:
                schedule = s
                break

        if not schedule:
            return {
                "success": False,
                "error": f"일정을 찾을 수 없습니다: {schedule_id}"
            }

        # Update fields
        if title:
            schedule["title"] = title

        if start_time:
            start_dt = datetime.fromisoformat(start_time.replace("Z", "+00:00"))
            schedule["start_time"] = start_dt.isoformat()

        if end_time:
            end_dt = datetime.fromisoformat(end_time.replace("Z", "+00:00"))
            schedule["end_time"] = end_dt.isoformat()

        # Validate time range after update
        start_dt = datetime.fromisoformat(schedule["start_time"])
        end_dt = datetime.fromisoformat(schedule["end_time"])
        if start_dt >= end_dt:
            return {
                "success": False,
                "error": "시작 시간은 종료 시간보다 빨라야 합니다."
            }

        if participants is not None:
            schedule["participants"] = participants

        if description is not None:
            schedule["description"] = description

        if location is not None:
            schedule["location"] = location

        return {
            "success": True,
            "message": "일정이 성공적으로 수정되었습니다.",
            "schedule": schedule
        }

    except Exception as e:
        return {
            "success": False,
            "error": f"일정 수정 중 오류가 발생했습니다: {str(e)}"
        }


@mcp.tool()
def delete_schedule(schedule_id: str) -> dict:
    """
    일정을 삭제합니다.

    Args:
        schedule_id: 삭제할 일정의 고유 ID

    Returns:
        삭제 결과
    """
    try:
        # Find and remove schedule
        for i, schedule in enumerate(schedule_storage):
            if schedule["schedule_id"] == schedule_id:
                deleted_schedule = schedule_storage.pop(i)
                return {
                    "success": True,
                    "message": "일정이 성공적으로 삭제되었습니다.",
                    "deleted_schedule_id": schedule_id,
                    "deleted_title": deleted_schedule["title"]
                }

        return {
            "success": False,
            "error": f"일정을 찾을 수 없습니다: {schedule_id}"
        }

    except Exception as e:
        return {
            "success": False,
            "error": f"일정 삭제 중 오류가 발생했습니다: {str(e)}"
        }


if __name__ == "__main__":
    mcp.run(transport="stdio")