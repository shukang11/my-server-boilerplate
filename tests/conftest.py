import os

import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

os.environ["SQLALCHEMY_DATABASE_URL"] = "sqlite:///:memory:"

from server_api.main import create_app  # noqa: E402
# create all tables
from server_core.database import DBBaseModel  # noqa: E402
from server_core.database._session import SessionLocal, engine  # noqa: E402

# set SQLALCHEMY_DATABASE_URL to memory database
DBBaseModel.metadata.create_all(bind=engine)

app = create_app()


TEST_ADMIN_USERNAME = "test_admin"
TEST_ADMIN_PASSWORD = "test_admin"
TEST_ADMIN_PHONE = "12345678901"


@pytest.fixture
def admin_username() -> str:
    return TEST_ADMIN_USERNAME


@pytest.fixture
def admin_password() -> str:
    return TEST_ADMIN_PASSWORD


@pytest.fixture
def admin_phone() -> str:
    return TEST_ADMIN_PHONE


@pytest.fixture
def admin_id(session: Session, admin_username: str) -> int:
    from server_core.database import UserInDB

    session.query(UserInDB).filter_by(username=admin_username).first().id


@pytest.fixture
def session() -> Session:
    session = SessionLocal()
    return session


@pytest.fixture
def client() -> TestClient:
    # override the default environment variable

    client = TestClient(app)
    return client
