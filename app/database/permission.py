from datetime import datetime
from typing import Optional

from sqlalchemy import SMALLINT, DateTime, Integer, Sequence, String
from sqlalchemy.orm import Mapped, mapped_column

from ._base_model import DBBaseModel


class PermissionInDB(DBBaseModel):
    __tablename__ = "permission"

    id: Mapped[int] = mapped_column(
        Integer,
        Sequence(start=1, increment=1, name="permission_id_sep"),
        primary_key=True,
        comment="permission id",
    )
    identifier: Mapped[str] = mapped_column(
        String(64), index=True, nullable=False, comment="权限标识"
    )
    permission_name: Mapped[str] = mapped_column(
        String(32), nullable=False, comment="权限名称"
    )

    remark: Mapped[Optional[str]] = mapped_column(
        String(100), nullable=True, comment="备注"
    )
    enabled: Mapped[int] = mapped_column(
        SMALLINT, default=1, nullable=True, comment="是否启用, 0 禁用 1 启用 2 废弃"
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.now, comment="创建时间"
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.now, onupdate=datetime.now, comment="更新时间"
    )

    def __init__(
        self, identifier: str, permission_name: str, remark: Optional[str] = None
    ) -> None:
        self.identifier = identifier
        self.permission_name = permission_name
        self.remark = remark


class PermissionRoleInDB(DBBaseModel):
    __tablename__ = "permission_role"

    id: Mapped[int] = mapped_column(
        Integer,
        Sequence(start=1, increment=1, name="permission_role_id_seq"),
        primary_key=True,
        comment="permission_role id",
    )
    role_id: Mapped[int] = mapped_column(Integer, nullable=False, comment="角色标识")
    permission_id: Mapped[int] = mapped_column(
        Integer, nullable=False, comment="权限标识"
    )

    def __init__(self, role_id: int, permission_id: int) -> None:
        self.role_id = role_id
        self.permission_id = permission_id
