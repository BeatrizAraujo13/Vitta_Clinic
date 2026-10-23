"""Testes de médicos e validação do CRM."""


def dados_medico(**overrides):
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


def testar_formato_e_unicidade_do_crm(cliente_teste, cabecalho_autenticacao):
    invalid = cliente_teste.post(
        "/api/v1/doctors",
        headers=cabecalho_autenticacao,
        json=dados_medico(crm="XYZ 123456"),
    )
    assert invalid.status_code == 400
    assert "CRM inválido" in invalid.get_json()["error"]

    duplicate = cliente_teste.post(
        "/api/v1/doctors",
        headers=cabecalho_autenticacao,
        json=dados_medico(crm="CRM-SP 123456"),
    )
    assert duplicate.status_code == 409

    created = cliente_teste.post(
        "/api/v1/doctors",
        headers=cabecalho_autenticacao,
        json=dados_medico(),
    )
    assert created.status_code == 201
    assert created.get_json()["doctor"]["crm"] == "RJ 123456"
