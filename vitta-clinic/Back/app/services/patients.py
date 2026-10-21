"""Patient CRUD and historical soft-delete rules."""

from datetime import datetime, timezone

from sqlalchemy import or_

from app.extensions import db
from app.models import Appointment, MedicalRecord, Patient
from app.services.common import commit_or_rollback, get_or_404
from app.utils.errors import ApiError
from app.utils.validators import is_valid_cpf, normalize_cpf


def list_patients(search: str | None = None, include_deleted: bool = False):
    query = Patient.query
    if not include_deleted:
        query = query.filter(Patient.deleted_at.is_(None))
    if search:
        term = f"%{search.strip()}%"
        digits = normalize_cpf(search)
        conditions = [Patient.name.ilike(term)]
        if digits:
            conditions.append(Patient.cpf.like(f"%{digits}%"))
        query = query.filter(or_(*conditions))
    return query.order_by(Patient.name).all()


def save_patient(data: dict, patient: Patient | None = None) -> Patient:
    cpf = normalize_cpf(data.get("cpf", patient.cpf if patient else ""))
    if not is_valid_cpf(cpf):
        raise ApiError("CPF inválido.", 400)
    existing = Patient.query.filter_by(cpf=cpf).first()
    if existing and existing.id != (patient.id if patient else None):
        raise ApiError("Já existe um paciente com este CPF.", 409)
    if patient is None:
        patient = Patient(cpf=cpf)
        db.session.add(patient)
    patient.cpf = cpf
    for field in ("name", "birth_date", "phone", "email", "address", "insurance", "notes"):
        if field in data:
            setattr(patient, field, data[field])
    commit_or_rollback()
    return patient


def delete_patient(patient_id: int):
    patient = get_or_404(Patient, patient_id, "Paciente")
    has_history = (
        db.session.query(Appointment.id).filter_by(patient_id=patient.id).first()
        or db.session.query(MedicalRecord.id).filter_by(patient_id=patient.id).first()
    )
    if has_history:
        patient.deleted_at = datetime.now(timezone.utc)
    else:
        db.session.delete(patient)
    commit_or_rollback()
    return {"deleted": True, "soft_deleted": bool(has_history)}
