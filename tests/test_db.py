from dataclasses import asdict

from sqlalchemy import select

from api_todolist.models import User


def test_create_user(session, mock_db_time):
    # mock_db_time chama o prefix em configtest
    with mock_db_time(model=User) as time:
        new_user = User(username="test", email="test@test", password="secret")

        session.add(new_user)
        session.commit()

    # scalar vai trasformar em obj python o que vir do bd
    user = session.scalar(
        select(User).where(User.username == "test")  # select * from User
    )

    assert asdict(user) == {
        "id": 1,
        "username": "test",
        "email": "test@test",
        "password": "secret",
        "created_at": time,
    }
