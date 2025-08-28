from http import HTTPStatus

from api_todolist.schemas import UserPublic


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


def test_error_create_user_conflict_username(client, user):
    response = client.post(
        "/users",
        json={
            "username": "test",
            "email": "test123@gmail.com",
            "password": "testest",
        },
    )

    assert response.status_code == HTTPStatus.CONFLICT


def test_error_create_user_conflict_email(client, user):
    response = client.post(
        "/users",
        json={
            "username": "test123",
            "email": "test@gmail.com",
            "password": "testest",
        },
    )

    assert response.status_code == HTTPStatus.CONFLICT


def test_read_users_with_user(client, user, token):
    user_schema = UserPublic.model_validate(user).model_dump()

    response = client.get(
        "/users",
        headers={"Authorization": f"Bearer {token}"},
    )

    assert response.status_code == HTTPStatus.OK
    assert response.json() == {"users": [user_schema]}


def test_read_user_for_id(client, user):
    user_schema = UserPublic.model_validate(user).model_dump()
    response = client.get("users/1")

    assert response.status_code == HTTPStatus.OK
    assert response.json() == user_schema


def test_error_read_user_for_id(client):
    response = client.get("users/12")

    assert response.status_code == HTTPStatus.NOT_FOUND


def test_update_user(client, user, token):
    response = client.put(
        "/users/1",
        json={
            "username": "bob",
            "email": "bob@example.com",
            "password": "123",
        },
        headers={"Authorization": f"Bearer {token}"},
    )

    assert response.status_code == HTTPStatus.OK
    assert response.json() == {
        "username": "bob",
        "email": "bob@example.com",
        "id": 1,
    }


def test_error_intregrity_update_user(client, user, token):
    client.post(
        "/users",
        json={
            "username": "bob",
            "email": "bob@example.com",
            "password": "123",
        },
    )

    response_update = client.put(
        "users/1",
        json={
            "username": "bob",
            "email": "bob@example.com",
            "password": "123",
        },
        headers={"Authorization": f"Bearer {token}"},
    )

    assert response_update.status_code == HTTPStatus.CONFLICT


def test_delete_user(client, user, token):
    response = client.delete(
        f"/users/{user.id}", headers={"Authorization": f"Bearer {token}"}
    )

    assert response.status_code == HTTPStatus.OK
    assert response.json() == {"message": "user deleted"}


def test_error_delete_user(client, token):
    response = client.delete(
        "/users/12", headers={"Authorization": f"Bearer {token}"}
    )

    assert response.status_code == HTTPStatus.FORBIDDEN


def test_get_token(client, user):
    response = client.post(
        "/token",
        data={"username": user.email, "password": user.clean_password},
    )

    token = response.json()

    assert response.status_code == HTTPStatus.OK
    assert token["token_type"] == "Bearer"
    assert "acess_token" in token
