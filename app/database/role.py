from datetime import datetime
from enum import IntEnum
from typing import Optional

from sqlalchemy import SMALLINT, DateTime, Integer, Sequence, String
from sqlalchemy.orm import Mapped, mapped_column

from ._base_model import DBBaseModel


class RoleEnableType(IntEnum):
    # 0 禁用 1 启用 2 废弃
    DISABLE = 0
    ENABLE = 1
    DEPRECATED = 2


class RoleInDB(DBBaseModel):
    __tablename__ = "role"

    id: Mapped[int] = mapped_column(
        Integer,
        Sequence(start=1, increment=1, name="role_id_sep"),
        primary_key=True,
        comment="role id",
    )
    identifier: Mapped[str] = mapped_column(
        String(64), index=True, nullable=False, comment="权限标识"
    )
    role_name: Mapped[str] = mapped_column(
        String(32), nullable=False, comment="角色名称"
    )
    enabled: Mapped[RoleEnableType] = mapped_column(
        SMALLINT, default=1, nullable=True, comment="是否启用, 0 禁用 1 启用 2 废弃"
    )
    remark: Mapped[Optional[str]] = mapped_column(
        String(100), nullable=True, comment="备注"
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.now, comment="创建时间"
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.now, onupdate=datetime.now, comment="更新时间"
    )

    def __init__(self, identifier: str, role_name: str, remark: Optional[str] = None):
        self.identifier = identifier
        self.role_name = role_name
        self.remark = remark
