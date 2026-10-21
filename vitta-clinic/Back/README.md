# Vitta Clinic API

Backend REST em Flask organizado com application factory, blueprints versionados, modelos SQLAlchemy, schemas Marshmallow e regras de negócio na camada `services`.

## Requisitos e início rápido (Windows PowerShell)

Requer Python 3.11 ou superior.

```powershell
cd Back
py -3.11 -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
Copy-Item .env.example .env
flask --app run.py db upgrade
flask --app run.py seed
flask --app run.py run --debug
```

A API fica disponível em `http://127.0.0.1:5000`; o health check é `GET /health`. O banco padrão é SQLite em `instance/vitta_clinic.db`. O comando `flask seed` também cria as tabelas caso ainda não existam e não duplica uma base que já tenha usuários.

Na primeira instalação, use somente `flask --app run.py db upgrade`; a migração inicial já está incluída. Para reinicializar os dados de desenvolvimento, pare o servidor e remova `instance/vitta_clinic.db`; depois rode novamente `flask --app run.py db upgrade` e `flask --app run.py seed`. Não reutilize as chaves de `.env.example` em produção.

## Contas de demonstração

| Perfil | E-mail | Senha |
| --- | --- | --- |
| Administrador | `admin@vitta.com` | `123456` |
| Médico | `medico@vitta.com` | `123456` |
| Recepcionista | `recepcao@vitta.com` | `123456` |

O seed inclui ainda 3 especialidades, 3 médicos, 5 pacientes, 5 consultas (uma realizada e quatro futuras) e 1 prontuário.

## Autenticação e cURL

### Login e token

```bash
curl -X POST http://127.0.0.1:5000/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email":"admin@vitta.com","password":"123456"}'
```

Copie o `access_token` da resposta. O token de acesso expira em 30 minutos; use o `refresh_token` no endpoint de renovação. Os exemplos protegidos abaixo usam `TOKEN` como variável de ambiente.

```bash
export TOKEN="cole-o-access-token-aqui"
curl http://127.0.0.1:5000/api/v1/auth/me \
  -H "Authorization: Bearer $TOKEN"
```

Para PowerShell, defina `$env:TOKEN = "..."` e use `curl.exe` nos mesmos exemplos.

### Criar paciente

```bash
curl -X POST http://127.0.0.1:5000/api/v1/patients \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"name":"Joana Exemplo","cpf":"529.982.247-25","birth_date":"1990-01-10","phone":"(11) 90000-0000","email":"joana@example.com"}'
```

CPF é validado pelos dígitos verificadores e armazenado somente com números.

### Agendar consulta

```bash
curl -X POST http://127.0.0.1:5000/api/v1/appointments \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"patient_id":1,"doctor_id":2,"date":"2030-05-20","time":"14:30","status":"agendada","notes":"Consulta de rotina"}'
```

### Filtrar agenda e relatórios

```bash
curl "http://127.0.0.1:5000/api/v1/appointments?date_from=2030-05-01&date_to=2030-05-31&status=agendada" \
  -H "Authorization: Bearer $TOKEN"
curl "http://127.0.0.1:5000/api/v1/reports/appointments?date_from=2030-05-01&date_to=2030-05-31" \
  -H "Authorization: Bearer $TOKEN"
```

### Criar prontuário

O médico ou administrador marca primeiro a consulta como realizada; prontuários exigem consulta realizada e só pode existir um por consulta.

```bash
curl -X PATCH http://127.0.0.1:5000/api/v1/appointments/1 \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"status":"realizada"}'
curl -X POST http://127.0.0.1:5000/api/v1/records \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"appointment_id":1,"record_date":"2030-05-20","complaint":"Retorno","diagnosis":"Estável","prescription":"Acompanhamento"}'
```

## Endpoints

Todos os endpoints de negócio ficam em `/api/v1`. Login é público; as demais rotas exigem JWT, exceto `POST /auth/register`, que exige token de administrador.

| Recurso | Rotas |
| --- | --- |
| Autenticação | `POST /auth/login`, `POST /auth/refresh`, `GET /auth/me`, `POST /auth/register` |
| Usuários (admin) | `GET/POST /users`, `GET/PATCH/DELETE /users/{id}` |
| Pacientes | `GET/POST /patients`, `GET/PATCH/DELETE /patients/{id}` |
| Médicos | `GET/POST /doctors`, `GET/PATCH/DELETE /doctors/{id}` |
| Especialidades (admin) | `GET/POST /specialties`, `GET/PATCH/DELETE /specialties/{id}` |
| Consultas | `GET/POST /appointments`, `GET/PATCH/DELETE /appointments/{id}` |
| Prontuários (admin/médico) | `GET/POST /records`, `GET/PATCH/DELETE /records/{id}` |
| Relatórios (admin) | `GET /reports/appointments`, `GET /reports/patients`, `GET /reports/doctors` |

Listagens aceitam filtros: pacientes `search`; médicos `search` e `specialty_id`; consultas `date_from`, `date_to`, `status` e `doctor_id`; prontuários `patient_id`. Administradores podem usar `include_deleted=true` em pacientes.

## Regras e perfis

- Perfis disponíveis: `admin`, `medico`, `recepcionista`; os três usuários de seed usam senha `123456`.
- Usuários, especialidades e relatórios são exclusivos de administradores. `POST /auth/register` também requer administrador.
- Médicos consultam sua própria agenda e prontuários e podem marcar suas consultas como realizadas; recepcionistas agendam consultas e mantêm pacientes.
- CPF (dígitos verificadores) e CRM (UF + número) são validados e únicos.
- Consultas agendadas não podem ficar no passado nem colidir para o mesmo médico ou paciente no mesmo horário. Horários cancelados podem ser reutilizados.
- Prontuários são restritos a médico/admin, só podem ser gravados em consultas realizadas e são únicos por consulta.
- Pacientes com histórico são desativados por soft delete; sem histórico, a linha é removida.
- Respostas de erro seguem JSON `{ "error": "...", "details": ... }`.

## Testes

```powershell
python -m pytest -q
```

Os testes usam SQLite em memória e cobrem autenticação/perfis, CPF, soft delete, datas e conflitos da agenda, e as regras de prontuário. Para aplicar alterações de modelo após o início do projeto, execute `flask --app run.py db migrate -m "Descrição"` e `flask --app run.py db upgrade`.

## Estrutura de pastas

```text
Back/
├── app/
│   ├── models/       # Entidades e relacionamentos SQLAlchemy
│   ├── routes/       # Blueprints REST /api/v1
│   ├── schemas/      # Validação e parsing Marshmallow
│   ├── services/     # Regras de negócio e persistência
│   ├── utils/        # JWT, validações e erros HTTP
│   ├── config.py
│   ├── extensions.py
│   └── seed.py
├── migrations/     # Migração inicial versionada (Flask-Migrate/Alembic)
├── tests/
├── .env.example
├── requirements.txt
└── run.py
```

Este backend é uma base demonstrativa. Para produção, use segredos exclusivos, HTTPS, controle de acesso operacional, backups, logs de auditoria e políticas de privacidade compatíveis com dados de saúde.
