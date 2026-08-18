import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_login_sucesso(client: AsyncClient, usuario_logado):
    response = await client.post(
        '/auth/login', json={'email': 'teste@teste.com', 'senha': '123456'}
    )
    assert response.status_code == 200
    assert 'access_token' in response.json()


@pytest.mark.asyncio
async def test_login_senha_incorreta(client: AsyncClient, usuario_logado):
    response = await client.post(
        '/auth/login', json={'email': 'teste@teste.com', 'senha': 'errada'}
    )
    assert response.status_code == 401


@pytest.mark.asyncio
async def test_me_com_token(client: AsyncClient, token_valido):
    response = await client.get(
        '/auth/me', headers={'Authorization': f'Bearer {token_valido}'}
    )
    assert response.status_code == 200
    assert response.json()['email'] == 'teste@teste.com'


@pytest.mark.asyncio
async def test_me_sem_token(client: AsyncClient):
    response = await client.get('/auth/me')
    assert response.status_code == 401
