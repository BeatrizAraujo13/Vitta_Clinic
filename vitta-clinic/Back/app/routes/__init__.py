"""Versioned API blueprints."""

from flask import Blueprint

api_v1 = Blueprint("api_v1", __name__, url_prefix="/api/v1")

from app.routes import (  # noqa: E402,F401
    appointments,
    auth,
    doctors,
    patients,
    records,
    reports,
    specialties,
    users,
)

api_v1.register_blueprint(auth.bp)
api_v1.register_blueprint(users.bp)
api_v1.register_blueprint(patients.bp)
api_v1.register_blueprint(doctors.bp)
api_v1.register_blueprint(specialties.bp)
api_v1.register_blueprint(appointments.bp)
api_v1.register_blueprint(records.bp)
api_v1.register_blueprint(reports.bp)
