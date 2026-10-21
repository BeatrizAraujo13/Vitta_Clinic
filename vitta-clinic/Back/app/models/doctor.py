"""Physician profiles, optionally associated with a login account."""

from app.extensions import db
from app.utils.validators import normalize_crm


class Doctor(db.Model):
    __tablename__ = "doctors"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), unique=True)
    specialty_id = db.Column(db.Integer, db.ForeignKey("specialties.id"), nullable=False)
    name = db.Column(db.String(160), nullable=False, index=True)
    crm = db.Column(db.String(12), nullable=False, unique=True, index=True)
    email = db.Column(db.String(254), nullable=False)
    phone = db.Column(db.String(32), nullable=False)
    schedule = db.Column(db.String(200))
    active = db.Column(db.Boolean, nullable=False, default=True)

    user = db.relationship("User", back_populates="doctor")
    specialty = db.relationship("Specialty", back_populates="doctors")
    appointments = db.relationship("Appointment", back_populates="doctor")

    @staticmethod
    def normalize_and_validate_crm(value: str) -> str:
        return normalize_crm(value)

    def to_dict(self):
        return {
            "id": self.id,
            "user_id": self.user_id,
            "name": self.name,
            "crm": self.crm,
            "specialty_id": self.specialty_id,
            "specialty": self.specialty.to_dict() if self.specialty else None,
            "email": self.email,
            "phone": self.phone,
            "schedule": self.schedule,
            "active": self.active,
        }
