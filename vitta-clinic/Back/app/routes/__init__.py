"""Blueprints versionados da API."""

from flask import Blueprint

api_v1 = Blueprint("api_v1", __name__, url_prefix="/api/v1")

from app.routes import (  # noqa: E402,F401
    autenticacao,
    consultas,
    especialidades,
    medicos,
    pacientes,
    prontuarios,
    relatorios,
    usuarios,
)

api_v1.register_blueprint(autenticacao.bp)
api_v1.register_blueprint(usuarios.bp)
api_v1.register_blueprint(pacientes.bp)
api_v1.register_blueprint(medicos.bp)
api_v1.register_blueprint(especialidades.bp)
api_v1.register_blueprint(consultas.bp)
api_v1.register_blueprint(prontuarios.bp)
api_v1.register_blueprint(relatorios.bp)
