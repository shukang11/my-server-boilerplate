from datetime import datetime

from sqlalchemy import Column, DateTime, Integer, Sequence, String

from ._base_model import DBBaseModel


# 用来开启一个事件的追踪标识, 例如: 提交审核，多次驳回，最后通过，可以事件凭证还原流程
class EventCredential(DBBaseModel):
    __tablename__ = "event_credential"

    id = Column(
        Integer,
        Sequence(start=1, increment=1, name="event_credential_id_seq"),
        primary_key=True,
        comment="event_credential id",
    )
    event_name = Column(String(64), index=True, nullable=False, comment="event name")
    remark = Column(String(100), nullable=True, comment="备注")
    create_at = Column(DateTime, default=datetime.now, comment="创建时间")

    def __init__(self, event_name: int, remark: str) -> None:
        self.event_name = event_name
        self.remark = remark
