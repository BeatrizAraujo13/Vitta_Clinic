"""Authentication and role-access tests."""


def test_seeded_roles_can_login_and_refresh(client, tokens):
    for email in ("admin@vitta.com", "medico@vitta.com", "recepcao@vitta.com"):
        assert tokens(email)["user"]["email"] == email

    refresh_token = tokens()["refresh_token"]
    refreshed = client.post(
        "/api/v1/auth/refresh",
        headers={"Authorization": f"Bearer {refresh_token}"},
    )
    assert refreshed.status_code == 200
    assert refreshed.get_json()["access_token"]


def test_seed_contains_requested_demo_records(client, auth_header):
    assert len(client.get("/api/v1/patients", headers=auth_header).get_json()["items"]) == 5
    assert len(client.get("/api/v1/doctors", headers=auth_header).get_json()["items"]) == 3
    assert len(client.get("/api/v1/specialties", headers=auth_header).get_json()["items"]) == 3
    assert len(client.get("/api/v1/appointments", headers=auth_header).get_json()["items"]) == 5
    assert len(client.get("/api/v1/records", headers=auth_header).get_json()["items"]) == 1


def test_current_user_requires_access_token(client, tokens):
    login_data = tokens("recepcao@vitta.com")
    response = client.get(
        "/api/v1/auth/me",
        headers={"Authorization": f"Bearer {login_data['access_token']}"},
    )
    assert response.status_code == 200
    assert response.get_json()["user"]["role"] == "recepcionista"
    assert client.get("/api/v1/auth/me").status_code == 401


def test_admin_only_endpoints_reject_receptionist(client, tokens):
    token_data = tokens("recepcao@vitta.com")
    headers = {"Authorization": f"Bearer {token_data['access_token']}"}
    assert client.get("/api/v1/users", headers=headers).status_code == 403
    assert client.get("/api/v1/specialties", headers=headers).status_code == 403
    assert client.get("/api/v1/reports/patients", headers=headers).status_code == 403


def test_admin_can_register_user_and_new_account_can_login(client, auth_header):
    payload = {
        "name": "Novo Usuário",
        "email": "novo.usuario@example.com",
        "password": "senha123",
        "role": "recepcionista",
    }
    created = client.post("/api/v1/auth/register", headers=auth_header, json=payload)
    assert created.status_code == 201
    assert created.get_json()["user"]["role"] == "recepcionista"
    login = client.post(
        "/api/v1/auth/login",
        json={"email": payload["email"], "password": payload["password"]},
    )
    assert login.status_code == 200


def test_receptionist_cannot_register_users(client, tokens):
    token_data = tokens("recepcao@vitta.com")
    response = client.post(
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
