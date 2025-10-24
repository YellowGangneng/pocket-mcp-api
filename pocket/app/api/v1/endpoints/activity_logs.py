"""API endpoints for managing activity logs."""

from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import Select, select
from sqlalchemy.ext.asyncio import AsyncSession

from pocket.app.core.database import get_session
from pocket.app.models import ActivityLog
from pocket.app.models.enums import ActivityEnum, TargetEnum
from pocket.app.schemas import (
    ActivityLogCreate,
    ActivityLogListResponse,
    ActivityLogRead,
    ActivityLogResponse,
    ActivityLogUpdate,
    MessageResponse,
)

router = APIRouter()


@router.get(
    "/",
    response_model=ActivityLogListResponse,
    summary="활동 로그 목록 조회",
)
async def list_activity_logs(
    session: AsyncSession = Depends(get_session),
) -> ActivityLogListResponse:
    """Return all activity logs without any filters."""

    query: Select[tuple[ActivityLog]] = select(ActivityLog).order_by(ActivityLog.created_at.desc())
    result = await session.execute(query)
    logs = result.scalars().all()

    return ActivityLogListResponse(data=[ActivityLogRead.model_validate(log) for log in logs])


@router.get(
    "/{log_id}",
    response_model=ActivityLogResponse,
    summary="활동 로그 단건 조회",
)
async def retrieve_activity_log(log_id: int, session: AsyncSession = Depends(get_session)) -> ActivityLogResponse:
    """Fetch a single activity log by identifier."""

    log = await session.get(ActivityLog, log_id)
    if log is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="활동 로그를 찾을 수 없습니다.")

    return ActivityLogResponse(message="활동 로그 조회에 성공했습니다.", data=ActivityLogRead.model_validate(log))


@router.post(
    "/",
    response_model=ActivityLogResponse,
    status_code=status.HTTP_201_CREATED,
    summary="활동 로그 등록",
)
async def create_activity_log(
    payload: ActivityLogCreate,
    session: AsyncSession = Depends(get_session),
) -> ActivityLogResponse:
    """Create a new activity log entry."""

    log = ActivityLog(**payload.model_dump(exclude_unset=True))
    session.add(log)
    await session.commit()
    await session.refresh(log)

    return ActivityLogResponse(message="활동 로그가 생성되었습니다.", data=ActivityLogRead.model_validate(log))


@router.put(
    "/{log_id}",
    response_model=ActivityLogResponse,
    summary="활동 로그 수정",
)
async def update_activity_log(
    log_id: int,
    payload: ActivityLogUpdate,
    session: AsyncSession = Depends(get_session),
) -> ActivityLogResponse:
    """Update an existing activity log entry."""

    log = await session.get(ActivityLog, log_id)
    if log is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="활동 로그를 찾을 수 없습니다.")

    update_data = payload.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(log, field, value)

    await session.commit()
    await session.refresh(log)

    return ActivityLogResponse(message="활동 로그가 수정되었습니다.", data=ActivityLogRead.model_validate(log))


@router.delete(
    "/{log_id}",
    response_model=MessageResponse,
    summary="활동 로그 삭제",
)
async def delete_activity_log(log_id: int, session: AsyncSession = Depends(get_session)) -> MessageResponse:
    """Delete an activity log entry."""

    log = await session.get(ActivityLog, log_id)
    if log is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="활동 로그를 찾을 수 없습니다.")

    await session.delete(log)
    await session.commit()

    return MessageResponse(message="활동 로그가 삭제되었습니다.")
