"""Administrator-only aggregate reports."""

from sqlalchemy import func

from app.extensions import db
from app.models import Appointment, AppointmentStatus, Doctor, Patient
from app.utils.errors import ApiError


def appointments_report(date_from=None, date_to=None, doctor_id=None):
    if date_from and date_to and date_from > date_to:
        raise ApiError("A data inicial deve ser anterior ou igual à data final.", 400)
    query = Appointment.query
    if date_from:
        query = query.filter(Appointment.appointment_date >= date_from)
    if date_to:
        query = query.filter(Appointment.appointment_date <= date_to)
    if doctor_id:
        query = query.filter_by(doctor_id=doctor_id)
    return [item.to_dict() for item in query.order_by(Appointment.appointment_date, Appointment.appointment_time).all()]


def patients_report():
    return [item.to_dict() for item in Patient.query.filter(Patient.deleted_at.is_(None)).order_by(Patient.name).all()]


def doctors_report(date_from=None, date_to=None):
    query = db.session.query(
        Doctor.id,
        Doctor.name,
        Doctor.crm,
        func.count(Appointment.id).label("appointment_count"),
    ).outerjoin(Appointment, Appointment.doctor_id == Doctor.id)
    if date_from:
        query = query.filter(db.or_(Appointment.id.is_(None), Appointment.appointment_date >= date_from))
    if date_to:
        query = query.filter(db.or_(Appointment.id.is_(None), Appointment.appointment_date <= date_to))
    query = query.group_by(Doctor.id).order_by(Doctor.name)
    return [
        {"doctor_id": row.id, "doctor_name": row.name, "crm": row.crm, "appointment_count": row.appointment_count}
        for row in query.all()
    ]
