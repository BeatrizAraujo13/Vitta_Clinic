"""Testes de datas de consultas e conflitos de agendamento."""

from datetime import date, timedelta


def dados_consulta(**overrides):
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


def testar_rejeicao_de_consulta_passada(cliente_teste, cabecalho_autenticacao):
    response = cliente_teste.post(
        "/api/v1/appointments",
        headers=cabecalho_autenticacao,
        json=dados_consulta(date=(date.today() - timedelta(days=1)).isoformat()),
    )
    assert response.status_code == 400
    assert "passado" in response.get_json()["error"]

    cancelled_past = cliente_teste.post(
        "/api/v1/appointments",
        headers=cabecalho_autenticacao,
        json=dados_consulta(
            date=(date.today() - timedelta(days=1)).isoformat(),
            status="cancelada",
        ),
    )
    assert cancelled_past.status_code == 400


def testar_rejeicao_de_conflito_de_medico_ou_paciente(cliente_teste, cabecalho_autenticacao):
    payload = dados_consulta()
    first = cliente_teste.post("/api/v1/appointments", headers=cabecalho_autenticacao, json=payload)
    assert first.status_code == 201

    doctor_conflict = cliente_teste.post(
        "/api/v1/appointments",
        headers=cabecalho_autenticacao,
        json=dados_consulta(patient_id=3),
    )
    assert doctor_conflict.status_code == 409

    patient_conflict = cliente_teste.post(
        "/api/v1/appointments",
        headers=cabecalho_autenticacao,
        json=dados_consulta(doctor_id=2),
    )
    assert patient_conflict.status_code == 409


def testar_cancelamento_nao_bloqueia_horario(cliente_teste, cabecalho_autenticacao):
    payload = dados_consulta()
    created = cliente_teste.post("/api/v1/appointments", headers=cabecalho_autenticacao, json=payload)
    appointment_id = created.get_json()["appointment"]["id"]
    assert cliente_teste.patch(
        f"/api/v1/appointments/{appointment_id}",
        headers=cabecalho_autenticacao,
        json={"status": "cancelada"},
    ).status_code == 200
    second = cliente_teste.post(
        "/api/v1/appointments",
        headers=cabecalho_autenticacao,
        json=dados_consulta(patient_id=3),
    )
    assert second.status_code == 201


def testar_medico_nao_conclui_consulta_futura(cliente_teste, tokens_teste):
    token_data = tokens_teste("medico@vitta.com")
    response = cliente_teste.patch(
        "/api/v1/appointments/4",
        headers={"Authorization": f"Bearer {token_data['access_token']}"},
        json={"status": "realizada"},
    )
    assert response.status_code == 400
    assert "futura" in response.get_json()["error"]
