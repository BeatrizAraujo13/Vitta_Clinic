"""Doctor and specialty management."""

from app.extensions import db
from app.models import Doctor, Specialty, User, UserRole
from app.services.common import commit_or_rollback, get_or_404
from app.utils.errors import ApiError
from app.utils.validators import normalize_crm


def list_doctors(search: str | None = None, specialty_id: int | None = None):
    query = Doctor.query
    if search:
        term = f"%{search.strip()}%"
        query = query.filter(db.or_(Doctor.name.ilike(term), Doctor.crm.ilike(term)))
    if specialty_id:
        query = query.filter_by(specialty_id=specialty_id)
    return query.order_by(Doctor.name).all()


def save_doctor(data: dict, doctor: Doctor | None = None) -> Doctor:
    specialty = get_or_404(Specialty, data.get("specialty_id", doctor.specialty_id if doctor else None), "Especialidade")
    try:
        crm = normalize_crm(data.get("crm", doctor.crm if doctor else ""))
    except ValueError as error:
        raise ApiError(str(error), 400) from error
    duplicate = Doctor.query.filter_by(crm=crm).first()
    if duplicate and duplicate.id != (doctor.id if doctor else None):
        raise ApiError("Já existe um médico com este CRM.", 409)
    user_id = data.get("user_id", doctor.user_id if doctor else None)
    if user_id is not None:
        user = get_or_404(User, user_id, "Usuário")
        if user.role != UserRole.MEDICO:
            raise ApiError("O usuário vinculado deve ter perfil médico.", 400)
        linked = Doctor.query.filter_by(user_id=user.id).first()
        if linked and linked.id != (doctor.id if doctor else None):
            raise ApiError("Este usuário já está vinculado a outro médico.", 409)
    if doctor is None:
        doctor = Doctor()
        db.session.add(doctor)
    doctor.specialty = specialty
    doctor.crm = crm
    for field in ("user_id", "name", "email", "phone", "schedule", "active"):
        if field in data:
            setattr(doctor, field, data[field])
    commit_or_rollback()
    return doctor


def delete_doctor(doctor_id: int):
    doctor = get_or_404(Doctor, doctor_id, "Médico")
    if doctor.appointments:
        doctor.active = False
    else:
        db.session.delete(doctor)
    commit_or_rollback()
    return {"deleted": True, "deactivated": not doctor.active}


def list_specialties():
    return Specialty.query.order_by(Specialty.name).all()


def save_specialty(data: dict, specialty: Specialty | None = None):
    name = data.get("name", specialty.name if specialty else "").strip()
    duplicate = Specialty.query.filter(db.func.lower(Specialty.name) == name.lower()).first()
    if duplicate and duplicate.id != (specialty.id if specialty else None):
        raise ApiError("Esta especialidade já está cadastrada.", 409)
    if specialty is None:
        specialty = Specialty()
        db.session.add(specialty)
    specialty.name = name
    if "description" in data:
        specialty.description = data["description"]
    commit_or_rollback()
    return specialty


def delete_specialty(specialty_id: int):
    specialty = get_or_404(Specialty, specialty_id, "Especialidade")
    if specialty.doctors:
        raise ApiError("Não é possível excluir uma especialidade vinculada a médicos.", 409)
    db.session.delete(specialty)
    commit_or_rollback()
