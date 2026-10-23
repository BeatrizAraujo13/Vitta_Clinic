"""Registros de pacientes com suporte à exclusão lógica."""

from datetime import datetime, timezone

from app.extensoes import db
from app.utils.validadores import cpf_valido, normalizar_cpf


class Paciente(db.Model):
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

    appointments = db.relationship("Consulta", back_populates="patient")
    records = db.relationship("Prontuario", back_populates="patient")

    @staticmethod
    def normalizar_e_validar_cpf(value: str) -> str:
        cpf = normalizar_cpf(value)
        if not cpf_valido(cpf):
            raise ValueError("CPF inválido.")
        return cpf

    def para_dicionario(self):
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
