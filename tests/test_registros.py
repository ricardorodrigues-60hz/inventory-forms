from http import HTTPStatus

import pytest
from httpx import AsyncClient


@pytest.fixture
def registro_payload():
    return {
        'num_patrimonio': '123456',
        'setor': 'TI',
        'local_especifico': 'Sala Servidores',
        'tipo_maquina': 'MASTER',
        'registrado_em_dispositivo': '2024-01-01T10:00:00Z',
    }


@pytest.mark.asyncio
async def test_criar_registro(
    client: AsyncClient, token_valido, registro_payload
):
    response = await client.post(
        '/registros/',
        headers={'Authorization': f'Bearer {token_valido}'},
        json=registro_payload,
    )
    assert response.status_code == HTTPStatus.CREATED
    assert response.json()['num_patrimonio'] == '123456'


@pytest.mark.asyncio
async def test_criar_registro_duplicado(
    client: AsyncClient, token_valido, registro_payload
):
    # Primeiro insert
    await client.post(
        '/registros/',
        headers={'Authorization': f'Bearer {token_valido}'},
        json=registro_payload,
    )

    # Segundo insert (duplicado)
    response = await client.post(
        '/registros/',
        headers={'Authorization': f'Bearer {token_valido}'},
        json=registro_payload,
    )
    assert response.status_code == HTTPStatus.CONFLICT


@pytest.mark.asyncio
async def test_batch_registros(client: AsyncClient, token_valido):
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
    assert response.status_code == HTTPStatus.CREATED
    assert len(response.json()) == 2
