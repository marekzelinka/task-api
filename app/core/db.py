from sqlalchemy.ext.asyncio import create_async_engine

from app.core.config import config

engine = create_async_engine(
    str(config.sqlalchemy_database_uri), echo=True, connect_args={"ssl": True}
)
