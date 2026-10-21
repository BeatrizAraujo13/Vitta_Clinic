"""Reusable service-level request and entity helpers."""

from flask import request
from marshmallow import Schema

from app.utils.errors import ApiError


def load_payload(schema: Schema, *, partial: bool = False):
    payload = request.get_json(silent=False)
    if not isinstance(payload, dict):
        raise ApiError("O corpo da requisição deve ser um objeto JSON.", 400)
    return schema.load(payload, partial=partial)


def get_or_404(model, entity_id: int, label: str | None = None):
    from app.extensions import db

    entity = db.session.get(model, entity_id)
    if entity is None:
        raise ApiError(f"{label or model.__name__} não encontrado(a).", 404)
    return entity


def commit_or_rollback():
    from sqlalchemy.exc import IntegrityError

    from app.extensions import db

    try:
        db.session.commit()
    except IntegrityError as error:
        db.session.rollback()
        raise ApiError("Registro duplicado ou relacionamento inválido.", 409) from error
