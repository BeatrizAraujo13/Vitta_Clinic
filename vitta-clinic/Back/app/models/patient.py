"""Patient records with soft-delete support."""

from datetime import datetime, timezone

from app.extensions import db
from app.utils.validators import is_valid_cpf, normalize_cpf


class Patient(db.Model):
    __tablename__ = "patients"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(160), nullable=False, index=True)
    cpf = db.Column(db.String(11), nullable=False, unique=True, index=True)
    birth_date = db.Column(db.Date, nullable=False)
    phone = db.Column(db.String(32), nullable=False)
    email = db.Column(db.String(254))
    address = db.Column(db.String(300))
    insurance = db.Column(db.String(120))
    notes = db.Column(db.Text)
    created_at = db.Column(db.DateTime(timezone=True), nullable=False, default=lambda: datetime.now(timezone.utc))
    deleted_at = db.Column(db.DateTime(timezone=True))

    appointments = db.relationship("Appointment", back_populates="patient")
    records = db.relationship("MedicalRecord", back_populates="patient")

    @staticmethod
    def normalize_and_validate_cpf(value: str) -> str:
        cpf = normalize_cpf(value)
        if not is_valid_cpf(cpf):
            raise ValueError("CPF inválido.")
        return cpf

    def to_dict(self):
        return {
            "id": self.id,
            "name": self.name,
            "cpf": self.cpf,
            "birth_date": self.birth_date.isoformat(),
            "phone": self.phone,
            "email": self.email,
            "address": self.address,
            "insurance": self.insurance,
            "notes": self.notes,
            "created_at": self.created_at.isoformat(),
            "deleted_at": self.deleted_at.isoformat() if self.deleted_at else None,
        }
