from http import HTTPStatus

from fastapi import Depends, FastAPI, HTTPException
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from api_todolist.database import get_session
from api_todolist.models import User
from api_todolist.schemas import (
    Message,
    Token,
    UserList,
    UserPublic,
    UserSchema,
)
from api_todolist.security import (
    create_acess_token,
    get_current_user,
    get_passwod_hash,
    verify_password,
)

app = FastAPI()


database = []


@app.get("/", status_code=HTTPStatus.OK, response_model=Message)
def read_root():
    return {"message": "olá, mundo"}


@app.post("/users", status_code=HTTPStatus.CREATED, response_model=UserPublic)
def create_user(
    user: UserSchema,
    session=Depends(get_session),
):
    db_user = session.scalar(
        select(User).where(
            (User.username == user.username) | (User.email == user.email)
        )
    )

    if db_user:
        if db_user.username == user.username:
            raise HTTPException(
                status_code=HTTPStatus.CONFLICT,
                detail="Já existe um usuário com esse nome.",
            )
        elif db_user.email == user.email:
            raise HTTPException(
                status_code=HTTPStatus.CONFLICT,
                detail="Já existe um usuário com esse email.",
            )

    db_user = User(
        username=user.username,
        email=user.email,
        password=get_passwod_hash(user.password),
    )

    session.add(db_user)
    session.commit()
    session.refresh(db_user)

    return db_user


@app.get("/users", status_code=HTTPStatus.OK, response_model=UserList)
def read_users(
    limit: int = 10,
    offset: int = 0,
    session: Session = Depends(get_session),
    current_user=Depends(get_current_user),
):
    users = session.scalars(select(User).limit(limit).offset(offset))
    return {"users": users}


@app.put(
    "/users/{user_id}", status_code=HTTPStatus.OK, response_model=UserPublic
)
def update_user(
    user: UserSchema,
    user_id: int,
    session: Session = Depends(get_session),
    current_user=Depends(get_current_user),
):
    if current_user.id != user_id:
        raise HTTPException(
            status_code=HTTPStatus.FORBIDDEN,
            detail="Você não possui permissão",
        )

    try:
        current_user.email = user.email
        current_user.username = user.username
        current_user.password = get_passwod_hash(user.password)

        session.add(current_user)
        session.commit()
        session.refresh(current_user)

        return current_user

    except IntegrityError:
        raise HTTPException(
            detail="Já existe usuário com essas credenciais",
            status_code=HTTPStatus.CONFLICT,
        )


@app.get(
    "/users/{user_id}", status_code=HTTPStatus.OK, response_model=UserPublic
)
def read_user_for_id(user_id: int, session: Session = Depends(get_session)):
    user_db = session.scalar(select(User).where(User.id == user_id))

    if not user_db:
        raise HTTPException(
            status_code=HTTPStatus.NOT_FOUND,
            detail="Não foi possível encontrar o usuário.",
        )

    return user_db


@app.delete(
    "/users/{user_id}", status_code=HTTPStatus.OK, response_model=Message
)
def delete_user(
    user_id: int,
    session: Session = Depends(get_session),
    current_user=Depends(get_current_user),
):
    if current_user.id != user_id:
        raise HTTPException(
            detail="sem autorização", status_code=HTTPStatus.FORBIDDEN
        )

    session.delete(current_user)
    session.commit()

    return {"message": "user deleted"}


@app.post("/token", response_model=Token)
def login_for_acess_token(
    form_data: OAuth2PasswordRequestForm = Depends(),
    session: Session = Depends(get_session),
):
    user = session.scalar(select(User).where(User.email == form_data.username))

    if not user:
        raise HTTPException(
            detail="Senha ou email incorretos.",
            status_code=HTTPStatus.UNAUTHORIZED,
        )

    if not verify_password(form_data.password, user.password):
        raise HTTPException(
            detail="Senha ou email incorretos.",
            status_code=HTTPStatus.UNAUTHORIZED,
        )

    acess_token = create_acess_token({"sub": user.email})
    return {"acess_token": acess_token, "token_type": "Bearer"}
