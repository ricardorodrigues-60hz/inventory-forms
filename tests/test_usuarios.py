from http import HTTPStatus

import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_criar_usuario(client: AsyncClient, token_valido):
    response = await client.post(
        '/usuarios/',
        headers={'Authorization': f'Bearer {token_valido}'},
        json={
            'nome': 'Novo Usuario',
            'email': 'novo@teste.com',
            'senha': 'senhaforte',
            'ativo': True,
        },
    )
    assert response.status_code == HTTPStatus.CREATED
    assert response.json()['nome'] == 'Novo Usuario'
    assert 'id' in response.json()


@pytest.mark.asyncio
async def test_listar_usuarios(client: AsyncClient, token_valido):
    response = await client.get(
        '/usuarios/', headers={'Authorization': f'Bearer {token_valido}'}
    )
    assert response.status_code == HTTPStatus.OK
    assert len(response.json()) > 0
