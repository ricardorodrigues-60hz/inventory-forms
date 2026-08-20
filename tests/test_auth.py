from http import HTTPStatus

import pytest
from httpx import AsyncClient

from forms_inventario.models import Usuario


@pytest.mark.asyncio
async def test_login_sucesso(client: AsyncClient, usuario: Usuario):
    response = await client.post(
        '/auth/login',
        json={'email': usuario.email, 'senha': usuario.clean_password},
    )
    assert response.status_code == HTTPStatus.OK
    assert 'access_token' in response.json()


@pytest.mark.asyncio
async def test_login_senha_incorreta(client: AsyncClient, usuario: Usuario):
    response = await client.post('/auth/login', json={'email': usuario.email, 'senha': 'errada'})
    assert response.status_code == HTTPStatus.UNAUTHORIZED


@pytest.mark.asyncio
async def test_me_com_token(client: AsyncClient, token_valido: str, usuario: Usuario):
    response = await client.get('/auth/me', headers={'Authorization': f'Bearer {token_valido}'})
    assert response.status_code == HTTPStatus.OK
    assert response.json()['email'] == usuario.email


@pytest.mark.asyncio
async def test_me_sem_token(client: AsyncClient):
    response = await client.get('/auth/me')
    assert response.status_code == HTTPStatus.UNAUTHORIZED
