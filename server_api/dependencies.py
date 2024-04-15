from typing import Generator

from sqlalchemy.orm import Session

from server_core.database._session import SessionLocal


def get_session() -> Generator[Session, None, None]:
    session = SessionLocal()
    try:
        with session.no_autoflush:
            yield session
    finally:
        session.commit()
        session.close()
