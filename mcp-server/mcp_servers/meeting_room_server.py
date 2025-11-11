"""
MCP Meeting Room Reservation Server - Meeting Room CRUD MCP Server using FastMCP
"""
from fastmcp import FastMCP
from datetime import datetime
from typing import List, Optional
import uuid

mcp = FastMCP("Meeting Room Reservation Server")

# Meeting room reservation storage
reservation_storage = []

# Meeting room list
meeting_rooms = [
    {"room_id": "ROOM-001", "name": "서울 본사 3층 회의실 A", "capacity": 10, "location": "서울 본사 3층"},
    {"room_id": "ROOM-002", "name": "서울 본사 3층 회의실 B", "capacity": 6, "location": "서울 본사 3층"},
    {"room_id": "ROOM-003", "name": "서울 본사 4층 대회의실", "capacity": 20, "location": "서울 본사 4층"},
    {"room_id": "ROOM-004", "name": "부산 지사 회의실", "capacity": 8, "location": "부산 지사 2층"}
]


# Initialize with sample reservation
def init_sample_reservations():
    sample_reservation = {
        "reservation_id": "RSV-20240201-0001",
        "room_id": "ROOM-001",
        "room_name": "서울 본사 3층 회의실 A",
        "meeting_title": "2024 Q1 전략 회의",
        "organizer_id": "USR-10023",
        "organizer_name": "김철수",
        "start_time": "2024-02-01T14:00:00+09:00",
        "end_time": "2024-02-01T16:00:00+09:00",
        "participants": ["USR-10023", "USR-10045", "USR-10067"],
        "participant_count": 3,
        "meeting_description": "2024년 1분기 사업 전략 논의",
        "equipment_needed": ["프로젝터", "화이트보드"],
        "status": "confirmed",
        "created_at": "2024-01-25T09:30:00+09:00"
    }
    reservation_storage.append(sample_reservation)

init_sample_reservations()


def generate_reservation_id() -> str:
    """Generate unique reservation ID"""
    now = datetime.now()
    date_str = now.strftime("%Y%m%d")
    unique_id = str(uuid.uuid4())[:8].upper()
    return f"RSV-{date_str}-{unique_id}"


def get_room_info(room_id: str) -> dict:
    """Get meeting room information by room_id"""
    for room in meeting_rooms:
        if room["room_id"] == room_id:
            return room
    return None


def check_room_availability(room_id: str, start_time: str, end_time: str, exclude_reservation_id: str = None) -> bool:
    """Check if meeting room is available for the given time period"""
    start_dt = datetime.fromisoformat(start_time)
    end_dt = datetime.fromisoformat(end_time)

    for reservation in reservation_storage:
        # Skip if it's the same reservation (for update)
        if exclude_reservation_id and reservation["reservation_id"] == exclude_reservation_id:
            continue

        # Skip if different room
        if reservation["room_id"] != room_id:
            continue

        # Skip if cancelled
        if reservation.get("status") == "cancelled":
            continue

        rsv_start = datetime.fromisoformat(reservation["start_time"])
        rsv_end = datetime.fromisoformat(reservation["end_time"])

        # Check for time overlap
        if (start_dt < rsv_end and end_dt > rsv_start):
            return False

    return True


@mcp.tool()
def create_reservation(
    room_id: str,
    meeting_title: str,
    organizer_id: str,
    organizer_name: str,
    start_time: str,
    end_time: str,
    participants: List[str],
    meeting_description: Optional[str] = None,
    equipment_needed: Optional[List[str]] = None
) -> dict:
    """
    회의실 예약을 생성합니다.

    Args:
        room_id: 회의실 ID (예: ROOM-001)
        meeting_title: 회의 제목
        organizer_id: 예약자(주최자) ID
        organizer_name: 예약자(주최자) 이름
        start_time: 시작 시간 (ISO 8601 format)
        end_time: 종료 시간 (ISO 8601 format)
        participants: 참석자 ID 목록
        meeting_description: 회의 설명
        equipment_needed: 필요한 장비 목록 (예: ["프로젝터", "화이트보드"])

    Returns:
        생성된 예약 정보
    """
    try:
        # Validate meeting room exists
        room_info = get_room_info(room_id)
        if not room_info:
            return {
                "success": False,
                "error": f"존재하지 않는 회의실입니다: {room_id}"
            }

        # Parse datetime strings
        start_dt = datetime.fromisoformat(start_time.replace("Z", "+00:00"))
        end_dt = datetime.fromisoformat(end_time.replace("Z", "+00:00"))

        # Validate time range
        if start_dt >= end_dt:
            return {
                "success": False,
                "error": "시작 시간은 종료 시간보다 빨라야 합니다."
            }

        # Validate time is in the future
        if start_dt < datetime.now(start_dt.tzinfo):
            return {
                "success": False,
                "error": "과거 시간으로 예약할 수 없습니다."
            }

        # Check room availability
        if not check_room_availability(room_id, start_dt.isoformat(), end_dt.isoformat()):
            return {
                "success": False,
                "error": "해당 시간에 회의실이 이미 예약되어 있습니다."
            }

        # Validate capacity
        participant_count = len(participants)
        if participant_count > room_info["capacity"]:
            return {
                "success": False,
                "error": f"회의실 수용 인원({room_info['capacity']}명)을 초과했습니다. (참석자: {participant_count}명)"
            }

        # Create new reservation
        reservation = {
            "reservation_id": generate_reservation_id(),
            "room_id": room_id,
            "room_name": room_info["name"],
            "meeting_title": meeting_title,
            "organizer_id": organizer_id,
            "organizer_name": organizer_name,
            "start_time": start_dt.isoformat(),
            "end_time": end_dt.isoformat(),
            "participants": participants,
            "participant_count": participant_count,
            "meeting_description": meeting_description,
            "equipment_needed": equipment_needed or [],
            "status": "confirmed",
            "created_at": datetime.now().isoformat()
        }

        reservation_storage.append(reservation)

        return {
            "success": True,
            "message": "회의실 예약이 성공적으로 생성되었습니다.",
            "reservation": reservation
        }

    except Exception as e:
        return {
            "success": False,
            "error": f"예약 생성 중 오류가 발생했습니다: {str(e)}"
        }


