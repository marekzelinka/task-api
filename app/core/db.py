from sqlalchemy.ext.asyncio import AsyncAttrs, async_sessionmaker, create_async_engine
from sqlalchemy.orm import DeclarativeBase
from sqlmodel.ext.asyncio.session import AsyncSession

from app.core.config import config

engine = create_async_engine(
    str(config.sqlalchemy_database_uri), echo=True, connect_args={"ssl": True}
)
async_session = async_sessionmaker(
    bind=engine, class_=AsyncSession, expire_on_commit=False
)


class Base(AsyncAttrs, DeclarativeBase):
    pass
