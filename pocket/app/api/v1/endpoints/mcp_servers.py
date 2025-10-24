"""API endpoints for managing MCP servers."""

from collections.abc import Sequence
from typing import Optional
from venv import logger

from fastapi import APIRouter, Depends, HTTPException, Query, Request, status
from sqlalchemy import Select, select
from sqlalchemy.ext.asyncio import AsyncSession

from pocket.app.core.database import get_session
from pocket.app.models import ActivityLog, Like, MCPServer
from pocket.app.models.enums import ActivityEnum, DeviceEnum, StatusEnum, TargetEnum, VisibilityEnum
from pocket.app.schemas import (
    LikeActionResponse,
    MCPServerCreate,
    MCPServerCreateResponse,
    MCPServerDetailResponse,
    MCPServerLikeRequest,
    MCPServerListResponse,
    MCPServerRead,
    MCPServerUpdate,
    MessageResponse,
)

router = APIRouter()


def _client_ip(request: Request) -> Optional[str]:
    """Extract the client's IP address from the incoming request."""

    client = request.client
    return client.host if client else None


async def _log_activity(
    session: AsyncSession,
    *,
    user_id: int,
    activity: Optional[ActivityEnum],
    target_id: int,
    company_code: Optional[int],
    ip_address: Optional[str],
    device: Optional[DeviceEnum],
) -> None:
    """Persist an activity log entry associated with MCP server changes."""
    
    if activity is None:
        print(f"WARNING: activity is None for user_id={user_id}, target_id={target_id}")
        return

    log = ActivityLog(
        user_id=user_id,
        activity_type=activity,
        target_id=target_id,
        target_type=TargetEnum.MCP_SERVER,
        ip_address=ip_address,
        device=device,
        company_code=company_code,
    )
    session.add(log)


@router.post(
    "/",
    response_model=MCPServerCreateResponse,
    status_code=status.HTTP_201_CREATED,
    summary="MCP 서버 등록",
)
async def create_mcp_server(
    payload: MCPServerCreate,
    request: Request,
    session: AsyncSession = Depends(get_session),
) -> MCPServerCreateResponse:
    """Create a new MCP server and store a corresponding activity log."""

    mcp_server = MCPServer(
        title=payload.title,
        description=payload.description,
        status=payload.status,
        user_id=payload.user_id,
        tags=payload.tags,
        io_type=payload.io_type,
        visibility_scope=payload.visibility_scope,
        company_code=payload.company_code,
    )
    session.add(mcp_server)
    await session.flush()

    logger.info(f"Created MCP server with id={mcp_server.id} for user_id={payload.user_id} activityenum : {ActivityEnum.CREATE}")

    await _log_activity(
        session,
        user_id=payload.user_id,
        activity=ActivityEnum.CREATE,
        target_id=mcp_server.id,
        company_code=payload.company_code,
        ip_address=_client_ip(request),
        device=payload.device,
    )

    await session.commit()
    await session.refresh(mcp_server)

    return MCPServerCreateResponse(
        message="MCP 서버가 성공적으로 등록되었습니다.",
        data=MCPServerRead.model_validate(mcp_server),
    )


@router.get(
    "/",
    response_model=MCPServerListResponse,
    summary="MCP 서버 목록 조회",
)
async def list_mcp_servers(
    session: AsyncSession = Depends(get_session),
) -> MCPServerListResponse:
    """Return all MCP servers without any filters."""

    query: Select[tuple[MCPServer]] = select(MCPServer).order_by(MCPServer.created_at.desc())
    result = await session.execute(query)
    records: Sequence[MCPServer] = result.scalars().all()

    return MCPServerListResponse(
        data=[MCPServerRead.model_validate(record) for record in records],
    )


@router.get(
    "/{mcp_id}",
    response_model=MCPServerDetailResponse,
    summary="MCP 서버 단건 조회",
)
async def retrieve_mcp_server(
    mcp_id: int,
    session: AsyncSession = Depends(get_session),
) -> MCPServerDetailResponse:
    """Fetch a single MCP server by identifier."""

    mcp_server = await session.get(MCPServer, mcp_id)
    if mcp_server is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="MCP 서버를 찾을 수 없습니다.")

    return MCPServerDetailResponse(data=MCPServerRead.model_validate(mcp_server))


