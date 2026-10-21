"""Authentication and account schemas."""

from marshmallow import fields, validate

from app.extensions import EmptySchema


class LoginSchema(EmptySchema):
    email = fields.Email(required=True)
    password = fields.String(required=True, load_only=True)


class UserCreateSchema(EmptySchema):
    name = fields.String(required=True, validate=validate.Length(min=2, max=120))
    email = fields.Email(required=True)
    password = fields.String(required=True, load_only=True, validate=validate.Length(min=6, max=128))
    role = fields.String(required=True, validate=validate.OneOf(["admin", "medico", "recepcionista"]))


class UserUpdateSchema(EmptySchema):
    name = fields.String(validate=validate.Length(min=2, max=120))
    email = fields.Email()
    role = fields.String(validate=validate.OneOf(["admin", "medico", "recepcionista"]))
    active = fields.Boolean()
    password = fields.String(load_only=True, validate=validate.Length(min=6, max=128))
