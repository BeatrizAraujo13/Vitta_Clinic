"""Appointment scheduling, conflict checks and physician scope."""

from datetime import datetime

from app.extensions import db
from app.models import Appointment, AppointmentStatus, Doctor, Patient, UserRole
from app.services.common import commit_or_rollback, get_or_404
from app.utils.errors import ApiError


def _validate_entities(patient_id: int, doctor_id: int):
    patient = get_or_404(Patient, patient_id, "Paciente")
    doctor = get_or_404(Doctor, doctor_id, "Médico")
    if patient.deleted_at is not None:
        raise ApiError("Não é possível agendar para um paciente inativo.", 409)
    if not doctor.active:
        raise ApiError("Não é possível agendar com um médico inativo.", 409)
    return patient, doctor


def _check_time(appointment_date, appointment_time, status):
    starts_at = datetime.combine(appointment_date, appointment_time)
    if status == AppointmentStatus.AGENDADA and starts_at < datetime.now():
        raise ApiError("Não é possível agendar consulta no passado.", 400)
    return starts_at


def _check_conflict(patient_id, doctor_id, appointment_date, appointment_time, exclude_id=None):
    query = Appointment.query.filter(
        Appointment.appointment_date == appointment_date,
        Appointment.appointment_time == appointment_time,
        Appointment.status != AppointmentStatus.CANCELADA,
        db.or_(Appointment.doctor_id == doctor_id, Appointment.patient_id == patient_id),
    )
    if exclude_id is not None:
        query = query.filter(Appointment.id != exclude_id)
    conflict = query.first()
    if conflict:
        if conflict.doctor_id == doctor_id:
            raise ApiError("O médico já possui uma consulta neste horário.", 409)
        raise ApiError("O paciente já possui uma consulta neste horário.", 409)


def list_appointments(user, *, date_from=None, date_to=None, status=None, doctor_id=None):
    query = Appointment.query.join(Patient).filter(Patient.deleted_at.is_(None))
    if user.role == UserRole.MEDICO:
        if not user.doctor:
            return []
        query = query.filter(Appointment.doctor_id == user.doctor.id)
    elif doctor_id:
        query = query.filter(Appointment.doctor_id == doctor_id)
    if date_from:
        query = query.filter(Appointment.appointment_date >= date_from)
    if date_to:
        query = query.filter(Appointment.appointment_date <= date_to)
    if status:
        query = query.filter(Appointment.status == status)
    return query.order_by(Appointment.appointment_date, Appointment.appointment_time).all()


def create_appointment(data: dict) -> Appointment:
    patient, doctor = _validate_entities(data["patient_id"], data["doctor_id"])
    status = AppointmentStatus(data.get("status", AppointmentStatus.AGENDADA.value))
    starts_at = _check_time(data["date"], data["time"], status)
    if starts_at < datetime.now():
        raise ApiError("Não é possível criar uma consulta no passado.", 400)
    if status == AppointmentStatus.REALIZADA:
        raise ApiError("Uma consulta nova não pode ser criada como realizada.", 400)
    _check_conflict(patient.id, doctor.id, data["date"], data["time"])
    appointment = Appointment(
        patient=patient,
        doctor=doctor,
        appointment_date=data["date"],
        appointment_time=data["time"],
        status=status,
        notes=data.get("notes"),
    )
    db.session.add(appointment)
    commit_or_rollback()
    return appointment


def update_appointment(appointment_id: int, data: dict, user) -> Appointment:
    appointment = get_or_404(Appointment, appointment_id, "Consulta")
    if user.role == UserRole.MEDICO:
        if not user.doctor or user.doctor.id != appointment.doctor_id:
            raise ApiError("Você só pode atualizar suas próprias consultas.", 403)
        if set(data) - {"status"} or data.get("status") != AppointmentStatus.REALIZADA.value:
            raise ApiError("Médicos podem apenas marcar suas consultas como realizadas.", 403)
    patient_id = data.get("patient_id", appointment.patient_id)
    doctor_id = data.get("doctor_id", appointment.doctor_id)
    appointment_date = data.get("date", appointment.appointment_date)
    appointment_time = data.get("time", appointment.appointment_time)
    status = AppointmentStatus(data.get("status", appointment.status.value))
    _validate_entities(patient_id, doctor_id)
    schedule_changed = (
        appointment_date != appointment.appointment_date
        or appointment_time != appointment.appointment_time
    )
    if schedule_changed and datetime.combine(appointment_date, appointment_time) < datetime.now():
        raise ApiError("Não é possível remarcar uma consulta para o passado.", 400)
    if status == AppointmentStatus.REALIZADA and datetime.combine(appointment_date, appointment_time) > datetime.now():
        raise ApiError("Não é possível marcar como realizada uma consulta futura.", 400)
    if appointment.record and status != AppointmentStatus.REALIZADA:
        raise ApiError("Uma consulta com prontuário não pode deixar de ser realizada.", 409)
    _check_time(appointment_date, appointment_time, status)
    _check_conflict(patient_id, doctor_id, appointment_date, appointment_time, appointment.id)
    appointment.patient_id = patient_id
    appointment.doctor_id = doctor_id
    appointment.appointment_date = appointment_date
    appointment.appointment_time = appointment_time
    appointment.status = status
    if "notes" in data:
        appointment.notes = data["notes"]
    commit_or_rollback()
    return appointment


def delete_appointment(appointment_id: int):
    appointment = get_or_404(Appointment, appointment_id, "Consulta")
    if appointment.record:
        raise ApiError("Não é possível excluir uma consulta com prontuário vinculado.", 409)
    db.session.delete(appointment)
    commit_or_rollback()
