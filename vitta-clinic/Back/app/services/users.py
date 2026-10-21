"""Administrator-only account lifecycle operations."""

from sqlalchemy import func

from app.extensions import db
from app.models import User
from app.services.common import commit_or_rollback, get_or_404
from app.utils.errors import ApiError


def list_users():
    return User.query.order_by(User.name).all()


def create_user(data: dict) -> User:
    email = data["email"].strip().lower()
    if User.query.filter(func.lower(User.email) == email).first():
        raise ApiError("Já existe um usuário com este e-mail.", 409)
    user = User(name=data["name"].strip(), email=email, role=data["role"])
    user.set_password(data["password"])
    db.session.add(user)
    commit_or_rollback()
    return user


def update_user(user_id: int, data: dict) -> User:
    user = get_or_404(User, user_id, "Usuário")
    if user.doctor and data.get("role", user.role.value) != "medico":
        raise ApiError("Um usuário vinculado a um médico deve manter o perfil médico.", 409)
    if "email" in data:
        email = data["email"].strip().lower()
        duplicate = User.query.filter(func.lower(User.email) == email, User.id != user.id).first()
        if duplicate:
            raise ApiError("Já existe um usuário com este e-mail.", 409)
        user.email = email
    for field in ("name", "role", "active"):
        if field in data:
            setattr(user, field, data[field])
    if "password" in data:
        user.set_password(data["password"])
    commit_or_rollback()
    return user


def delete_user(user_id: int, current_user: User):
    user = get_or_404(User, user_id, "Usuário")
    if current_user.id == user.id:
        raise ApiError("Não é possível excluir a própria conta autenticada.", 409)
    if user.doctor and user.doctor.appointments:
        user.active = False
        user.doctor.active = False
    else:
        if user.doctor:
            db.session.delete(user.doctor)
        db.session.delete(user)
    commit_or_rollback()
