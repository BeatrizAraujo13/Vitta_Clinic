"""Medical record REST endpoints."""

from flask import Blueprint, request

from app.models import MedicalRecord
from app.schemas.record import MedicalRecordSchema, MedicalRecordUpdateSchema
from app.services.common import get_or_404, load_payload
from app.services.records import create_record, delete_record, list_records, update_record
from app.utils.auth import current_user, roles_required
from app.utils.errors import ApiError

bp = Blueprint("records", __name__, url_prefix="/records")


@bp.get("")
@roles_required("admin", "medico")
def index():
    patient_id = request.args.get("patient_id")
    try:
        patient_id = int(patient_id) if patient_id else None
    except ValueError as error:
        raise ApiError("patient_id deve ser um número inteiro.", 400) from error
    return {"items": [record.to_dict() for record in list_records(current_user(), patient_id)]}


@bp.post("")
@roles_required("admin", "medico")
def create():
    record = create_record(load_payload(MedicalRecordSchema()), current_user())
    return {"record": record.to_dict()}, 201


@bp.get("/<int:record_id>")
@roles_required("admin", "medico")
def show(record_id):
    record = get_or_404(MedicalRecord, record_id, "Prontuário")
    user = current_user()
    if user.role.value == "medico" and (not user.doctor or record.doctor_id != user.doctor.id):
        raise ApiError("Prontuário não encontrado.", 404)
    return {"record": record.to_dict()}


@bp.patch("/<int:record_id>")
@roles_required("admin", "medico")
def update(record_id):
    data = load_payload(MedicalRecordUpdateSchema(), partial=True)
    if not data:
        raise ApiError("Informe ao menos um campo para atualizar.", 400)
    record = update_record(record_id, data, current_user())
    return {"record": record.to_dict()}


@bp.delete("/<int:record_id>")
@roles_required("admin", "medico")
def delete(record_id):
    delete_record(record_id, current_user())
    return {"deleted": True}
