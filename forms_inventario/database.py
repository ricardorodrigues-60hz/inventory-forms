from typing import AsyncGenerator

from sqlalchemy.ext.asyncio import (
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)
from sqlalchemy.orm import declarative_base

from forms_inventario.config import settings

engine_args = {}
if settings.database_url.startswith('postgresql'):
    engine_args = {'pool_size': 10, 'max_overflow': 20}

engine = create_async_engine(settings.database_url, echo=False, **engine_args)

async_session_maker = async_sessionmaker(
    engine, class_=AsyncSession, expire_on_commit=False
)

Base = declarative_base()


async def get_db() -> AsyncGenerator[AsyncSession, None]:

    async with async_session_maker() as session:
        yield session
