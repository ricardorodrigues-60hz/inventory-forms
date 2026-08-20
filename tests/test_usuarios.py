from http import HTTPStatus

import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_criar_usuario(client: AsyncClient, token_valido: str):
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
async def test_listar_usuarios(client: AsyncClient, token_valido: str):
    response = await client.get('/usuarios/', headers={'Authorization': f'Bearer {token_valido}'})
    assert response.status_code == HTTPStatus.OK
    assert len(response.json()) > 0


@pytest.mark.asyncio
async def test_criar_usuario_email_duplicado(client: AsyncClient, token_valido: str, usuario):
    response = await client.post(
        '/usuarios/',
        headers={'Authorization': f'Bearer {token_valido}'},
        json={
            'nome': 'Outro Nome',
            'email': usuario.email,
            'senha': 'senhaforte',
            'ativo': True,
        },
    )
    assert response.status_code == HTTPStatus.CONFLICT
    assert response.json() == {'detail': 'Email ja cadastrado'}


@pytest.mark.asyncio
async def test_buscar_usuario_inexistente(client: AsyncClient, token_valido: str):
    response = await client.get(
        '/usuarios/00000000-0000-0000-0000-000000000000',
        headers={'Authorization': f'Bearer {token_valido}'},
    )
    assert response.status_code == HTTPStatus.NOT_FOUND
