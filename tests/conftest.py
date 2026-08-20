from contextlib import contextmanager
from datetime import datetime
from typing import AsyncGenerator

import factory
import pytest
import pytest_asyncio
from httpx import ASGITransport, AsyncClient
from sqlalchemy import event
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.pool import StaticPool

from forms_inventario.app import app
from forms_inventario.database import get_session, table_registry
from forms_inventario.models import Registro, Usuario
from forms_inventario.security import get_password_hash

SQLALCHEMY_DATABASE_URL = 'sqlite+aiosqlite:///:memory:'


@pytest_asyncio.fixture
async def session() -> AsyncGenerator[AsyncSession, None]:
    engine = create_async_engine(
        SQLALCHEMY_DATABASE_URL,
        connect_args={'check_same_thread': False},
        poolclass=StaticPool,
    )
    async with engine.begin() as conn:
        await conn.run_sync(table_registry.metadata.create_all)

    async with AsyncSession(engine, expire_on_commit=False) as session:
        yield session

    async with engine.begin() as conn:
        await conn.run_sync(table_registry.metadata.drop_all)


@pytest_asyncio.fixture
async def client(session: AsyncSession) -> AsyncGenerator[AsyncClient, None]:
    def get_session_override():
        return session

    async with AsyncClient(transport=ASGITransport(app=app), base_url='http://test') as ac:
        app.dependency_overrides[get_session] = get_session_override
        yield ac

    app.dependency_overrides.clear()


@contextmanager
def _mock_db_time(*, model, time=datetime(2025, 5, 20)):
    def fake_time_hook(mapper, connection, target):
        if hasattr(target, 'created_at'):
            target.created_at = time

        if hasattr(target, 'updated_at'):
            target.updated_at = time

    event.listen(model, 'before_insert', fake_time_hook)

    yield time

    event.remove(model, 'before_insert', fake_time_hook)


@pytest.fixture
def mock_db_time():
    return _mock_db_time


@pytest_asyncio.fixture
async def usuario(session: AsyncSession) -> Usuario:
    password = 'testest'
    user = UsuarioFactory(senha_hash=get_password_hash(password))
    session.add(user)
    await session.commit()
    await session.refresh(user)
    user.clean_password = password
    return user


@pytest_asyncio.fixture
async def outro_usuario(session: AsyncSession) -> Usuario:
    password = 'testest'
    user = UsuarioFactory(senha_hash=get_password_hash(password))
    session.add(user)
    await session.commit()
    await session.refresh(user)
    user.clean_password = password
    return user


@pytest_asyncio.fixture
async def token_valido(client: AsyncClient, usuario: Usuario) -> str:
    response = await client.post(
        '/auth/login',
        json={'email': usuario.email, 'senha': usuario.clean_password},
    )
    return response.json()['access_token']


class UsuarioFactory(factory.Factory):
    class Meta:
        model = Usuario

    nome = factory.Sequence(lambda n: f'usuario{n}')
    email = factory.LazyAttribute(lambda obj: f'{obj.nome}@test.com')
    senha_hash = factory.LazyAttribute(lambda obj: f'{obj.nome}@example.com')
    ativo = True


class RegistroFactory(factory.Factory):
    class Meta:
        model = Registro

    num_patrimonio = factory.Sequence(lambda n: f'PAT{n:06d}')
    setor = 'TI'
    local_especifico = 'Sala Servidores'
    tipo_maquina = 'MASTER'
    registrado_em_dispositivo = datetime(2025, 1, 1, 10, 0, 0)
