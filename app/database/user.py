from datetime import datetime
from enum import IntEnum
from typing import TYPE_CHECKING, Optional

from sqlalchemy import SMALLINT, DateTime, ForeignKey, Integer, Sequence, String, select
from sqlalchemy.orm import Mapped, joinedload, mapped_column, relationship

from app.utils import getmd5

from ._base_model import DBBaseModel

if TYPE_CHECKING:
    from sqlalchemy.ext.asyncio import AsyncSession


class UserStatus(IntEnum):
    # 状态 0 正常 1 禁用
    NORMAL = 0
    DISABLE = 1


class UserTokenInDB(DBBaseModel):
    __tablename__ = "user_token"

    user_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("user.id"),
        nullable=False,
        primary_key=True,
        comment="user token id",
    )
    token: Mapped[str] = mapped_column(String(32), nullable=False, comment="token")
    created_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.now, comment="创建时间"
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime,
        nullable=True,
        default=datetime.now,
        onupdate=datetime.now,
        comment="更新时间",
    )

    def __init__(self, user_id: int, token: str) -> None:
        self.user_id = user_id
        self.token = token

    def __repr__(self):
        return f"<UserToken(user_id='{self.user_id}', token='{self.token}')>"


class UserInDB(DBBaseModel):
    __tablename__ = "user"

    id: Mapped[int] = mapped_column(
        Integer,
        Sequence(start=1, increment=1, name="db_user_id_sep"),
        primary_key=True,
        comment="user id",
    )
    username: Mapped[Optional[str]] = mapped_column(
        String(64), nullable=True, comment="用户名"
    )
    phone: Mapped[Optional[str]] = mapped_column(
        String(11), nullable=True, comment="手机号"
    )
    email: Mapped[Optional[str]] = mapped_column(
        String(100), nullable=True, comment="邮箱"
    )
    password: Mapped[str] = mapped_column(String(32), nullable=False, comment="密码")
    status: Mapped[UserStatus] = mapped_column(
        SMALLINT, nullable=False, default=0, comment="状态 0 正常 1 禁用"
    )
    create_at: Mapped[datetime] = mapped_column(
        DateTime, nullable=False, default=datetime.now, comment="创建时间"
    )
    update_at: Mapped[datetime] = mapped_column(
        DateTime,
        nullable=False,
        default=datetime.now,
        onupdate=datetime.now,
        comment="更新时间",
    )

    token: Mapped[Optional[UserTokenInDB]] = relationship(
        "UserTokenInDB", backref="user", uselist=False
    )

    def __init__(
        self,
        phone: Optional[str] = None,
        username: Optional[str] = None,
        email: Optional[str] = None,
        password: Optional[str] = None,
    ) -> None:
        self.username = username
        self.email = email
        self.phone = phone
        self.password = password

    @classmethod
    async def find_by_username(
        cls, session: "AsyncSession", username: str
    ) -> Optional["UserInDB"]:
        stmt = select(cls).where(cls.username == username)
        result = await session.scalar(stmt)
        return result

    @classmethod
    async def find_by_id(
        cls, session: "AsyncSession", user_id: int
    ) -> Optional["UserInDB"]:
        stmt = select(cls).where(cls.id == user_id)
        result = await session.scalar(stmt)
        return result

    @classmethod
    async def find_by_token(
        cls, session: "AsyncSession", token: str
    ) -> Optional["UserInDB"]:
        stmt = (
            select(cls)
            .options(joinedload(cls.token))
            .where(UserTokenInDB.token == token)
        )
        result = await session.scalar(stmt)
        return result

    def __repr__(self):
        return f"<User(id='{self.id}', username='{self.username}')>"

    def make_new_token(self, salt: str) -> str:
        raw = f"{self.id}{self.password}{salt}"
        md5_value = getmd5(raw)
        return md5_value