@mcp.tool()
def read_reservation(
    reservation_id: Optional[str] = None,
    room_id: Optional[str] = None,
    organizer_id: Optional[str] = None,
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
    status: Optional[str] = None,
    limit: int = 50
) -> dict:
    """
    회의실 예약을 조회합니다. 특정 ID로 조회하거나 회의실별, 예약자별, 날짜별, 상태별로 필터링할 수 있습니다.

    Args:
        reservation_id: 조회할 예약의 고유 ID
        room_id: 특정 회의실의 예약만 조회
        organizer_id: 특정 예약자의 예약만 조회
        start_date: 조회 시작 날짜 (YYYY-MM-DD)
        end_date: 조회 종료 날짜 (YYYY-MM-DD)
        status: 예약 상태 (confirmed, cancelled)
        limit: 최대 조회 개수

    Returns:
        조회된 예약 목록
    """
    try:
        filtered_reservations = []

        for reservation in reservation_storage:
            # Filter by reservation_id
            if reservation_id and reservation["reservation_id"] != reservation_id:
                continue

            # Filter by room_id
            if room_id and reservation["room_id"] != room_id:
                continue

            # Filter by organizer_id
            if organizer_id and reservation["organizer_id"] != organizer_id:
                continue

            # Filter by status
            if status and reservation.get("status") != status:
                continue

            # Filter by date range
            if start_date:
                start_dt = datetime.fromisoformat(f"{start_date}T00:00:00")
                reservation_start = datetime.fromisoformat(reservation["start_time"])
                if reservation_start.date() < start_dt.date():
                    continue

            if end_date:
                end_dt = datetime.fromisoformat(f"{end_date}T23:59:59")
                reservation_start = datetime.fromisoformat(reservation["start_time"])
                if reservation_start.date() > end_dt.date():
                    continue

            filtered_reservations.append(reservation)

        # Apply limit
        filtered_reservations = filtered_reservations[:limit]

        return {
            "success": True,
            "count": len(filtered_reservations),
            "reservations": filtered_reservations
        }

    except Exception as e:
        return {
            "success": False,
            "error": f"예약 조회 중 오류가 발생했습니다: {str(e)}"
        }


