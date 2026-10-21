"""Patient REST endpoints."""

from flask import Blueprint, request

from app.models import Patient, UserRole
from app.schemas.patient import PatientSchema, PatientUpdateSchema
from app.services.common import get_or_404, load_payload
from app.services.patients import delete_patient, list_patients, save_patient
from app.utils.auth import current_user, roles_required
from app.utils.errors import ApiError

bp = Blueprint("patients", __name__, url_prefix="/patients")


@bp.get("")
@roles_required("admin", "medico", "recepcionista")
def index():
    user = current_user()
    include_deleted = request.args.get("include_deleted") == "true"
    if include_deleted and user.role != UserRole.ADMIN:
        raise ApiError("Apenas administradores podem consultar pacientes excluídos.", 403)
    items = list_patients(request.args.get("search"), include_deleted)
    return {"items": [patient.to_dict() for patient in items]}


@bp.post("")
@roles_required("admin", "recepcionista")
def create():
    patient = save_patient(load_payload(PatientSchema()))
    return {"patient": patient.to_dict()}, 201


@bp.get("/<int:patient_id>")
@roles_required("admin", "medico", "recepcionista")
def show(patient_id):
    patient = get_or_404(Patient, patient_id, "Paciente")
    if patient.deleted_at:
        raise ApiError("Paciente não encontrado(a).", 404)
    return {"patient": patient.to_dict()}


@bp.patch("/<int:patient_id>")
@roles_required("admin", "recepcionista")
def update(patient_id):
    patient = get_or_404(Patient, patient_id, "Paciente")
    if patient.deleted_at:
        raise ApiError("Não é possível editar um paciente excluído.", 409)
    data = load_payload(PatientUpdateSchema(), partial=True)
    if not data:
        raise ApiError("Informe ao menos um campo para atualizar.", 400)
    return {"patient": save_patient(data, patient).to_dict()}


@bp.delete("/<int:patient_id>")
@roles_required("admin", "recepcionista")
def delete(patient_id):
    return delete_patient(patient_id)