@router.put(
    "/{mcp_id}",
    response_model=MessageResponse,
    summary="MCP 서버 수정",
)
async def update_mcp_server(
    mcp_id: int,
    payload: MCPServerUpdate,
    request: Request,
    session: AsyncSession = Depends(get_session),
) -> MessageResponse:
    """Update attributes of an existing MCP server owned by the caller."""

    mcp_server = await session.get(MCPServer, mcp_id)
    if mcp_server is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="MCP 서버를 찾을 수 없습니다.")
    if mcp_server.user_id != payload.user_id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="수정 권한이 없습니다.")

    update_data = payload.model_dump(exclude_unset=True)
    update_data.pop("user_id", None)
    device = update_data.pop("device", None)

    for field, value in update_data.items():
        setattr(mcp_server, field, value)

    await _log_activity(
        session,
        user_id=payload.user_id,
        activity=ActivityEnum.UPDATE,
        target_id=mcp_server.id,
        company_code=payload.company_code or mcp_server.company_code,
        ip_address=_client_ip(request),
        device=device,
    )

    await session.commit()
    await session.refresh(mcp_server)

    return MessageResponse(message="MCP 서버가 수정되었습니다.")


@router.delete(
    "/{mcp_id}",
    response_model=MessageResponse,
    summary="MCP 서버 삭제",
)
async def delete_mcp_server(
    mcp_id: int,
    request: Request,
    session: AsyncSession = Depends(get_session),
) -> MessageResponse:
    """Delete an MCP server by ID and log the operation."""

    mcp_server = await session.get(MCPServer, mcp_id)
    if mcp_server is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="MCP 서버를 찾을 수 없습니다.")

    # Store values for activity log before deletion
    user_id = mcp_server.user_id
    company_code = mcp_server.company_code

    await session.delete(mcp_server)
    await _log_activity(
        session,
        user_id=user_id,
        activity=ActivityEnum.DELETE,
        target_id=mcp_id,
        company_code=company_code,
        ip_address=_client_ip(request),
        device=None,
    )
    await session.commit()

    return MessageResponse(message="MCP 서버가 삭제되었습니다.")


@router.post(
    "/{mcp_id}/like",
    response_model=LikeActionResponse,
    status_code=status.HTTP_201_CREATED,
    summary="MCP 서버 좋아요",
)
async def like_mcp_server(
    mcp_id: int,
    *,
    user_id: int = Query(..., description="Identifier of the user performing the like action."),
    session: AsyncSession = Depends(get_session),
) -> LikeActionResponse:
    """Register a like from a user for a specific MCP server."""

    mcp_server = await session.get(MCPServer, mcp_id)
    if mcp_server is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="MCP 서버를 찾을 수 없습니다.")

    existing_like = await session.execute(
        select(Like).where(
            Like.target_id == mcp_id,
            Like.target_type == TargetEnum.MCP_SERVER,
            Like.user_id == user_id,
        )
    )
    if existing_like.scalars().first():
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="이미 좋아요를 누른 MCP 서버입니다.")

    like = Like(target_id=mcp_id, target_type=TargetEnum.MCP_SERVER, user_id=user_id)
    session.add(like)
    await session.commit()

    return LikeActionResponse(message="좋아요가 등록되었습니다.")


@router.delete(
    "/{mcp_id}/like",
    response_model=LikeActionResponse,
    summary="MCP 서버 좋아요 취소",
)
async def unlike_mcp_server(
    mcp_id: int,
    *,
    user_id: int = Query(..., description="Identifier of the user removing the like."),
    session: AsyncSession = Depends(get_session),
) -> LikeActionResponse:
    """Remove a like from a user for a specific MCP server."""

    like_result = await session.execute(
        select(Like).where(
            Like.target_id == mcp_id,
            Like.target_type == TargetEnum.MCP_SERVER,
            Like.user_id == user_id,
        )
    )
    like = like_result.scalars().first()
    if like is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="좋아요 정보가 없습니다.")

    await session.delete(like)
    await session.commit()

    return LikeActionResponse(message="좋아요가 취소되었습니다.")
