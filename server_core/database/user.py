from datetime import datetime
from typing import TYPE_CHECKING, Optional

from sqlalchemy import SMALLINT, Column, DateTime, Integer, Sequence, String

from server_core.utils import getmd5

from ._base_model import DBBaseModel

if TYPE_CHECKING:
    from sqlalchemy.orm import Session


class UserToken(DBBaseModel):
    __tablename__ = "user_token"

    user_id = Column(Integer, nullable=False, primary_key=True, comment="admin_user id")
    token = Column(String(32), nullable=False, comment="token")
    created_at = Column(DateTime, default=datetime.now, comment="创建时间")
    updated_at = Column(
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


class User(DBBaseModel):
    __tablename__ = "db_user"

    id = Column(
        Integer,
        Sequence(start=1, increment=1, name="db_user_id_sep"),
        primary_key=True,
        comment="user id",
    )
    username = Column(String(64), nullable=True, comment="用户名")
    phone = Column(String(11), nullable=True, comment="手机号")
    email = Column(String(100), nullable=True, comment="邮箱")
    password = Column(String(32), nullable=False, comment="密码")
    status = Column(SMALLINT, nullable=False, default=0, comment="状态 0 正常 1 禁用")
    create_at = Column(
        DateTime, nullable=False, default=datetime.now, comment="创建时间"
    )
    update_at = Column(
        DateTime,
        nullable=False,
        default=datetime.now,
        onupdate=datetime.now,
        comment="更新时间",
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
    def find_by_username(cls, session: "Session", username: str) -> Optional["User"]:
        return session.query(cls).filter(cls.username == username).first()

    @classmethod
    def find_by_id(cls, session: "Session", user_id: int) -> Optional["User"]:
        return session.query(cls).filter(cls.id == user_id).first()

    @classmethod
    def find_by_token(cls, session: "Session", token: str) -> Optional["User"]:
        user = (
            session.query(User)
            .join(UserToken, User.id == UserToken.user_id)
            .filter(UserToken.token == token)
            .first()
        )
        return user

    def __repr__(self):
        return f"<User(id='{self.id}', username='{self.username}')>"

    def token(self, salt: str) -> str:
        raw = f"{self.id}{self.password}{salt}"
        md5_value = getmd5(raw)
        return md5_value
