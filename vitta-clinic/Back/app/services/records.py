"""Medical record rules and physician authorization."""

from datetime import date

from app.extensions import db
from app.models import Appointment, AppointmentStatus, MedicalRecord, UserRole
from app.services.common import commit_or_rollback, get_or_404
from app.utils.errors import ApiError


def list_records(user, patient_id=None):
    query = MedicalRecord.query
    if user.role == UserRole.MEDICO:
        if not user.doctor:
            return []
        query = query.filter_by(doctor_id=user.doctor.id)
    if patient_id:
        query = query.filter_by(patient_id=patient_id)
    return query.order_by(MedicalRecord.record_date.desc(), MedicalRecord.id.desc()).all()


def _validate_appointment(appointment: Appointment, user):
    if appointment.status != AppointmentStatus.REALIZADA:
        raise ApiError("O prontuário só pode ser criado em uma consulta realizada.", 409)
    if user.role == UserRole.MEDICO and (not user.doctor or user.doctor.id != appointment.doctor_id):
        raise ApiError("Médicos só podem acessar prontuários de suas próprias consultas.", 403)


def create_record(data: dict, user) -> MedicalRecord:
    appointment = get_or_404(Appointment, data["appointment_id"], "Consulta")
    _validate_appointment(appointment, user)
    if data["record_date"] > date.today():
        raise ApiError("A data do prontuário não pode estar no futuro.", 400)
    if appointment.record:
        raise ApiError("Já existe um prontuário para esta consulta.", 409)
    record = MedicalRecord(
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
    commit_or_rollback()
    return record


def update_record(record_id: int, data: dict, user) -> MedicalRecord:
    record = get_or_404(MedicalRecord, record_id, "Prontuário")
    if user.role == UserRole.MEDICO and (not user.doctor or record.doctor_id != user.doctor.id):
        raise ApiError("Médicos só podem editar seus próprios prontuários.", 403)
    appointment_id = data.get("appointment_id", record.appointment_id)
    appointment = get_or_404(Appointment, appointment_id, "Consulta")
    _validate_appointment(appointment, user)
    if data.get("record_date", record.record_date) > date.today():
        raise ApiError("A data do prontuário não pode estar no futuro.", 400)
    duplicate = MedicalRecord.query.filter_by(appointment_id=appointment.id).first()
    if duplicate and duplicate.id != record.id:
        raise ApiError("Já existe um prontuário para esta consulta.", 409)
    if appointment.patient_id != record.patient_id:
        raise ApiError("O prontuário não pode ser movido para outro paciente.", 409)
    record.appointment = appointment
    record.doctor_id = appointment.doctor_id
    for field in ("record_date", "complaint", "diagnosis", "prescription", "notes"):
        if field in data:
            setattr(record, field, data[field])
    commit_or_rollback()
    return record


def delete_record(record_id: int, user):
    record = get_or_404(MedicalRecord, record_id, "Prontuário")
    if user.role == UserRole.MEDICO and (not user.doctor or record.doctor_id != user.doctor.id):
        raise ApiError("Médicos só podem excluir seus próprios prontuários.", 403)
    db.session.delete(record)
    commit_or_rollback()
