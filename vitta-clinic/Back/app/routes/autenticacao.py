"""Rotas de acesso, renovação, conta atual e cadastro de administrador."""

from flask import Blueprint
from flask_jwt_extended import create_access_token, create_refresh_token, get_jwt_identity, jwt_required
from sqlalchemy import func

from app.extensoes import db
from app.models import Usuario
from app.schemas.autenticacao import EsquemaLogin, EsquemaCriacaoUsuario
from app.services.comum import carregar_dados
from app.services.usuarios import criar_usuario
from app.utils.autenticacao import usuario_atual, perfis_obrigatorios
from app.utils.erros import ErroApi

bp = Blueprint("auth", __name__, url_prefix="/auth")


def _par_de_tokens(user):
    claims = {"role": user.role.value, "doctor_id": user.doctor.id if user.doctor else None}
    return {
        "access_token": create_access_token(identity=str(user.id), additional_claims=claims),
        "refresh_token": create_refresh_token(identity=str(user.id), additional_claims=claims),
        "user": user.para_dicionario(),
    }


@bp.post("/login")
def entrar():
    data = carregar_dados(EsquemaLogin())
    user = Usuario.query.filter(func.lower(Usuario.email) == data["email"].lower()).first()
    if user is None or not user.active or not user.verificar_senha(data["password"]):
        raise ErroApi("E-mail ou senha inválidos.", 401)
    return _par_de_tokens(user)


@bp.post("/refresh")
@jwt_required(refresh=True)
def atualizar_token():
    identity = get_jwt_identity()
    try:
        user = db.session.get(Usuario, int(identity))
    except (TypeError, ValueError):
        user = None
    if user is None or not user.active:
        raise ErroApi("Usuário inativo.", 401)
    return {"access_token": create_access_token(identity=str(user.id), additional_claims={"role": user.role.value, "doctor_id": user.doctor.id if user.doctor else None})}


@bp.get("/me")
@jwt_required()
def minha_conta():
    return {"user": usuario_atual().para_dicionario()}


@bp.post("/register")
@perfis_obrigatorios("admin")
def cadastrar():
    data = carregar_dados(EsquemaCriacaoUsuario())
    user = criar_usuario(data)
    return {"user": user.para_dicionario()}, 201
