"""Appointment REST endpoints."""

from datetime import date

from flask import Blueprint, request

from app.schemas.appointment import AppointmentSchema, AppointmentUpdateSchema
from app.services.appointments import (
    create_appointment,
    delete_appointment,
    list_appointments,
    update_appointment,
)
from app.services.common import get_or_404, load_payload
from app.models import Appointment
from app.utils.auth import current_user, roles_required
from app.utils.errors import ApiError

bp = Blueprint("appointments", __name__, url_prefix="/appointments")


def _query_date(name):
    value = request.args.get(name)
    if not value:
        return None
    try:
        return date.fromisoformat(value)
    except ValueError as error:
        raise ApiError(f"{name} deve estar no formato AAAA-MM-DD.", 400) from error


@bp.get("")
@roles_required("admin", "medico", "recepcionista")
def index():
    status = request.args.get("status")
    if status and status not in {"agendada", "realizada", "cancelada"}:
        raise ApiError("Status inválido.", 400)
    doctor_id = request.args.get("doctor_id")
    try:
        doctor_id = int(doctor_id) if doctor_id else None
    except ValueError as error:
        raise ApiError("doctor_id deve ser um número inteiro.", 400) from error
    items = list_appointments(
        current_user(),
        date_from=_query_date("date_from"),
        date_to=_query_date("date_to"),
        status=status,
        doctor_id=doctor_id,
    )
    return {"items": [appointment.to_dict() for appointment in items]}


@bp.post("")
@roles_required("admin", "recepcionista")
def create():
    appointment = create_appointment(load_payload(AppointmentSchema()))
    return {"appointment": appointment.to_dict()}, 201


@bp.get("/<int:appointment_id>")
@roles_required("admin", "medico", "recepcionista")
def show(appointment_id):
    appointment = get_or_404(Appointment, appointment_id, "Consulta")
    user = current_user()
    if user.role.value == "medico" and (not user.doctor or appointment.doctor_id != user.doctor.id):
        raise ApiError("Consulta não encontrada.", 404)
    return {"appointment": appointment.to_dict()}


@bp.patch("/<int:appointment_id>")
@roles_required("admin", "medico", "recepcionista")
def update(appointment_id):
    data = load_payload(AppointmentUpdateSchema(), partial=True)
    if not data:
        raise ApiError("Informe ao menos um campo para atualizar.", 400)
    appointment = update_appointment(appointment_id, data, current_user())
    return {"appointment": appointment.to_dict()}


@bp.delete("/<int:appointment_id>")
@roles_required("admin", "recepcionista")
def delete(appointment_id):
    delete_appointment(appointment_id)
    return {"deleted": True}
