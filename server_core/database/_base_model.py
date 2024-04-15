from typing import Any, Dict

from sqlalchemy.orm import Session  # noqa
from sqlalchemy.orm import declarative_base

Base = declarative_base()


class DBBaseModel(Base):
    __abstract__ = True

    def to_dict(self) -> Dict[str, Any]:
        return {c.name: getattr(self, c.name) for c in self.__table__.columns}

    def add(self, session: Session, commit: bool = False) -> "DBBaseModel":
        session.add(self)
        if commit:
            session.commit()
        return self
