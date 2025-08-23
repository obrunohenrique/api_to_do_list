from contextlib import contextmanager
from datetime import datetime

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine, event
from sqlalchemy.orm import Session

from api_todolist.app import app
from api_todolist.models import table_registry


@pytest.fixture
def client():
    return TestClient(app)


# arrange para preparar testes com o bd
@pytest.fixture
def session():
    # cria conecção com o bd(liga)
    engine = create_engine("sqlite:///:memory:")

    # cria no bd as tabelas que criamos
    table_registry.metadata.create_all(engine)

    # abre uma session de troca entre o bd e o código
    # 'olha me dá alguma coisa pra eu e o bd interagir'
    with Session(engine) as session:
        yield session

    table_registry.metadata.drop_all(engine)


# quando essa função é chamada o tempo já é setado por parametro
@contextmanager
def _mock_db_time(model, time=datetime(2025, 8, 22)):
    def fake_time_hook(mapper, connection, target):
        # se tiver o atributo -> seta o tempo mockado
        if hasattr(target, "created_at"):
            target.created_at = time

    # quando o teste vai inserir no bd, chama a função pra add o tempo mockado
    event.listen(model, "before_insert", fake_time_hook)

    # congela o tempo até que termine o escopo de with
    # ou seja, até que o bd seja populado com o dado mockado
    yield time

    # limpa tudo depois que encerra o teste
    event.remove(model, "before_insert", fake_time_hook)


# só serve de prefix pra chamar a função p/ mockar
@pytest.fixture
def mock_db_time():
    return _mock_db_time
