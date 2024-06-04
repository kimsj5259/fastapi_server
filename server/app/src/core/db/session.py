from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.asyncio import create_async_engine
from sqlmodel.ext.asyncio.session import AsyncSession

from ..config import settings


connect_args = {"check_same_thread": False}

engine = create_async_engine(
    settings.ASYNC_DATABASE_URI,
    # echo=True,
    future=True,
    pool_size=settings.POOL_SIZE,
    max_overflow=64,
)

SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False,
)
