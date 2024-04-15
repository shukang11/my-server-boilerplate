from datetime import datetime
from typing import Optional

from sqlalchemy import SMALLINT, Column, DateTime, Integer, Sequence, String

from ._base_model import DBBaseModel


class Role(DBBaseModel):
    __tablename__ = "role"

    id = Column(
        Integer,
        Sequence(start=1, increment=1, name="role_id_sep"),
        primary_key=True,
        comment="role id",
    )
    identifier = Column(String(64), index=True, nullable=False, comment="权限标识")
    role_name = Column(String(32), nullable=False, comment="角色名称")
    enabled = Column(
        SMALLINT, default=1, nullable=True, comment="是否启用, 0 禁用 1 启用 2 废弃"
    )
    remark = Column(String(100), nullable=True, comment="备注")
    created_at = Column(DateTime, default=datetime.now, comment="创建时间")
    updated_at = Column(
        DateTime, default=datetime.now, onupdate=datetime.now, comment="更新时间"
    )

    def __init__(self, identifier: str, role_name: str, remark: Optional[str] = None):
        self.identifier = identifier
        self.role_name = role_name
        self.remark = remark
