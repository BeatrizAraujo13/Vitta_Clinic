"""Agendamento de consultas, verificação de conflitos e escopo médico."""

from datetime import datetime

from app.extensoes import db
from app.models import Consulta, StatusConsulta, Medico, Paciente, PerfilUsuario
from app.services.comum import confirmar_ou_reverter, obter_ou_404
from app.utils.erros import ErroApi


def _validar_entidades(patient_id: int, doctor_id: int):
    patient = obter_ou_404(Paciente, patient_id, "Paciente")
    doctor = obter_ou_404(Medico, doctor_id, "Médico")
    if patient.deleted_at is not None:
        raise ErroApi("Não é possível agendar para um paciente inativo.", 409)
    if not doctor.active:
        raise ErroApi("Não é possível agendar com um médico inativo.", 409)
    return patient, doctor


def _validar_horario(appointment_date, appointment_time, status):
    inicia_em = datetime.combine(appointment_date, appointment_time)
    if status == StatusConsulta.AGENDADA and inicia_em < datetime.now():
        raise ErroApi("Não é possível agendar consulta no passado.", 400)
    return inicia_em


def _validar_conflito(patient_id, doctor_id, appointment_date, appointment_time, exclude_id=None):
    query = Consulta.query.filter(
        Consulta.appointment_date == appointment_date,
        Consulta.appointment_time == appointment_time,
        Consulta.status != StatusConsulta.CANCELADA,
        db.or_(Consulta.doctor_id == doctor_id, Consulta.patient_id == patient_id),
    )
    if exclude_id is not None:
        query = query.filter(Consulta.id != exclude_id)
    conflict = query.first()
    if conflict:
        if conflict.doctor_id == doctor_id:
            raise ErroApi("O médico já possui uma consulta neste horário.", 409)
        raise ErroApi("O paciente já possui uma consulta neste horário.", 409)


def listar_consultas(user, *, date_from=None, date_to=None, status=None, doctor_id=None):
    query = Consulta.query.join(Paciente).filter(Paciente.deleted_at.is_(None))
    if user.role == PerfilUsuario.MEDICO:
        if not user.doctor:
            return []
        query = query.filter(Consulta.doctor_id == user.doctor.id)
    elif doctor_id:
        query = query.filter(Consulta.doctor_id == doctor_id)
    if date_from:
        query = query.filter(Consulta.appointment_date >= date_from)
    if date_to:
        query = query.filter(Consulta.appointment_date <= date_to)
    if status:
        query = query.filter(Consulta.status == status)
    return query.order_by(Consulta.appointment_date, Consulta.appointment_time).all()


def criar_consulta(data: dict) -> Consulta:
    patient, doctor = _validar_entidades(data["patient_id"], data["doctor_id"])
    status = StatusConsulta(data.get("status", StatusConsulta.AGENDADA.value))
    inicia_em = _validar_horario(data["date"], data["time"], status)
    if inicia_em < datetime.now():
        raise ErroApi("Não é possível criar uma consulta no passado.", 400)
    if status == StatusConsulta.REALIZADA:
        raise ErroApi("Uma consulta nova não pode ser criada como realizada.", 400)
    _validar_conflito(patient.id, doctor.id, data["date"], data["time"])
    appointment = Consulta(
        patient=patient,
        doctor=doctor,
        appointment_date=data["date"],
        appointment_time=data["time"],
        status=status,
        notes=data.get("notes"),
    )
    db.session.add(appointment)
    confirmar_ou_reverter()
    return appointment


def atualizar_consulta(appointment_id: int, data: dict, user) -> Consulta:
    appointment = obter_ou_404(Consulta, appointment_id, "Consulta")
    if user.role == PerfilUsuario.MEDICO:
        if not user.doctor or user.doctor.id != appointment.doctor_id:
            raise ErroApi("Você só pode atualizar suas próprias consultas.", 403)
        if set(data) - {"status"} or data.get("status") != StatusConsulta.REALIZADA.value:
            raise ErroApi("Médicos podem apenas marcar suas consultas como realizadas.", 403)
    patient_id = data.get("patient_id", appointment.patient_id)
    doctor_id = data.get("doctor_id", appointment.doctor_id)
    appointment_date = data.get("date", appointment.appointment_date)
    appointment_time = data.get("time", appointment.appointment_time)
    status = StatusConsulta(data.get("status", appointment.status.value))
    _validar_entidades(patient_id, doctor_id)
    schedule_changed = (
        appointment_date != appointment.appointment_date
        or appointment_time != appointment.appointment_time
    )
    if schedule_changed and datetime.combine(appointment_date, appointment_time) < datetime.now():
        raise ErroApi("Não é possível remarcar uma consulta para o passado.", 400)
    if status == StatusConsulta.REALIZADA and datetime.combine(appointment_date, appointment_time) > datetime.now():
        raise ErroApi("Não é possível marcar como realizada uma consulta futura.", 400)
    if appointment.record and status != StatusConsulta.REALIZADA:
        raise ErroApi("Uma consulta com prontuário não pode deixar de ser realizada.", 409)
    _validar_horario(appointment_date, appointment_time, status)
    _validar_conflito(patient_id, doctor_id, appointment_date, appointment_time, appointment.id)
    appointment.patient_id = patient_id
    appointment.doctor_id = doctor_id
    appointment.appointment_date = appointment_date
    appointment.appointment_time = appointment_time
    appointment.status = status
    if "notes" in data:
        appointment.notes = data["notes"]
    confirmar_ou_reverter()
    return appointment


def excluir_consulta(appointment_id: int):
    appointment = obter_ou_404(Consulta, appointment_id, "Consulta")
    if appointment.record:
        raise ErroApi("Não é possível excluir uma consulta com prontuário vinculado.", 409)
    db.session.delete(appointment)
    confirmar_ou_reverter()
