import os
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker

USER = os.getenv("POSTGRES_USER", "user")
PASSWORD = os.getenv("POSTGRES_PASSWORD", "password")
DATABASE = os.getenv("POSTGRES_DATABASE", "url_shortener")
HOST = os.getenv("POSTGRES_HOST", "postgres")
PORT = os.getenv("POSTGRES_PORT", "5432")
DATABASE_URL = f"postgresql+asyncpg://{USER}:{PASSWORD}@{HOST}:{PORT}/{DATABASE}"

engine = create_async_engine(DATABASE_URL, echo=False)
AsyncSessionLocal = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

__all__ = ["engine", "AsyncSessionLocal", "DATABASE_URL"]
