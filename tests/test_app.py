from http import HTTPStatus

from fastapi.testclient import TestClient

from api_todolist.app import app


def test_read_root_deve_retornar_ok_e_ola_mundo():
    client = TestClient(app)  # arrange(organização)

    response = client.get("/")  # act (ação)

    assert response.status_code == HTTPStatus.OK  # assert (confirmação)
    assert response.json() == {"message": "olá, mundo"}
