"""Gerenciamento de médicos e especialidades."""

from app.extensoes import db
from app.models import Medico, Especialidade, Usuario, PerfilUsuario
from app.services.comum import confirmar_ou_reverter, obter_ou_404
from app.utils.erros import ErroApi
from app.utils.validadores import normalizar_crm


def listar_medicos(search: str | None = None, specialty_id: int | None = None):
    query = Medico.query
    if search:
        term = f"%{search.strip()}%"
        query = query.filter(db.or_(Medico.name.ilike(term), Medico.crm.ilike(term)))
    if specialty_id:
        query = query.filter_by(specialty_id=specialty_id)
    return query.order_by(Medico.name).all()


def salvar_medico(data: dict, doctor: Medico | None = None) -> Medico:
    specialty = obter_ou_404(Especialidade, data.get("specialty_id", doctor.specialty_id if doctor else None), "Especialidade")
    try:
        crm = normalizar_crm(data.get("crm", doctor.crm if doctor else ""))
    except ValueError as error:
        raise ErroApi(str(error), 400) from error
    duplicate = Medico.query.filter_by(crm=crm).first()
    if duplicate and duplicate.id != (doctor.id if doctor else None):
        raise ErroApi("Já existe um médico com este CRM.", 409)
    user_id = data.get("user_id", doctor.user_id if doctor else None)
    if user_id is not None:
        user = obter_ou_404(Usuario, user_id, "Usuário")
        if user.role != PerfilUsuario.MEDICO:
            raise ErroApi("O usuário vinculado deve ter perfil médico.", 400)
        linked = Medico.query.filter_by(user_id=user.id).first()
        if linked and linked.id != (doctor.id if doctor else None):
            raise ErroApi("Este usuário já está vinculado a outro médico.", 409)
    if doctor is None:
        doctor = Medico()
        db.session.add(doctor)
    doctor.specialty = specialty
    doctor.crm = crm
    for field in ("user_id", "name", "email", "phone", "schedule", "active"):
        if field in data:
            setattr(doctor, field, data[field])
    confirmar_ou_reverter()
    return doctor


def excluir_medico(doctor_id: int):
    doctor = obter_ou_404(Medico, doctor_id, "Médico")
    if doctor.appointments:
        doctor.active = False
    else:
        db.session.delete(doctor)
    confirmar_ou_reverter()
    return {"deleted": True, "deactivated": not doctor.active}


def listar_especialidades():
    return Especialidade.query.order_by(Especialidade.name).all()


def salvar_especialidade(data: dict, specialty: Especialidade | None = None):
    name = data.get("name", specialty.name if specialty else "").strip()
    duplicate = Especialidade.query.filter(db.func.lower(Especialidade.name) == name.lower()).first()
    if duplicate and duplicate.id != (specialty.id if specialty else None):
        raise ErroApi("Esta especialidade já está cadastrada.", 409)
    if specialty is None:
        specialty = Especialidade()
        db.session.add(specialty)
    specialty.name = name
    if "description" in data:
        specialty.description = data["description"]
    confirmar_ou_reverter()
    return specialty


def excluir_especialidade(specialty_id: int):
    specialty = obter_ou_404(Especialidade, specialty_id, "Especialidade")
    if specialty.doctors:
        raise ErroApi("Não é possível excluir uma especialidade vinculada a médicos.", 409)
    db.session.delete(specialty)
    confirmar_ou_reverter()
