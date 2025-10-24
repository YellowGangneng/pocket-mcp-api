"""API v1 router declarations."""

from fastapi import APIRouter

from pocket.app.api.v1.endpoints.activity_logs import router as activity_logs_router
from pocket.app.api.v1.endpoints.likes import router as likes_router
from pocket.app.api.v1.endpoints.mcp_servers import router as mcp_servers_router

api_router = APIRouter()
api_router.include_router(mcp_servers_router, prefix="/mcp_servers", tags=["MCP Servers"])
api_router.include_router(activity_logs_router, prefix="/activity_logs", tags=["Activity Logs"])
api_router.include_router(likes_router, prefix="/likes", tags=["Likes"])
