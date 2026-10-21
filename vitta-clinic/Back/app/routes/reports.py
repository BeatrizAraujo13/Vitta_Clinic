"""Administrator-only reports."""

from datetime import date

from flask import Blueprint, request

from app.services.reports import appointments_report, doctors_report, patients_report
from app.utils.auth import roles_required
from app.utils.errors import ApiError

bp = Blueprint("reports", __name__, url_prefix="/reports")


def _query_date(name):
    value = request.args.get(name)
    if not value:
        return None
    try:
        return date.fromisoformat(value)
    except ValueError as error:
        raise ApiError(f"{name} deve estar no formato AAAA-MM-DD.", 400) from error


@bp.get("/appointments")
@roles_required("admin")
def appointments():
    doctor_id = request.args.get("doctor_id")
    try:
        doctor_id = int(doctor_id) if doctor_id else None
    except ValueError as error:
        raise ApiError("doctor_id deve ser um número inteiro.", 400) from error
    items = appointments_report(_query_date("date_from"), _query_date("date_to"), doctor_id)
    return {"items": items, "count": len(items)}


@bp.get("/patients")
@roles_required("admin")
def patients():
    items = patients_report()
    return {"items": items, "count": len(items)}


@bp.get("/doctors")
@roles_required("admin")
def doctors():
    items = doctors_report(_query_date("date_from"), _query_date("date_to"))
    return {"items": items, "count": len(items)}
