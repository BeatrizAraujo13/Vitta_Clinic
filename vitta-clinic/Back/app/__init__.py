"""Flask application factory for the Vitta Clinic API."""

import os

import click
from flask import Flask

from app.config import Config
from app.extensions import bcrypt, cors, db, jwt, migrate
from app.utils.errors import register_error_handlers


def create_app(config_object=Config):
    app = Flask(__name__)
    app.config.from_object(config_object)
    os.makedirs(app.instance_path, exist_ok=True)

    db.init_app(app)
    migrate.init_app(app, db)
    jwt.init_app(app)
    bcrypt.init_app(app)
    cors.init_app(
        app,
        resources={r"/api/*": {"origins": app.config["CORS_ORIGINS"]}},
        supports_credentials=False,
    )
    register_error_handlers(app)

    from app import models  # noqa: F401
    from app.routes import api_v1

    app.register_blueprint(api_v1)

    @app.get("/health")
    def health():
        return {"status": "ok", "service": "vitta-clinic-api"}

    @app.cli.command("seed")
    def seed_command():
        """Create the development seed data (tables are created if needed)."""
        db.create_all()
        from app.seed import seed_database

        if seed_database():
            click.echo("Dados de demonstração criados.")
        else:
            click.echo("O banco já possui usuários; seed não alterou os dados.")

    @jwt.unauthorized_loader
    def missing_token(_reason):
        return {"error": "Token JWT obrigatório."}, 401

    @jwt.invalid_token_loader
    def invalid_token(_reason):
        return {"error": "Token JWT inválido."}, 401

    @jwt.expired_token_loader
    def expired_token(_header, _payload):
        return {"error": "Token JWT expirado."}, 401

    @jwt.needs_fresh_token_loader
    def fresh_token_required(_header, _payload):
        return {"error": "É necessário um token JWT atualizado."}, 401

    return app
