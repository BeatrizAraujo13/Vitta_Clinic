"""Aplicação Flask isolada e funções auxiliares de JWT para os testes da API."""

import pytest

from app import criar_aplicacao
from app.extensoes import db
from app.dados_iniciais import popular_banco


class ConfiguracaoTeste:
    TESTING = True
    SECRET_KEY = "test-secret-key-that-is-at-least-32-bytes"
    JWT_SECRET_KEY = "test-jwt-secret-key-that-is-at-least-32-bytes"
    DATA_ENCRYPTION_KEY = "AAECAwQFBgcICQoLDA0ODxAREhMUFRYXGBkaGxwdHh8="
    SQLALCHEMY_DATABASE_URI = "sqlite://"
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    CORS_ORIGINS = ["http://localhost"]
    JWT_ACCESS_TOKEN_EXPIRES = 300
    JWT_REFRESH_TOKEN_EXPIRES = 600


@pytest.fixture
def app():
    application = criar_aplicacao(ConfiguracaoTeste)
    with application.app_context():
        db.create_all()
        popular_banco()
        yield application
        db.session.remove()
        db.drop_all()


@pytest.fixture
def cliente_teste(app):
    return app.test_client()


@pytest.fixture
def tokens_teste(cliente_teste):
    def entrar(email="admin@vitta.com", password="123456"):
        response = cliente_teste.post("/api/v1/auth/login", json={"email": email, "password": password})
        assert response.status_code == 200
        return response.get_json()

    return entrar


@pytest.fixture
def cabecalho_autenticacao(tokens_teste):
    token_data = tokens_teste()
    return {"Authorization": f"Bearer {token_data['access_token']}"}
