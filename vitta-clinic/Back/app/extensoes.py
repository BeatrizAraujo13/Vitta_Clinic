"""Extensões Flask compartilhadas, inicializadas pela fábrica da aplicação."""

from flask_bcrypt import Bcrypt
from flask_cors import CORS
from flask_jwt_extended import JWTManager
from flask_migrate import Migrate
from flask_sqlalchemy import SQLAlchemy
from marshmallow import Schema
from sqlalchemy.orm import DeclarativeBase


class BaseDeclarativa(DeclarativeBase):
    """Base declarativa dos modelos SQLAlchemy."""


db = SQLAlchemy(model_class=BaseDeclarativa)
migrate = Migrate()
jwt = JWTManager()
bcrypt = Bcrypt()
cors = CORS()


class EsquemaVazio(Schema):
    """Esquema base que rejeita campos desconhecidos nas requisições por padrão."""

    class Meta:
        unknown = "raise"
