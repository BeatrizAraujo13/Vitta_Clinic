"""Shared Flask extensions, initialized by the application factory."""

from flask_bcrypt import Bcrypt
from flask_cors import CORS
from flask_jwt_extended import JWTManager
from flask_migrate import Migrate
from flask_sqlalchemy import SQLAlchemy
from marshmallow import Schema
from sqlalchemy.orm import DeclarativeBase


class Base(DeclarativeBase):
    """Declarative base for SQLAlchemy models."""


db = SQLAlchemy(model_class=Base)
migrate = Migrate()
jwt = JWTManager()
bcrypt = Bcrypt()
cors = CORS()


class EmptySchema(Schema):
    """Base schema that rejects unknown request fields by default."""

    class Meta:
        unknown = "raise"
