"""Medical specialties."""

from app.extensions import db


class Specialty(db.Model):
    __tablename__ = "specialties"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False, unique=True, index=True)
    description = db.Column(db.Text)

    doctors = db.relationship("Doctor", back_populates="specialty")

    def to_dict(self):
        return {"id": self.id, "name": self.name, "description": self.description}
