"""Doctor and CRM validation tests."""


def doctor_payload(**overrides):
    payload = {
        "name": "Médico de Teste",
        "crm": "RJ 123456",
        "specialty_id": 1,
        "email": "medico.teste@example.com",
        "phone": "(21) 90000-0000",
        "schedule": "Seg a sex, 08:00–17:00",
    }
    payload.update(overrides)
    return payload


def test_crm_format_and_uniqueness_are_validated(client, auth_header):
    invalid = client.post(
        "/api/v1/doctors",
        headers=auth_header,
        json=doctor_payload(crm="XYZ 123456"),
    )
    assert invalid.status_code == 400
    assert "CRM inválido" in invalid.get_json()["error"]

    duplicate = client.post(
        "/api/v1/doctors",
        headers=auth_header,
        json=doctor_payload(crm="CRM-SP 123456"),
    )
    assert duplicate.status_code == 409

    created = client.post(
        "/api/v1/doctors",
        headers=auth_header,
        json=doctor_payload(),
    )
    assert created.status_code == 201
    assert created.get_json()["doctor"]["crm"] == "RJ 123456"
