"""Operações de ciclo de vida de contas restritas a administradores."""

from sqlalchemy import func

from app.extensoes import db
from app.models import Usuario
from app.services.comum import confirmar_ou_reverter, obter_ou_404
from app.utils.erros import ErroApi


def listar_usuarios():
    return Usuario.query.order_by(Usuario.name).all()


def criar_usuario(data: dict) -> Usuario:
    email = data["email"].strip().lower()
    if Usuario.query.filter(func.lower(Usuario.email) == email).first():
        raise ErroApi("Já existe um usuário com este e-mail.", 409)
    user = Usuario(name=data["name"].strip(), email=email, role=data["role"])
    user.definir_senha(data["password"])
    db.session.add(user)
    confirmar_ou_reverter()
    return user


def atualizar_usuario(user_id: int, data: dict) -> Usuario:
    user = obter_ou_404(Usuario, user_id, "Usuário")
    if user.doctor and data.get("role", user.role.value) != "medico":
        raise ErroApi("Um usuário vinculado a um médico deve manter o perfil médico.", 409)
    if "email" in data:
        email = data["email"].strip().lower()
        duplicate = Usuario.query.filter(func.lower(Usuario.email) == email, Usuario.id != user.id).first()
        if duplicate:
            raise ErroApi("Já existe um usuário com este e-mail.", 409)
        user.email = email
    for field in ("name", "role", "active"):
        if field in data:
            setattr(user, field, data[field])
    if "password" in data:
        user.definir_senha(data["password"])
    confirmar_ou_reverter()
    return user


def excluir_usuario(user_id: int, usuario_atual: Usuario):
    user = obter_ou_404(Usuario, user_id, "Usuário")
    if usuario_atual.id == user.id:
        raise ErroApi("Não é possível excluir a própria conta autenticada.", 409)
    if user.doctor and user.doctor.appointments:
        user.active = False
        user.doctor.active = False
    else:
        if user.doctor:
            db.session.delete(user.doctor)
        db.session.delete(user)
    confirmar_ou_reverter()
