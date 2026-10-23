"""Funções reutilizáveis de requisição e entidade na camada de serviços."""

from flask import request
from marshmallow import Schema

from app.utils.erros import ErroApi


def carregar_dados(schema: Schema, *, partial: bool = False):
    payload = request.get_json(silent=False)
    if not isinstance(payload, dict):
        raise ErroApi("O corpo da requisição deve ser um objeto JSON.", 400)
    return schema.load(payload, partial=partial)


def obter_ou_404(model, entity_id: int, label: str | None = None):
    from app.extensoes import db

    entity = db.session.get(model, entity_id)
    if entity is None:
        raise ErroApi(f"{label or model.__name__} não encontrado(a).", 404)
    return entity


def confirmar_ou_reverter():
    from sqlalchemy.exc import IntegrityError

    from app.extensoes import db

    try:
        db.session.commit()
    except IntegrityError as error:
        db.session.rollback()
        raise ErroApi("Registro duplicado ou relacionamento inválido.", 409) from error
