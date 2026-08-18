from http import HTTPStatus

from fastapi.testclient import TestClient

from forms_inventario.app import app


def test_root_read_retorna_ok():
    client = TestClient(app)

    response = client.get('/')

    assert response.status_code == HTTPStatus.OK
    assert response.json() == {'message': 'Ta funcionando!'}
