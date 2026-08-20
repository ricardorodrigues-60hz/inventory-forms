from http import HTTPStatus

import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_criar_registro(client: AsyncClient, token_valido: str):
    response = await client.post(
        '/registros/',
        headers={'Authorization': f'Bearer {token_valido}'},
        json={
            'num_patrimonio': '123456',
            'setor': 'TI',
            'local_especifico': 'Sala Servidores',
            'tipo_maquina': 'MASTER',
            'registrado_em_dispositivo': '2024-01-01T10:00:00Z',
        },
    )
    assert response.status_code == HTTPStatus.CREATED
    assert response.json()['num_patrimonio'] == '123456'


@pytest.mark.asyncio
async def test_criar_registro_duplicado(client: AsyncClient, token_valido: str):
    payload = {
        'num_patrimonio': '123456',
        'setor': 'TI',
        'local_especifico': 'Sala Servidores',
        'tipo_maquina': 'MASTER',
        'registrado_em_dispositivo': '2024-01-01T10:00:00Z',
    }

    await client.post(
        '/registros/',
        headers={'Authorization': f'Bearer {token_valido}'},
        json=payload,
    )

    response = await client.post(
        '/registros/',
        headers={'Authorization': f'Bearer {token_valido}'},
        json=payload,
    )
    assert response.status_code == HTTPStatus.CONFLICT


@pytest.mark.asyncio
async def test_batch_registros(client: AsyncClient, token_valido: str):
    payloads = [
        {
            'num_patrimonio': 'B1',
            'setor': 'RH',
            'local_especifico': 'Sala 1',
            'tipo_maquina': 'SLIM',
            'registrado_em_dispositivo': '2024-01-01T10:00:00Z',
        },
        {
            'num_patrimonio': 'B2',
            'setor': 'RH',
            'local_especifico': 'Sala 1',
            'tipo_maquina': 'MASTER',
            'registrado_em_dispositivo': '2024-01-01T10:05:00Z',
        },
    ]

    response = await client.post(
        '/registros/batch',
        headers={'Authorization': f'Bearer {token_valido}'},
        json=payloads,
    )
    length_line = 2
    assert response.status_code == HTTPStatus.CREATED
    assert len(response.json()) == length_line


@pytest.mark.asyncio
async def test_buscar_registro_inexistente(client: AsyncClient, token_valido: str):
    response = await client.get(
        '/registros/00000000-0000-0000-0000-000000000000',
        headers={'Authorization': f'Bearer {token_valido}'},
    )
    assert response.status_code == HTTPStatus.NOT_FOUND
