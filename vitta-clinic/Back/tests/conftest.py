"""Shared isolated Flask application and JWT helpers for API tests."""

import pytest

from app import create_app
from app.extensions import db
from app.seed import seed_database


class TestConfig:
    TESTING = True
    SECRET_KEY = "test-secret-key-that-is-at-least-32-bytes"
    JWT_SECRET_KEY = "test-jwt-secret-key-that-is-at-least-32-bytes"
    SQLALCHEMY_DATABASE_URI = "sqlite://"
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    CORS_ORIGINS = ["http://localhost"]
    JWT_ACCESS_TOKEN_EXPIRES = 300
    JWT_REFRESH_TOKEN_EXPIRES = 600


@pytest.fixture
def app():
    application = create_app(TestConfig)
    with application.app_context():
        db.create_all()
        seed_database()
        yield application
        db.session.remove()
        db.drop_all()


@pytest.fixture
def client(app):
    return app.test_client()


@pytest.fixture
def tokens(client):
    def login(email="admin@vitta.com", password="123456"):
        response = client.post("/api/v1/auth/login", json={"email": email, "password": password})
        assert response.status_code == 200
        return response.get_json()

    return login


@pytest.fixture
def auth_header(tokens):
    token_data = tokens()
    return {"Authorization": f"Bearer {token_data['access_token']}"}
