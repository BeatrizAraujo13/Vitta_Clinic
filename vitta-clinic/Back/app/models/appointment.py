"""Appointment scheduling and status."""

from datetime import datetime
from enum import Enum

from app.extensions import db
from sqlalchemy import Index, text


class AppointmentStatus(str, Enum):
    AGENDADA = "agendada"
    REALIZADA = "realizada"
    CANCELADA = "cancelada"


class Appointment(db.Model):
    __tablename__ = "appointments"
    __table_args__ = (
        Index(
            "uq_appointment_doctor_active_slot",
            "doctor_id",
            "appointment_date",
            "appointment_time",
            unique=True,
            sqlite_where=text("status != 'cancelada'"),
            postgresql_where=text("status != 'cancelada'"),
        ),
        Index(
            "uq_appointment_patient_active_slot",
            "patient_id",
            "appointment_date",
            "appointment_time",
            unique=True,
            sqlite_where=text("status != 'cancelada'"),
            postgresql_where=text("status != 'cancelada'"),
        ),
    )

    id = db.Column(db.Integer, primary_key=True)
    patient_id = db.Column(db.Integer, db.ForeignKey("patients.id"), nullable=False, index=True)
    doctor_id = db.Column(db.Integer, db.ForeignKey("doctors.id"), nullable=False, index=True)
    appointment_date = db.Column(db.Date, nullable=False, index=True)
    appointment_time = db.Column(db.Time, nullable=False)
    status = db.Column(db.Enum(AppointmentStatus, values_callable=lambda enum: [item.value for item in enum]), nullable=False, default=AppointmentStatus.AGENDADA)
    notes = db.Column(db.Text)

    patient = db.relationship("Patient", back_populates="appointments")
    doctor = db.relationship("Doctor", back_populates="appointments")
    record = db.relationship("MedicalRecord", back_populates="appointment", uselist=False)

    def starts_at(self) -> datetime:
        return datetime.combine(self.appointment_date, self.appointment_time)

    def is_in_past(self, now: datetime | None = None) -> bool:
        return self.starts_at() < (now or datetime.now())

    def to_dict(self):
        return {
            "id": self.id,
            "patient_id": self.patient_id,
            "patient_name": self.patient.name if self.patient else None,
            "doctor_id": self.doctor_id,
            "doctor_name": self.doctor.name if self.doctor else None,
            "specialty_id": self.doctor.specialty_id if self.doctor else None,
            "date": self.appointment_date.isoformat(),
            "time": self.appointment_time.strftime("%H:%M"),
            "status": self.status.value,
            "notes": self.notes,
        }
