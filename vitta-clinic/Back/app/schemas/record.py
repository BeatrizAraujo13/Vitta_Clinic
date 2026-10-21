"""Electronic medical record request schemas."""

from marshmallow import fields, validate

from app.extensions import EmptySchema


class MedicalRecordSchema(EmptySchema):
    appointment_id = fields.Integer(required=True)
    record_date = fields.Date(required=True)
    complaint = fields.String(required=True, validate=validate.Length(min=2))
    diagnosis = fields.String(required=True, validate=validate.Length(min=2))
    prescription = fields.String(allow_none=True)
    notes = fields.String(allow_none=True)


class MedicalRecordUpdateSchema(EmptySchema):
    appointment_id = fields.Integer()
    record_date = fields.Date()
    complaint = fields.String(validate=validate.Length(min=2))
    diagnosis = fields.String(validate=validate.Length(min=2))
    prescription = fields.String(allow_none=True)
    notes = fields.String(allow_none=True)
