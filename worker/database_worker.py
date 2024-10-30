from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

import config

db_url = config.settings.DATABASE_URL_asyncpg

async_engine = create_async_engine(
    url=db_url,
    echo=True,
    pool_size=10,
    max_overflow=10,
)

async_session = async_sessionmaker(
    bind=async_engine,
    autoflush=False,
    autocommit=False,
    expire_on_commit=False,
    class_=AsyncSession,
)
