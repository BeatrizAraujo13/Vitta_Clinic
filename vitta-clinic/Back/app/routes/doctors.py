"""Physician REST endpoints."""

from flask import Blueprint, request

from app.models import Doctor
from app.schemas.doctor import DoctorSchema, DoctorUpdateSchema
from app.services.common import get_or_404, load_payload
from app.services.doctors import delete_doctor, list_doctors, save_doctor
from app.utils.auth import roles_required
from app.utils.errors import ApiError

bp = Blueprint("doctors", __name__, url_prefix="/doctors")


@bp.get("")
@roles_required("admin", "medico", "recepcionista")
def index():
    try:
        specialty_id = int(request.args["specialty_id"]) if request.args.get("specialty_id") else None
    except ValueError as error:
        raise ApiError("specialty_id deve ser um número inteiro.", 400) from error
    items = list_doctors(request.args.get("search"), specialty_id)
    return {"items": [doctor.to_dict() for doctor in items]}


@bp.post("")
@roles_required("admin")
def create():
    doctor = save_doctor(load_payload(DoctorSchema()))
    return {"doctor": doctor.to_dict()}, 201


@bp.get("/<int:doctor_id>")
@roles_required("admin", "medico", "recepcionista")
def show(doctor_id):
    return {"doctor": get_or_404(Doctor, doctor_id, "Médico").to_dict()}


@bp.patch("/<int:doctor_id>")
@roles_required("admin")
def update(doctor_id):
    data = load_payload(DoctorUpdateSchema(), partial=True)
    if not data:
        raise ApiError("Informe ao menos um campo para atualizar.", 400)
    doctor = save_doctor(data, get_or_404(Doctor, doctor_id, "Médico"))
    return {"doctor": doctor.to_dict()}


@bp.delete("/<int:doctor_id>")
@roles_required("admin")
def delete(doctor_id):
    return delete_doctor(doctor_id)
