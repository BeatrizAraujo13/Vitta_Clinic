"""Esquemas de requisição de consultas."""

from marshmallow import fields, validate

from app.extensoes import EsquemaVazio


class EsquemaConsulta(EsquemaVazio):
    patient_id = fields.Integer(required=True)
    doctor_id = fields.Integer(required=True)
    date = fields.Date(required=True)
    time = fields.Time(required=True, format="%H:%M")
    status = fields.String(validate=validate.OneOf(["agendada", "realizada", "cancelada"]), load_default="agendada")
    notes = fields.String(allow_none=True)


class EsquemaAtualizacaoConsulta(EsquemaVazio):
    patient_id = fields.Integer()
    doctor_id = fields.Integer()
    date = fields.Date()
    time = fields.Time(format="%H:%M")
    status = fields.String(validate=validate.OneOf(["agendada", "realizada", "cancelada"]))
    notes = fields.String(allow_none=True)
