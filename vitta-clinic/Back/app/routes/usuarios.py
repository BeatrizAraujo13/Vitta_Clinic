"""Rotas de usuários restritas a administradores."""

from flask import Blueprint

from app.schemas.autenticacao import EsquemaCriacaoUsuario, EsquemaAtualizacaoUsuario
from app.services.comum import obter_ou_404, carregar_dados
from app.services.usuarios import criar_usuario, excluir_usuario, listar_usuarios, atualizar_usuario
from app.models import Usuario
from app.utils.autenticacao import usuario_atual, perfis_obrigatorios

bp = Blueprint("users", __name__, url_prefix="/users")


@bp.get("")
@perfis_obrigatorios("admin")
def listar():
    return {"items": [user.para_dicionario() for user in listar_usuarios()]}


@bp.post("")
@perfis_obrigatorios("admin")
def criar():
    user = criar_usuario(carregar_dados(EsquemaCriacaoUsuario()))
    return {"user": user.para_dicionario()}, 201


@bp.get("/<int:user_id>")
@perfis_obrigatorios("admin")
def obter(user_id):
    return {"user": obter_ou_404(Usuario, user_id, "Usuário").para_dicionario()}


@bp.patch("/<int:user_id>")
@perfis_obrigatorios("admin")
def atualizar(user_id):
    user = atualizar_usuario(user_id, carregar_dados(EsquemaAtualizacaoUsuario(), partial=True))
    return {"user": user.para_dicionario()}


@bp.delete("/<int:user_id>")
@perfis_obrigatorios("admin")
def excluir(user_id):
    excluir_usuario(user_id, usuario_atual())
    return {"deleted": True}, 200
