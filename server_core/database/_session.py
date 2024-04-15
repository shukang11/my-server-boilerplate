import os

from sqlalchemy import Engine, create_engine
from sqlalchemy.orm import sessionmaker

SQLALCHEMY_DATABASE_URL = os.getenv("SQLALCHEMY_DATABASE_URL")

if not SQLALCHEMY_DATABASE_URL:
    raise ValueError("SQLALCHEMY_DATABASE_URL must be set in environment")

engine: Engine

if SQLALCHEMY_DATABASE_URL.startswith("sqlite") and "memory" in SQLALCHEMY_DATABASE_URL:
    engine = create_engine(SQLALCHEMY_DATABASE_URL)
else:
    engine = create_engine(
        SQLALCHEMY_DATABASE_URL,
        max_overflow=10,
        pool_size=5,
        pool_timeout=30,
        pool_recycle=3600,
    )
SessionLocal = sessionmaker(autocommit=False, autoflush=True, bind=engine)
