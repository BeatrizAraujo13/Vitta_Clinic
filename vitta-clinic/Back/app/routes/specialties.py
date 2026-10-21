"""Administrator-only specialty REST endpoints."""

from flask import Blueprint

from app.models import Specialty
from app.schemas.doctor import SpecialtySchema, SpecialtyUpdateSchema
from app.services.common import get_or_404, load_payload
from app.services.doctors import delete_specialty, list_specialties, save_specialty
from app.utils.auth import roles_required
from app.utils.errors import ApiError

bp = Blueprint("specialties", __name__, url_prefix="/specialties")


@bp.get("")
@roles_required("admin")
def index():
    return {"items": [specialty.to_dict() for specialty in list_specialties()]}


@bp.post("")
@roles_required("admin")
def create():
    specialty = save_specialty(load_payload(SpecialtySchema()))
    return {"specialty": specialty.to_dict()}, 201


@bp.get("/<int:specialty_id>")
@roles_required("admin")
def show(specialty_id):
    return {"specialty": get_or_404(Specialty, specialty_id, "Especialidade").to_dict()}


@bp.patch("/<int:specialty_id>")
@roles_required("admin")
def update(specialty_id):
    data = load_payload(SpecialtyUpdateSchema(), partial=True)
    if not data:
        raise ApiError("Informe ao menos um campo para atualizar.", 400)
    specialty = save_specialty(data, get_or_404(Specialty, specialty_id, "Especialidade"))
    return {"specialty": specialty.to_dict()}


@bp.delete("/<int:specialty_id>")
@roles_required("admin")
def delete(specialty_id):
    delete_specialty(specialty_id)
    return {"deleted": True}
