from typing import AsyncGenerator

from sqlalchemy.ext.asyncio import (
    AsyncSession,
    create_async_engine,
)

from forms_inventario.settings import Settings

engine_args = {}
if Settings().DATABASE_URL.startswith('postgresql'):
    engine_args = {'pool_size': 10, 'max_overflow': 20}

engine = create_async_engine(Settings().DATABASE_URL, echo=False, **engine_args)

async def get_session():
    async with AsyncSession(engine, expire_on_commit=False) as session:
        yield session