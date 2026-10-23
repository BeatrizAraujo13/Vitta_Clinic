"""Perfis médicos, opcionalmente associados a uma conta de acesso."""

from app.extensoes import db
from app.utils.validadores import normalizar_crm


class Medico(db.Model):
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

    user = db.relationship("Usuario", back_populates="doctor")
    specialty = db.relationship("Especialidade", back_populates="doctors")
    appointments = db.relationship("Consulta", back_populates="doctor")

    @staticmethod
    def normalizar_e_validar_crm(value: str) -> str:
        return normalizar_crm(value)

    def para_dicionario(self):
        return {
            "id": self.id,
            "user_id": self.user_id,
            "name": self.name,
            "crm": self.crm,
            "specialty_id": self.specialty_id,
            "specialty": self.specialty.para_dicionario() if self.specialty else None,
            "email": self.email,
            "phone": self.phone,
            "schedule": self.schedule,
            "active": self.active,
        }
