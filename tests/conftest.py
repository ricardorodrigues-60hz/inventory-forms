import asyncio
from typing import AsyncGenerator

import pytest
import pytest_asyncio
from httpx import ASGITransport, AsyncClient
from sqlalchemy.ext.asyncio import (
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)
from sqlalchemy.pool import StaticPool

from forms_inventario.app import app
from forms_inventario.database import Base, get_db
from forms_inventario.models import Usuario
from forms_inventario.security import get_password_hash

# Banco em memoria para os testes
SQLALCHEMY_DATABASE_URL = 'sqlite+aiosqlite:///:memory:'

engine = create_async_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={'check_same_thread': False},
    poolclass=StaticPool,
)

TestingSessionLocal = async_sessionmaker(
    autocommit=False, autoflush=False, bind=engine, class_=AsyncSession
)


async def override_get_db() -> AsyncGenerator[AsyncSession, None]:
    async with TestingSessionLocal() as session:
        yield session


app.dependency_overrides[get_db] = override_get_db


@pytest.fixture(scope='session')
def event_loop():
    """Create an instance of the default event loop for each test case."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest_asyncio.fixture(autouse=True)
async def setup_db():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)


@pytest_asyncio.fixture
async def db_session() -> AsyncGenerator[AsyncSession, None]:
    async with TestingSessionLocal() as session:
        yield session


@pytest_asyncio.fixture
async def client() -> AsyncGenerator[AsyncClient, None]:
    async with AsyncClient(
        transport=ASGITransport(app=app), base_url='http://test'
    ) as ac:
        yield ac


@pytest_asyncio.fixture
async def usuario_logado(db_session: AsyncSession) -> Usuario:
    user = Usuario(
        nome='Teste',
        email='teste@teste.com',
        senha_hash=get_password_hash('123456'),
        ativo=True,
    )
    db_session.add(user)
    await db_session.commit()
    await db_session.refresh(user)
    return user


@pytest_asyncio.fixture
async def token_valido(client: AsyncClient, usuario_logado: Usuario) -> str:
    response = await client.post(
        '/auth/login', json={'email': 'teste@teste.com', 'senha': '123456'}
    )
    return response.json()['access_token']
