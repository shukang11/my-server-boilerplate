from datetime import datetime
from enum import IntEnum
from typing import TYPE_CHECKING, Optional

from pydantic import BaseModel, Field

if TYPE_CHECKING:
    from server_core.database import UserInDB


# 用户状态 枚举
class UserStatus(IntEnum):
    # 正常
    NORMAL = 0
    # 禁用
    DISABLE = 1


# 用户模型
class UserModel(BaseModel):
    id: int
    username: Optional[str] = None
    email: Optional[str] = None
    status: Optional[UserStatus] = Field(default=UserStatus.NORMAL)
    create_at: Optional[datetime] = None
    update_at: Optional[datetime] = None

    @classmethod
    def from_db(cls, user: "UserInDB") -> "UserModel":
        return cls(
            id=user.id,
            username=user.username,
            email=user.email,
            status=UserStatus(user.status),
            create_at=user.create_at,
            update_at=user.update_at,
        )


# 创建管理员用户请求
class CreateUserReq(BaseModel):
    username: str
    phone: str
    email: Optional[str] = None
    password_hash: str


# 创建登录请求
class LoginReq(BaseModel):
    username: str
    password: str


class LoginResp(BaseModel):
    token: str


class AuthClaims(BaseModel):
    sub: str  # "subject / user id"
    iat: Optional[datetime] = None  # "issue at 签发时间"

    nbf: Optional[datetime] = None  # "not before"
    exp: Optional[datetime] = None  # "expire at"
