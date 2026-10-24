"""Testes de situação e titularidade dos prontuários."""

from datetime import date, timedelta

from app.extensoes import db
from app.models import Consulta


def dados_prontuario(appointment_id):
    return {
        "appointment_id": appointment_id,
        "record_date": date.today().isoformat(),
        "complaint": "Acompanhamento",
        "diagnosis": "Paciente estável",
        "prescription": "Retorno de rotina",
    }


def testar_prontuario_exige_consulta_concluida_e_unica(cliente_teste, cabecalho_autenticacao):
    scheduled = cliente_teste.post(
        "/api/v1/records",
        headers=cabecalho_autenticacao,
        json=dados_prontuario(2),
    )
    assert scheduled.status_code == 409

    with cliente_teste.application.app_context():
        appointment = db.session.get(Consulta, 2)
        appointment.appointment_date = date.today() - timedelta(days=1)
        db.session.commit()

    completed = cliente_teste.patch(
        "/api/v1/appointments/2",
        headers=cabecalho_autenticacao,
        json={"status": "realizada"},
    )
    assert completed.status_code == 200
    created = cliente_teste.post(
        "/api/v1/records",
        headers=cabecalho_autenticacao,
        json=dados_prontuario(2),
    )
    assert created.status_code == 201
    duplicate = cliente_teste.post(
        "/api/v1/records",
        headers=cabecalho_autenticacao,
        json=dados_prontuario(2),
    )
    assert duplicate.status_code == 409


def testar_medico_atualiza_somente_status_de_sua_consulta(cliente_teste, tokens_teste):
    token_data = tokens_teste("medico@vitta.com")
    headers = {"Authorization": f"Bearer {token_data['access_token']}"}
    own_consultation = cliente_teste.patch(
        "/api/v1/appointments/1",
        headers=headers,
        json={"notes": "Tentar alteração"},
    )
    assert own_consultation.status_code == 403
    other_doctor = cliente_teste.get("/api/v1/appointments/2", headers=headers)
    assert other_doctor.status_code == 404
