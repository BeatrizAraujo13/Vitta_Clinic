"""Especialidades médicas."""

from app.extensoes import db


class Especialidade(db.Model):
    __tablename__ = "specialties"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False, unique=True, index=True)
    description = db.Column(db.Text)

    doctors = db.relationship("Medico", back_populates="specialty")

    def para_dicionario(self):
        return {"id": self.id, "name": self.name, "description": self.description}
