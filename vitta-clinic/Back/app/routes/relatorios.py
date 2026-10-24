"""Relatórios restritos a administradores."""

from datetime import date

from flask import Blueprint, request

from app.services.relatorios import relatorio_consultas, relatorio_medicos, relatorio_pacientes
from app.utils.autenticacao import perfis_obrigatorios
from app.utils.erros import ErroApi

bp = Blueprint("reports", __name__, url_prefix="/reports")


def _data_consultada(name):
    value = request.args.get(name)
    if not value:
        return None
    try:
        return date.fromisoformat(value)
    except ValueError as error:
        raise ErroApi(f"{name} deve estar no formato AAAA-MM-DD.", 400) from error


@bp.get("/appointments")
@perfis_obrigatorios("admin")
def consultas():
    doctor_id = request.args.get("doctor_id")
    try:
        doctor_id = int(doctor_id) if doctor_id else None
    except ValueError as error:
        raise ErroApi("doctor_id deve ser um número inteiro.", 400) from error
    items = relatorio_consultas(_data_consultada("date_from"), _data_consultada("date_to"), doctor_id)
    return {"items": items, "count": len(items)}


@bp.get("/patients")
@perfis_obrigatorios("admin")
def pacientes():
    items = relatorio_pacientes()
    return {"items": items, "count": len(items)}


@bp.get("/doctors")
@perfis_obrigatorios("admin")
def medicos():
    items = relatorio_medicos(_data_consultada("date_from"), _data_consultada("date_to"))
    return {"items": items, "count": len(items)}
