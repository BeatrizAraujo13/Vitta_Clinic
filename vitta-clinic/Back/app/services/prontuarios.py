"""Regras de prontuários e autorização médica."""

from datetime import date

from app.extensoes import db
from app.models import Consulta, StatusConsulta, Prontuario, PerfilUsuario
from app.services.comum import confirmar_ou_reverter, obter_ou_404
from app.utils.erros import ErroApi


def listar_prontuarios(user, patient_id=None):
    query = Prontuario.query
    if user.role == PerfilUsuario.MEDICO:
        if not user.doctor:
            return []
        query = query.filter_by(doctor_id=user.doctor.id)
    if patient_id:
        query = query.filter_by(patient_id=patient_id)
    return query.order_by(Prontuario.record_date.desc(), Prontuario.id.desc()).all()


def _validar_consulta(appointment: Consulta, user):
    if appointment.status != StatusConsulta.REALIZADA:
        raise ErroApi("O prontuário só pode ser criado em uma consulta realizada.", 409)
    if user.role == PerfilUsuario.MEDICO and (not user.doctor or user.doctor.id != appointment.doctor_id):
        raise ErroApi("Médicos só podem acessar prontuários de suas próprias consultas.", 403)


def criar_prontuario(data: dict, user) -> Prontuario:
    appointment = obter_ou_404(Consulta, data["appointment_id"], "Consulta")
    _validar_consulta(appointment, user)
    if data["record_date"] > date.today():
        raise ErroApi("A data do prontuário não pode estar no futuro.", 400)
    if appointment.record:
        raise ErroApi("Já existe um prontuário para esta consulta.", 409)
    record = Prontuario(
        patient_id=appointment.patient_id,
        appointment=appointment,
        doctor_id=appointment.doctor_id,
        record_date=data["record_date"],
        complaint=data["complaint"],
        diagnosis=data["diagnosis"],
        prescription=data.get("prescription"),
        notes=data.get("notes"),
    )
    db.session.add(record)
    confirmar_ou_reverter()
    return record


def atualizar_prontuario(record_id: int, data: dict, user) -> Prontuario:
    record = obter_ou_404(Prontuario, record_id, "Prontuário")
    if user.role == PerfilUsuario.MEDICO and (not user.doctor or record.doctor_id != user.doctor.id):
        raise ErroApi("Médicos só podem editar seus próprios prontuários.", 403)
    appointment_id = data.get("appointment_id", record.appointment_id)
    appointment = obter_ou_404(Consulta, appointment_id, "Consulta")
    _validar_consulta(appointment, user)
    if data.get("record_date", record.record_date) > date.today():
        raise ErroApi("A data do prontuário não pode estar no futuro.", 400)
    duplicate = Prontuario.query.filter_by(appointment_id=appointment.id).first()
    if duplicate and duplicate.id != record.id:
        raise ErroApi("Já existe um prontuário para esta consulta.", 409)
    if appointment.patient_id != record.patient_id:
        raise ErroApi("O prontuário não pode ser movido para outro paciente.", 409)
    record.appointment = appointment
    record.doctor_id = appointment.doctor_id
    for field in ("record_date", "complaint", "diagnosis", "prescription", "notes"):
        if field in data:
            setattr(record, field, data[field])
    confirmar_ou_reverter()
    return record


def excluir_prontuario(record_id: int, user):
    record = obter_ou_404(Prontuario, record_id, "Prontuário")
    if user.role == PerfilUsuario.MEDICO and (not user.doctor or record.doctor_id != user.doctor.id):
        raise ErroApi("Médicos só podem excluir seus próprios prontuários.", 403)
    db.session.delete(record)
    confirmar_ou_reverter()
