"""Rotas REST de médicos."""

from flask import Blueprint, request

from app.models import Medico
from app.schemas.medico import EsquemaMedico, EsquemaAtualizacaoMedico
from app.services.comum import obter_ou_404, carregar_dados
from app.services.medicos import excluir_medico, listar_medicos, salvar_medico
from app.utils.autenticacao import perfis_obrigatorios
from app.utils.erros import ErroApi

bp = Blueprint("doctors", __name__, url_prefix="/doctors")


@bp.get("")
@perfis_obrigatorios("admin", "medico", "recepcionista")
def listar():
    try:
        specialty_id = int(request.args["specialty_id"]) if request.args.get("specialty_id") else None
    except ValueError as error:
        raise ErroApi("specialty_id deve ser um número inteiro.", 400) from error
    items = listar_medicos(request.args.get("search"), specialty_id)
    return {"items": [doctor.para_dicionario() for doctor in items]}


@bp.post("")
@perfis_obrigatorios("admin")
def criar():
    doctor = salvar_medico(carregar_dados(EsquemaMedico()))
    return {"doctor": doctor.para_dicionario()}, 201


@bp.get("/<int:doctor_id>")
@perfis_obrigatorios("admin", "medico", "recepcionista")
def obter(doctor_id):
    return {"doctor": obter_ou_404(Medico, doctor_id, "Médico").para_dicionario()}


@bp.patch("/<int:doctor_id>")
@perfis_obrigatorios("admin")
def atualizar(doctor_id):
    data = carregar_dados(EsquemaAtualizacaoMedico(), partial=True)
    if not data:
        raise ErroApi("Informe ao menos um campo para atualizar.", 400)
    doctor = salvar_medico(data, obter_ou_404(Medico, doctor_id, "Médico"))
    return {"doctor": doctor.para_dicionario()}


@bp.delete("/<int:doctor_id>")
@perfis_obrigatorios("admin")
def excluir(doctor_id):
    return excluir_medico(doctor_id)
