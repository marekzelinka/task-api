from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine
from sqlmodel.ext.asyncio.session import AsyncSession

from app.core.config import config

engine = create_async_engine(
    str(config.sqlalchemy_database_uri), echo=True, connect_args={"ssl": True}
)
async_session = async_sessionmaker(
    bind=engine, class_=AsyncSession, expire_on_commit=False
)
