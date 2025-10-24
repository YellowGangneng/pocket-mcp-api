"""API endpoints for managing likes."""

from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import Select, select
from sqlalchemy.ext.asyncio import AsyncSession

from pocket.app.core.database import get_session
from pocket.app.models import Like
from pocket.app.models.enums import TargetEnum
from pocket.app.schemas import LikeCreate, LikeListResponse, LikeRead, MessageResponse

router = APIRouter()


@router.get(
    "/",
    response_model=LikeListResponse,
    summary="좋아요 목록 조회",
)
async def list_likes(
    session: AsyncSession = Depends(get_session),
) -> LikeListResponse:
    """Return all likes without any filters."""

    query: Select[tuple[Like]] = select(Like)
    result = await session.execute(query)
    likes = result.scalars().all()

    return LikeListResponse(data=[LikeRead.model_validate(like) for like in likes])


@router.get(
    "/{like_id}",
    response_model=LikeRead,
    summary="좋아요 단건 조회",
)
async def retrieve_like(like_id: int, session: AsyncSession = Depends(get_session)) -> LikeRead:
    """Fetch a single like entry."""

    like = await session.get(Like, like_id)
    if like is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="좋아요 정보를 찾을 수 없습니다.")

    return LikeRead.model_validate(like)


@router.post(
    "/",
    response_model=LikeRead,
    status_code=status.HTTP_201_CREATED,
    summary="좋아요 등록",
)
async def create_like(payload: LikeCreate, session: AsyncSession = Depends(get_session)) -> LikeRead:
    """Create a like entry manually."""

    exists = await session.execute(
        select(Like).where(
            Like.target_id == payload.target_id,
            Like.target_type == payload.target_type,
            Like.user_id == payload.user_id,
        )
    )
    if exists.scalars().first():
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="이미 존재하는 좋아요입니다.")

    like = Like(**payload.model_dump())
    session.add(like)
    await session.commit()
    await session.refresh(like)

    return LikeRead.model_validate(like)


@router.delete(
    "/{like_id}",
    response_model=MessageResponse,
    summary="좋아요 삭제",
)
async def delete_like(like_id: int, session: AsyncSession = Depends(get_session)) -> MessageResponse:
    """Delete a like entry."""

    like = await session.get(Like, like_id)
    if like is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="좋아요 정보를 찾을 수 없습니다.")

    await session.delete(like)
    await session.commit()

    return MessageResponse(message="좋아요가 삭제되었습니다.")