@mcp.tool()
def update_reservation(
    reservation_id: str,
    room_id: Optional[str] = None,
    meeting_title: Optional[str] = None,
    start_time: Optional[str] = None,
    end_time: Optional[str] = None,
    participants: Optional[List[str]] = None,
    meeting_description: Optional[str] = None,
    equipment_needed: Optional[List[str]] = None
) -> dict:
    """
    기존 회의실 예약을 수정합니다.

    Args:
        reservation_id: 수정할 예약의 고유 ID
        room_id: 회의실 ID
        meeting_title: 회의 제목
        start_time: 시작 시간 (ISO 8601 format)
        end_time: 종료 시간 (ISO 8601 format)
        participants: 참석자 ID 목록
        meeting_description: 회의 설명
        equipment_needed: 필요한 장비 목록

    Returns:
        수정된 예약 정보
    """
    try:
        # Find reservation
        reservation = None
        for r in reservation_storage:
            if r["reservation_id"] == reservation_id:
                reservation = r
                break

        if not reservation:
            return {
                "success": False,
                "error": f"예약을 찾을 수 없습니다: {reservation_id}"
            }

        # Check if reservation is cancelled
        if reservation.get("status") == "cancelled":
            return {
                "success": False,
                "error": "취소된 예약은 수정할 수 없습니다."
            }

        # Update room if changed
        if room_id and room_id != reservation["room_id"]:
            room_info = get_room_info(room_id)
            if not room_info:
                return {
                    "success": False,
                    "error": f"존재하지 않는 회의실입니다: {room_id}"
                }
            reservation["room_id"] = room_id
            reservation["room_name"] = room_info["name"]

        # Update meeting title
        if meeting_title:
            reservation["meeting_title"] = meeting_title

        # Update time
        if start_time:
            start_dt = datetime.fromisoformat(start_time.replace("Z", "+00:00"))
            reservation["start_time"] = start_dt.isoformat()

        if end_time:
            end_dt = datetime.fromisoformat(end_time.replace("Z", "+00:00"))
            reservation["end_time"] = end_dt.isoformat()

        # Validate time range after update
        start_dt = datetime.fromisoformat(reservation["start_time"])
        end_dt = datetime.fromisoformat(reservation["end_time"])
        if start_dt >= end_dt:
            return {
                "success": False,
                "error": "시작 시간은 종료 시간보다 빨라야 합니다."
            }

        # Check room availability (excluding current reservation)
        current_room_id = reservation["room_id"]
        if not check_room_availability(
            current_room_id,
            reservation["start_time"],
            reservation["end_time"],
            exclude_reservation_id=reservation_id
        ):
            return {
                "success": False,
                "error": "해당 시간에 회의실이 이미 예약되어 있습니다."
            }

        # Update participants
        if participants is not None:
            # Validate capacity
            room_info = get_room_info(reservation["room_id"])
            if len(participants) > room_info["capacity"]:
                return {
                    "success": False,
                    "error": f"회의실 수용 인원({room_info['capacity']}명)을 초과했습니다. (참석자: {len(participants)}명)"
                }
            reservation["participants"] = participants
            reservation["participant_count"] = len(participants)

        # Update other fields
        if meeting_description is not None:
            reservation["meeting_description"] = meeting_description

        if equipment_needed is not None:
            reservation["equipment_needed"] = equipment_needed

        return {
            "success": True,
            "message": "예약이 성공적으로 수정되었습니다.",
            "reservation": reservation
        }

    except Exception as e:
        return {
            "success": False,
            "error": f"예약 수정 중 오류가 발생했습니다: {str(e)}"
        }


@mcp.tool()
def delete_reservation(reservation_id: str) -> dict:
    """
    회의실 예약을 삭제(취소)합니다.

    Args:
        reservation_id: 삭제할 예약의 고유 ID

    Returns:
        삭제 결과
    """
    try:
        # Find reservation
        for reservation in reservation_storage:
            if reservation["reservation_id"] == reservation_id:
                # Mark as cancelled instead of removing
                if reservation.get("status") == "cancelled":
                    return {
                        "success": False,
                        "error": "이미 취소된 예약입니다."
                    }

                reservation["status"] = "cancelled"
                reservation["cancelled_at"] = datetime.now().isoformat()

                return {
                    "success": True,
                    "message": "예약이 성공적으로 취소되었습니다.",
                    "cancelled_reservation_id": reservation_id,
                    "meeting_title": reservation["meeting_title"]
                }

        return {
            "success": False,
            "error": f"예약을 찾을 수 없습니다: {reservation_id}"
        }

    except Exception as e:
        return {
            "success": False,
            "error": f"예약 취소 중 오류가 발생했습니다: {str(e)}"
        }


@mcp.tool()
def list_meeting_rooms() -> dict:
    """
    사용 가능한 회의실 목록을 조회합니다.

    Returns:
        회의실 목록
    """
    return {
        "success": True,
        "count": len(meeting_rooms),
        "meeting_rooms": meeting_rooms
    }


@mcp.tool()
def check_availability(
    room_id: str,
    start_time: str,
    end_time: str
) -> dict:
    """
    특정 회의실의 특정 시간대 예약 가능 여부를 확인합니다.

    Args:
        room_id: 회의실 ID
        start_time: 시작 시간 (ISO 8601 format)
        end_time: 종료 시간 (ISO 8601 format)

    Returns:
        예약 가능 여부
    """
    try:
        # Validate meeting room exists
        room_info = get_room_info(room_id)
        if not room_info:
            return {
                "success": False,
                "error": f"존재하지 않는 회의실입니다: {room_id}"
            }

        # Parse datetime strings
        start_dt = datetime.fromisoformat(start_time.replace("Z", "+00:00"))
        end_dt = datetime.fromisoformat(end_time.replace("Z", "+00:00"))

        # Validate time range
        if start_dt >= end_dt:
            return {
                "success": False,
                "error": "시작 시간은 종료 시간보다 빨라야 합니다."
            }

        # Check availability
        is_available = check_room_availability(room_id, start_dt.isoformat(), end_dt.isoformat())

        return {
            "success": True,
            "room_id": room_id,
            "room_name": room_info["name"],
            "start_time": start_dt.isoformat(),
            "end_time": end_dt.isoformat(),
            "is_available": is_available,
            "message": "예약 가능합니다." if is_available else "해당 시간에 이미 예약이 있습니다."
        }

    except Exception as e:
        return {
            "success": False,
            "error": f"예약 가능 여부 확인 중 오류가 발생했습니다: {str(e)}"
        }


if __name__ == "__main__":
    mcp.run(transport="stdio")
