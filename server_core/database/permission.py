from datetime import datetime
from typing import Optional

from sqlalchemy import SMALLINT, Column, DateTime, Integer, Sequence, String

from ._base_model import DBBaseModel


class Permission(DBBaseModel):
    __tablename__ = "permission"

    id = Column(
        Integer,
        Sequence(start=1, increment=1, name="permission_id_sep"),
        primary_key=True,
        comment="permission id",
    )
    identifier = Column(String(64), index=True, nullable=False, comment="权限标识")
    permission_name = Column(String(32), nullable=False, comment="权限名称")

    remark = Column(String(100), nullable=True, comment="备注")
    enabled = Column(
        SMALLINT, default=1, nullable=True, comment="是否启用, 0 禁用 1 启用 2 废弃"
    )
    created_at = Column(DateTime, default=datetime.now, comment="创建时间")
    updated_at = Column(
        DateTime, default=datetime.now, onupdate=datetime.now, comment="更新时间"
    )

    def __init__(
        self, identifier: str, permission_name: str, remark: Optional[str] = None
    ) -> None:
        self.identifier = identifier
        self.permission_name = permission_name
        self.remark = remark


class PermissionRole(DBBaseModel):
    __tablename__ = "permission_role"

    id = Column(
        Integer,
        Sequence(start=1, increment=1, name="permission_role_id_seq"),
        primary_key=True,
        comment="permission_role id",
    )
    role_id = Column(Integer, nullable=False, comment="角色标识")
    permission_id = Column(Integer, nullable=False, comment="权限标识")

    def __init__(self, role_id: int, permission_id: int) -> None:
        self.role_id = role_id
        self.permission_id = permission_id
