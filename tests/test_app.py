from http import HTTPStatus


def test_read_root_deve_retornar_ok_e_ola_mundo(client):
    response = client.get("/")  # act (ação)

    assert response.status_code == HTTPStatus.OK  # assert (confirmação)
    assert response.json() == {"message": "olá, mundo"}


def test_create_user(client):
    response = client.post(
        "/users",
        json={
            "username": "alice",
            "email": "alice@gmail.com",
            "password": "secret",
        },
    )

    assert response.status_code == HTTPStatus.CREATED
    assert response.json() == {
        "id": 1,
        "email": "alice@gmail.com",
        "username": "alice",
    }


def test_read_users(client):
    response = client.get("/users")

    assert response.status_code == HTTPStatus.OK
    assert response.json() == {
        "users": [
            {"id": 1, "username": "alice", "email": "alice@gmail.com"},
        ]
    }


def test_read_user_for_id(client):
    response = client.get("users/1")

    assert response.status_code == HTTPStatus.OK
    assert response.json() == {
        "username": "alice",
        "email": "alice@gmail.com",
        "id": 1,
    }


def test_error_read_user_for_id(client):
    response = client.get("users/12")

    assert response.status_code == HTTPStatus.NOT_FOUND


def test_update_user(client):
    response = client.put(
        "/users/1",
        json={
            "username": "bob",
            "email": "bob@example.com",
            "password": "123",
        },
    )

    assert response.status_code == HTTPStatus.OK
    assert response.json() == {
        "username": "bob",
        "email": "bob@example.com",
        "id": 1,
    }


def test_error_not_id_update_user(client):
    response = client.put(
        "users/12",
        json={
            "username": "bob",
            "email": "bob@example.com",
            "password": "123",
        },
    )

    assert response.status_code == HTTPStatus.NOT_FOUND


def test_delete_user(client):
    response = client.delete("/users/1")

    assert response.status_code == HTTPStatus.OK
    assert response.json() == {
        "username": "bob",
        "email": "bob@example.com",
        "id": 1,
    }


def test_error_delete_user(client):
    response = client.delete("/users/12")

    assert response.status_code == HTTPStatus.NOT_FOUND
