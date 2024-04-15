import logging
from typing import Optional

from fastapi import Depends, Request
from sqlalchemy.orm import Session

from server_api.dependencies import get_session
from server_core.authentication import AuthController, AuthenticationException
from server_core.authentication.schema import UserModel
from server_core.utils import getmd5

logger = logging.getLogger(__name__)


def auth_header(request: Request) -> None:
    os_ = request.query_params.get("os", "")
    pkg = request.query_params.get("pkg", "")
    request.query_params.get("tk", "")
    vn = request.query_params.get("vn", "")
    lang = request.query_params.get("lang", "")
    ts = request.query_params.get("ts", "")

    vc = request.query_params.get("vc", "")

    salt = "3582d6815e095be3d83fecae039ef46e88cff3844bba6c5f703dae669a9a6647"
    origin = f"{pkg}{vn}{lang}{os_}{ts}{salt}" or ""
    if not origin:
        raise AuthenticationException()

    hashed = getmd5(origin)
    if not hashed:
        raise AuthenticationException()

    if vc.lower() != hashed.lower():
        raise AuthenticationException()


def _get_token(request: Request) -> Optional[str]:
    return request.headers.get("Authorization")


def get_current_avaliable_user(
    token: Optional[str] = Depends(_get_token), session: Session = Depends(get_session)
) -> UserModel:
    try:
        user = AuthController.get_current_user(session=session, jwt_token=token)
        if not user:
            raise AuthenticationException("Token has expired")
        return user
    except Exception:
        raise AuthenticationException("Token has expired")
