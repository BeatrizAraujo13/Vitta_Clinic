"""Esquemas de autenticação e conta."""

from marshmallow import fields, validate

from app.extensoes import EsquemaVazio


class EsquemaLogin(EsquemaVazio):
    email = fields.Email(required=True)
    password = fields.String(required=True, load_only=True)


class EsquemaCriacaoUsuario(EsquemaVazio):
    name = fields.String(required=True, validate=validate.Length(min=2, max=120))
    email = fields.Email(required=True)
    password = fields.String(required=True, load_only=True, validate=validate.Length(min=6, max=128))
    role = fields.String(required=True, validate=validate.OneOf(["admin", "medico", "recepcionista"]))


class EsquemaAtualizacaoUsuario(EsquemaVazio):
    name = fields.String(validate=validate.Length(min=2, max=120))
    email = fields.Email()
    role = fields.String(validate=validate.OneOf(["admin", "medico", "recepcionista"]))
    active = fields.Boolean()
    password = fields.String(load_only=True, validate=validate.Length(min=6, max=128))
