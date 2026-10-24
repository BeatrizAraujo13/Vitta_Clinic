"""Rotas REST de especialidades restritas a administradores."""

from flask import Blueprint

from app.models import Especialidade
from app.schemas.medico import EsquemaEspecialidade, EsquemaAtualizacaoEspecialidade
from app.services.comum import obter_ou_404, carregar_dados
from app.services.medicos import excluir_especialidade, listar_especialidades, salvar_especialidade
from app.utils.autenticacao import perfis_obrigatorios
from app.utils.erros import ErroApi

bp = Blueprint("specialties", __name__, url_prefix="/specialties")


@bp.get("")
@perfis_obrigatorios("admin")
def listar():
    return {"items": [specialty.para_dicionario() for specialty in listar_especialidades()]}


@bp.post("")
@perfis_obrigatorios("admin")
def criar():
    specialty = salvar_especialidade(carregar_dados(EsquemaEspecialidade()))
    return {"specialty": specialty.para_dicionario()}, 201


@bp.get("/<int:specialty_id>")
@perfis_obrigatorios("admin")
def obter(specialty_id):
    return {"specialty": obter_ou_404(Especialidade, specialty_id, "Especialidade").para_dicionario()}


@bp.patch("/<int:specialty_id>")
@perfis_obrigatorios("admin")
def atualizar(specialty_id):
    data = carregar_dados(EsquemaAtualizacaoEspecialidade(), partial=True)
    if not data:
        raise ErroApi("Informe ao menos um campo para atualizar.", 400)
    specialty = salvar_especialidade(data, obter_ou_404(Especialidade, specialty_id, "Especialidade"))
    return {"specialty": specialty.para_dicionario()}


@bp.delete("/<int:specialty_id>")
@perfis_obrigatorios("admin")
def excluir(specialty_id):
    excluir_especialidade(specialty_id)
    return {"deleted": True}
