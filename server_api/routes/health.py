from typing import Dict

from fastapi import APIRouter

from server_api.response import ResponseSucc

router = APIRouter(prefix="/health", tags=["health"])


@router.get("/check")
async def health_check_get() -> ResponseSucc[Dict[str, str]]:
    """健康检查"""
    return ResponseSucc[dict](result={"status": "ok"})
