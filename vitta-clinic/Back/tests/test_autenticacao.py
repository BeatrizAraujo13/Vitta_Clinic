"""Testes de autenticação e acesso por perfil."""


def testar_login_e_atualizacao_de_token_dos_perfis_iniciais(cliente_teste, tokens_teste):
    for email in ("admin@vitta.com", "medico@vitta.com", "recepcao@vitta.com"):
        assert tokens_teste(email)["user"]["email"] == email

    refresh_token = tokens_teste()["refresh_token"]
    refreshed = cliente_teste.post(
        "/api/v1/auth/refresh",
        headers={"Authorization": f"Bearer {refresh_token}"},
    )
    assert refreshed.status_code == 200
    assert refreshed.get_json()["access_token"]


def testar_registros_de_demonstracao_iniciais(cliente_teste, cabecalho_autenticacao):
    assert len(cliente_teste.get("/api/v1/patients", headers=cabecalho_autenticacao).get_json()["items"]) == 5
    assert len(cliente_teste.get("/api/v1/doctors", headers=cabecalho_autenticacao).get_json()["items"]) == 3
    assert len(cliente_teste.get("/api/v1/specialties", headers=cabecalho_autenticacao).get_json()["items"]) == 3
    assert len(cliente_teste.get("/api/v1/appointments", headers=cabecalho_autenticacao).get_json()["items"]) == 5
    assert len(cliente_teste.get("/api/v1/records", headers=cabecalho_autenticacao).get_json()["items"]) == 1


def testar_usuario_atual_exige_token_de_acesso(cliente_teste, tokens_teste):
    login_data = tokens_teste("recepcao@vitta.com")
    response = cliente_teste.get(
        "/api/v1/auth/me",
        headers={"Authorization": f"Bearer {login_data['access_token']}"},
    )
    assert response.status_code == 200
    assert response.get_json()["user"]["role"] == "recepcionista"
    assert cliente_teste.get("/api/v1/auth/me").status_code == 401


def testar_endpoints_administrativos_rejeitam_atendente(cliente_teste, tokens_teste):
    token_data = tokens_teste("recepcao@vitta.com")
    headers = {"Authorization": f"Bearer {token_data['access_token']}"}
    assert cliente_teste.get("/api/v1/users", headers=headers).status_code == 403
    assert cliente_teste.get("/api/v1/specialties", headers=headers).status_code == 403
    assert cliente_teste.get("/api/v1/reports/patients", headers=headers).status_code == 403


def testar_administrador_cadastra_usuario_e_novo_login(cliente_teste, cabecalho_autenticacao):
    payload = {
        "name": "Novo Usuário",
        "email": "novo.usuario@example.com",
        "password": "senha123",
        "role": "recepcionista",
    }
    created = cliente_teste.post("/api/v1/auth/register", headers=cabecalho_autenticacao, json=payload)
    assert created.status_code == 201
    assert created.get_json()["user"]["role"] == "recepcionista"
    entrar = cliente_teste.post(
        "/api/v1/auth/login",
        json={"email": payload["email"], "password": payload["password"]},
    )
    assert entrar.status_code == 200


def testar_atendente_nao_cadastra_usuarios(cliente_teste, tokens_teste):
    token_data = tokens_teste("recepcao@vitta.com")
    response = cliente_teste.post(
        "/api/v1/auth/register",
        headers={"Authorization": f"Bearer {token_data['access_token']}"},
        json={
            "name": "Outro Usuário",
            "email": "outro@example.com",
            "password": "senha123",
            "role": "recepcionista",
        },
    )
    assert response.status_code == 403
