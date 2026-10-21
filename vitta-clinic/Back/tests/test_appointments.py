"""Appointment date and scheduling conflict tests."""

from datetime import date, timedelta


def appointment_payload(**overrides):
    payload = {
        "patient_id": 2,
        "doctor_id": 1,
        "date": (date.today() + timedelta(days=7)).isoformat(),
        "time": "15:15",
        "status": "agendada",
        "notes": "",
    }
    payload.update(overrides)
    return payload


def test_past_appointment_is_rejected(client, auth_header):
    response = client.post(
        "/api/v1/appointments",
        headers=auth_header,
        json=appointment_payload(date=(date.today() - timedelta(days=1)).isoformat()),
    )
    assert response.status_code == 400
    assert "passado" in response.get_json()["error"]

    cancelled_past = client.post(
        "/api/v1/appointments",
        headers=auth_header,
        json=appointment_payload(
            date=(date.today() - timedelta(days=1)).isoformat(),
            status="cancelada",
        ),
    )
    assert cancelled_past.status_code == 400


def test_conflict_for_same_doctor_or_patient_is_rejected(client, auth_header):
    payload = appointment_payload()
    first = client.post("/api/v1/appointments", headers=auth_header, json=payload)
    assert first.status_code == 201

    doctor_conflict = client.post(
        "/api/v1/appointments",
        headers=auth_header,
        json=appointment_payload(patient_id=3),
    )
    assert doctor_conflict.status_code == 409

    patient_conflict = client.post(
        "/api/v1/appointments",
        headers=auth_header,
        json=appointment_payload(doctor_id=2),
    )
    assert patient_conflict.status_code == 409


def test_cancelled_appointment_does_not_block_slot(client, auth_header):
    payload = appointment_payload()
    created = client.post("/api/v1/appointments", headers=auth_header, json=payload)
    appointment_id = created.get_json()["appointment"]["id"]
    assert client.patch(
        f"/api/v1/appointments/{appointment_id}",
        headers=auth_header,
        json={"status": "cancelada"},
    ).status_code == 200
    second = client.post(
        "/api/v1/appointments",
        headers=auth_header,
        json=appointment_payload(patient_id=3),
    )
    assert second.status_code == 201


def test_doctor_cannot_mark_future_consultation_as_completed(client, tokens):
    token_data = tokens("medico@vitta.com")
    response = client.patch(
        "/api/v1/appointments/4",
        headers={"Authorization": f"Bearer {token_data['access_token']}"},
        json={"status": "realizada"},
    )
    assert response.status_code == 400
    assert "futura" in response.get_json()["error"]
