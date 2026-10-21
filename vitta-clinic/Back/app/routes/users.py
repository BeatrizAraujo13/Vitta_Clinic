"""Administrator-only user endpoints."""

from flask import Blueprint

from app.schemas.auth import UserCreateSchema, UserUpdateSchema
from app.services.common import get_or_404, load_payload
from app.services.users import create_user, delete_user, list_users, update_user
from app.models import User
from app.utils.auth import current_user, roles_required

bp = Blueprint("users", __name__, url_prefix="/users")


@bp.get("")
@roles_required("admin")
def index():
    return {"items": [user.to_dict() for user in list_users()]}


@bp.post("")
@roles_required("admin")
def create():
    user = create_user(load_payload(UserCreateSchema()))
    return {"user": user.to_dict()}, 201


@bp.get("/<int:user_id>")
@roles_required("admin")
def show(user_id):
    return {"user": get_or_404(User, user_id, "Usuário").to_dict()}


@bp.patch("/<int:user_id>")
@roles_required("admin")
def update(user_id):
    user = update_user(user_id, load_payload(UserUpdateSchema(), partial=True))
    return {"user": user.to_dict()}


@bp.delete("/<int:user_id>")
@roles_required("admin")
def delete(user_id):
    delete_user(user_id, current_user())
    return {"deleted": True}, 200
