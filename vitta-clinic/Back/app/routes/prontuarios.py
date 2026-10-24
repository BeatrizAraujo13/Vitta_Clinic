"""Rotas REST de prontuários."""

from flask import Blueprint, request

from app.models import Prontuario
from app.schemas.prontuario import EsquemaProntuario, EsquemaAtualizacaoProntuario
from app.services.comum import obter_ou_404, carregar_dados
from app.services.prontuarios import criar_prontuario, excluir_prontuario, listar_prontuarios, atualizar_prontuario
from app.utils.autenticacao import usuario_atual, perfis_obrigatorios
from app.utils.erros import ErroApi

bp = Blueprint("records", __name__, url_prefix="/records")


@bp.get("")
@perfis_obrigatorios("admin", "medico")
def listar():
    patient_id = request.args.get("patient_id")
    try:
        patient_id = int(patient_id) if patient_id else None
    except ValueError as error:
        raise ErroApi("patient_id deve ser um número inteiro.", 400) from error
    return {"items": [record.para_dicionario() for record in listar_prontuarios(usuario_atual(), patient_id)]}


@bp.post("")
@perfis_obrigatorios("admin", "medico")
def criar():
    record = criar_prontuario(carregar_dados(EsquemaProntuario()), usuario_atual())
    return {"record": record.para_dicionario()}, 201


@bp.get("/<int:record_id>")
@perfis_obrigatorios("admin", "medico")
def obter(record_id):
    record = obter_ou_404(Prontuario, record_id, "Prontuário")
    user = usuario_atual()
    if user.role.value == "medico" and (not user.doctor or record.doctor_id != user.doctor.id):
        raise ErroApi("Prontuário não encontrado.", 404)
    return {"record": record.para_dicionario()}


@bp.patch("/<int:record_id>")
@perfis_obrigatorios("admin", "medico")
def atualizar(record_id):
    data = carregar_dados(EsquemaAtualizacaoProntuario(), partial=True)
    if not data:
        raise ErroApi("Informe ao menos um campo para atualizar.", 400)
    record = atualizar_prontuario(record_id, data, usuario_atual())
    return {"record": record.para_dicionario()}


@bp.delete("/<int:record_id>")
@perfis_obrigatorios("admin", "medico")
def excluir(record_id):
    excluir_prontuario(record_id, usuario_atual())
    return {"deleted": True}
