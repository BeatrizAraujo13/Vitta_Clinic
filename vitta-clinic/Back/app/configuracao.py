"""Configuração da aplicação baseada em variáveis de ambiente."""

import os


class Configuracao:
    SECRET_KEY = os.getenv("SECRET_KEY", "dev-only-change-this-secret-key-32")
    JWT_SECRET_KEY = os.getenv("JWT_SECRET_KEY", "dev-only-change-this-jwt-secret-32")
    SQLALCHEMY_DATABASE_URI = os.getenv("DATABASE_URL", "sqlite:///vitta_clinic.db")
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    JWT_ACCESS_TOKEN_EXPIRES = 60 * 30
    JWT_REFRESH_TOKEN_EXPIRES = 60 * 60 * 24 * 30
    CORS_ORIGINS = [
        origin.strip()
        for origin in os.getenv(
            "CORS_ORIGINS", "http://localhost:5500,http://127.0.0.1:5500"
        ).split(",")
        if origin.strip()
    ]
