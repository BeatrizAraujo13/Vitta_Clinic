"""Login, refresh, current account and administrator registration endpoints."""

from flask import Blueprint
from flask_jwt_extended import create_access_token, create_refresh_token, get_jwt_identity, jwt_required
from sqlalchemy import func

from app.extensions import db
from app.models import User
from app.schemas.auth import LoginSchema, UserCreateSchema
from app.services.common import load_payload
from app.services.users import create_user
from app.utils.auth import current_user, roles_required
from app.utils.errors import ApiError

bp = Blueprint("auth", __name__, url_prefix="/auth")


def _token_pair(user):
    claims = {"role": user.role.value, "doctor_id": user.doctor.id if user.doctor else None}
    return {
        "access_token": create_access_token(identity=str(user.id), additional_claims=claims),
        "refresh_token": create_refresh_token(identity=str(user.id), additional_claims=claims),
        "user": user.to_dict(),
    }


@bp.post("/login")
def login():
    data = load_payload(LoginSchema())
    user = User.query.filter(func.lower(User.email) == data["email"].lower()).first()
    if user is None or not user.active or not user.check_password(data["password"]):
        raise ApiError("E-mail ou senha inválidos.", 401)
    return _token_pair(user)


@bp.post("/refresh")
@jwt_required(refresh=True)
def refresh():
    identity = get_jwt_identity()
    try:
        user = db.session.get(User, int(identity))
    except (TypeError, ValueError):
        user = None
    if user is None or not user.active:
        raise ApiError("Usuário inativo.", 401)
    return {"access_token": create_access_token(identity=str(user.id), additional_claims={"role": user.role.value, "doctor_id": user.doctor.id if user.doctor else None})}


@bp.get("/me")
@jwt_required()
def me():
    return {"user": current_user().to_dict()}


@bp.post("/register")
@roles_required("admin")
def register():
    data = load_payload(UserCreateSchema())
    user = create_user(data)
    return {"user": user.to_dict()}, 201
