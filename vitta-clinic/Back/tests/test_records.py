"""Medical record state and ownership tests."""

from datetime import date, timedelta

from app.extensions import db
from app.models import Appointment


def record_payload(appointment_id):
    return {
        "appointment_id": appointment_id,
        "record_date": date.today().isoformat(),
        "complaint": "Acompanhamento",
        "diagnosis": "Paciente estável",
        "prescription": "Retorno de rotina",
    }


def test_record_requires_completed_appointment_and_is_unique(client, auth_header):
    scheduled = client.post(
        "/api/v1/records",
        headers=auth_header,
        json=record_payload(2),
    )
    assert scheduled.status_code == 409

    with client.application.app_context():
        appointment = db.session.get(Appointment, 2)
        appointment.appointment_date = date.today() - timedelta(days=1)
        db.session.commit()

    completed = client.patch(
        "/api/v1/appointments/2",
        headers=auth_header,
        json={"status": "realizada"},
    )
    assert completed.status_code == 200
    created = client.post(
        "/api/v1/records",
        headers=auth_header,
        json=record_payload(2),
    )
    assert created.status_code == 201
    duplicate = client.post(
        "/api/v1/records",
        headers=auth_header,
        json=record_payload(2),
    )
    assert duplicate.status_code == 409


def test_doctor_can_only_update_own_appointment_status(client, tokens):
    token_data = tokens("medico@vitta.com")
    headers = {"Authorization": f"Bearer {token_data['access_token']}"}
    own_consultation = client.patch(
        "/api/v1/appointments/1",
        headers=headers,
        json={"notes": "Tentar alteração"},
    )
    assert own_consultation.status_code == 403
    other_doctor = client.get("/api/v1/appointments/2", headers=headers)
    assert other_doctor.status_code == 404
