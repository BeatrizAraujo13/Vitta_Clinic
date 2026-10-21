"""Patient validation, uniqueness and deletion behavior."""


def patient_payload(**overrides):
    payload = {
        "name": "Paciente de Teste",
        "cpf": "111.222.333-96",
        "birth_date": "1990-01-01",
        "phone": "(11) 90000-0000",
        "email": "paciente.teste@example.com",
        "address": "Rua de Teste, 10",
        "insurance": "Particular",
        "notes": "",
    }
    payload.update(overrides)
    return payload


def test_patient_requires_valid_unique_cpf(client, auth_header):
    invalid = client.post(
        "/api/v1/patients",
        headers=auth_header,
        json=patient_payload(cpf="123.456.789-00"),
    )
    assert invalid.status_code == 400
    assert "CPF inválido" in invalid.get_json()["error"]

    duplicate = client.post(
        "/api/v1/patients",
        headers=auth_header,
        json=patient_payload(cpf="529.982.247-25"),
    )
    assert duplicate.status_code == 409


def test_patient_without_history_is_removed_and_history_is_soft_deleted(client, auth_header):
    created = client.post(
        "/api/v1/patients",
        headers=auth_header,
        json=patient_payload(),
    )
    assert created.status_code == 201
    patient_id = created.get_json()["patient"]["id"]
    removed = client.delete(f"/api/v1/patients/{patient_id}", headers=auth_header)
    assert removed.status_code == 200
    assert removed.get_json()["soft_deleted"] is False

    historical = client.delete("/api/v1/patients/1", headers=auth_header)
    assert historical.status_code == 200
    assert historical.get_json()["soft_deleted"] is True
    assert all(item["id"] != 1 for item in client.get("/api/v1/patients", headers=auth_header).get_json()["items"])
    assert any(
        item["id"] == 1
        for item in client.get("/api/v1/patients?include_deleted=true", headers=auth_header).get_json()["items"]
    )
