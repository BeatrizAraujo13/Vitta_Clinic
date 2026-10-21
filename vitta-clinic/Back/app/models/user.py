"""User accounts and role definitions."""

from datetime import datetime, timezone
from enum import Enum

from app.extensions import bcrypt, db


class UserRole(str, Enum):
    ADMIN = "admin"
    MEDICO = "medico"
    RECEPCIONISTA = "recepcionista"


class User(db.Model):
    __tablename__ = "users"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120), nullable=False)
    email = db.Column(db.String(254), nullable=False, unique=True, index=True)
    password_hash = db.Column(db.String(128), nullable=False)
    role = db.Column(db.Enum(UserRole, values_callable=lambda enum: [item.value for item in enum]), nullable=False)
    active = db.Column(db.Boolean, nullable=False, default=True)
    created_at = db.Column(db.DateTime(timezone=True), nullable=False, default=lambda: datetime.now(timezone.utc))

    doctor = db.relationship("Doctor", back_populates="user", uselist=False)

    def set_password(self, password: str) -> None:
        self.password_hash = bcrypt.generate_password_hash(password).decode("utf-8")

    def check_password(self, password: str) -> bool:
        return bcrypt.check_password_hash(self.password_hash, password)

    def to_dict(self):
        return {
            "id": self.id,
            "name": self.name,
            "email": self.email,
            "role": self.role.value,
            "active": self.active,
            "doctor_id": self.doctor.id if self.doctor else None,
        }
