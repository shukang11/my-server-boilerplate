import logging

from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine, AsyncSession

from app.settings import settings

logger = logging.getLogger(__name__)

async_engine = create_async_engine(
    settings.SQLALCHEMY_DATABASE_URL,
    pool_pre_ping=True,
    echo=settings.ECHO_SQL,
)
AsyncSessionLocal = async_sessionmaker(
    bind=async_engine,
    class_=AsyncSession,
    autoflush=False,
    future=True,
)
