"""Esquemas de médicos e especialidades."""

from marshmallow import fields, validate

from app.extensoes import EsquemaVazio


class EsquemaMedico(EsquemaVazio):
    user_id = fields.Integer(allow_none=True)
    specialty_id = fields.Integer(required=True)
    name = fields.String(required=True, validate=validate.Length(min=2, max=160))
    crm = fields.String(required=True, validate=validate.Length(min=6, max=20))
    email = fields.Email(required=True)
    phone = fields.String(required=True, validate=validate.Length(min=8, max=32))
    schedule = fields.String(allow_none=True, validate=validate.Length(max=200))
    active = fields.Boolean(load_default=True)


class EsquemaAtualizacaoMedico(EsquemaVazio):
    user_id = fields.Integer(allow_none=True)
    specialty_id = fields.Integer()
    name = fields.String(validate=validate.Length(min=2, max=160))
    crm = fields.String(validate=validate.Length(min=6, max=20))
    email = fields.Email()
    phone = fields.String(validate=validate.Length(min=8, max=32))
    schedule = fields.String(allow_none=True, validate=validate.Length(max=200))
    active = fields.Boolean()


class EsquemaEspecialidade(EsquemaVazio):
    name = fields.String(required=True, validate=validate.Length(min=2, max=100))
    description = fields.String(allow_none=True)


class EsquemaAtualizacaoEspecialidade(EsquemaVazio):
    name = fields.String(validate=validate.Length(min=2, max=100))
    description = fields.String(allow_none=True)
