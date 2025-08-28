from http import HTTPStatus

from jwt import decode

from api_todolist.security import ALGORITHM, SECRET_KEY, create_acess_token


def test_jwt():
    data = {"test": "test"}

    token = create_acess_token(data)

    decoded = decode(token, SECRET_KEY, ALGORITHM)

    assert decoded["test"] == data["test"]
    assert "exp" in decoded


def test_jwt_invalid_token(client):
    response = client.delete(
        "/users/1", headers={"Authorization": "Bearer token-invalido"}
    )

    assert response.status_code == HTTPStatus.UNAUTHORIZED
    assert response.json() == {"detail": "Usuário não autorizado."}
