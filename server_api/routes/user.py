from fastapi import APIRouter, Depends

from server_api.dependencies import get_session
from server_api.middleware.auth import get_current_avaliable_user
from server_api.response import ResponseError, ResponseSucc
from server_core.authentication import AuthController, LoginReq, LoginResp, UserModel

router = APIRouter(prefix="/auth", tags=["个人信息接口"])


@router.post(
    "/login",
    summary="登录",
    description="学员登录",
    response_model=ResponseSucc[LoginResp],
)
async def customer_login(
    req: LoginReq, session=Depends(get_session)
) -> ResponseSucc[LoginResp]:
    user = AuthController(session=session).login_user(req=req)
    if not user:
        return ResponseError.from_error("login failed")
    return ResponseSucc(data=user)


@router.post(
    "/info",
    summary="用户信息",
    description="获得用户信息",
    response_model=ResponseSucc[UserModel],
)
async def customer_info(
    user: UserModel = Depends(get_current_avaliable_user),
) -> ResponseSucc[UserModel]:
    return ResponseSucc(data=user)


@router.post(
    "/logout",
    summary="登出",
    description="学员登出",
    response_model=ResponseSucc[bool],
)
async def customer_logout() -> ResponseSucc[UserModel]:
    return ResponseSucc(data=True)
