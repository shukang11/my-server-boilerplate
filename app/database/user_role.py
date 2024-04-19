from datetime import datetime

from sqlalchemy import DateTime, Integer, Sequence
from sqlalchemy.orm import Mapped, mapped_column

from ._base_model import DBBaseModel


class UserRoleInDB(DBBaseModel):
    __tablename__ = "db_user_role"

    id: Mapped[int] = mapped_column(
        Integer,
        Sequence(start=1, increment=1, name="user_role_id_sep"),
        primary_key=True,
        comment="user_role id",
    )
    user_id: Mapped[int] = mapped_column(Integer, nullable=False, comment="user id")
    role_id: Mapped[int] = mapped_column(
        Integer, nullable=False, comment="admin_role id"
    )
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

    def __init__(self, user_id: int, role_id: int) -> None:
        self.user_id = user_id
        self.role_id = role_id
