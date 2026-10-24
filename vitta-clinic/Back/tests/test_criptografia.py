import pytest
from sqlalchemy import text

from app import criar_aplicacao
from app.extensoes import db
from app.models import Paciente
from app.utils.criptografia import cifrar_valor, decifrar_valor, decodificar_chave


def test_chave_de_criptografia_e_obrigatoria():
    with pytest.raises(RuntimeError, match="DATA_ENCRYPTION_KEY"):
        decodificar_chave(None)

    with pytest.raises(RuntimeError, match="32 bytes"):
        decodificar_chave("dG9vLXNob3J0")


def test_aes_gcm_cifra_e_detecta_adulteracao(app):
    with app.app_context():
        chave = app.config["CHAVE_CIFRAGEM"]
        cifra = cifrar_valor("informação clínica", chave, "medical_records.notes")

        assert cifra.startswith("v1:")
        assert "informação clínica" not in cifra
        assert decifrar_valor(cifra, chave, "medical_records.notes") == "informação clínica"

        adulterada = cifra[:-2] + ("AA" if cifra[-2:] != "AA" else "BB")
        with pytest.raises(ValueError, match="autenticar"):
            decifrar_valor(adulterada, chave, "medical_records.notes")

        with pytest.raises(ValueError, match="autenticar"):
            decifrar_valor(cifra, chave, "medical_records.complaint")


def test_campos_pessoais_sao_cifrados_no_banco_e_abertos_no_modelo(app):
    with app.app_context():
        registro_bruto = db.session.execute(
            text("SELECT birth_date, phone, email, address FROM patients WHERE id = 1")
        ).one()
        paciente = db.session.get(Paciente, 1)

        assert registro_bruto.birth_date.startswith("v1:")
        assert registro_bruto.phone.startswith("v1:")
        assert registro_bruto.email.startswith("v1:")
        assert registro_bruto.address.startswith("v1:")
        assert paciente.birth_date.isoformat() == "1988-04-12"
        assert paciente.phone == "(11) 99911-2233"
        assert paciente.email == "ana.lima@email.com"
        assert paciente.address.startswith("Rua das Flores")


def test_aplicacao_rejeita_chave_de_criptografia_ausente():
    class ConfiguracaoSemChave:
        TESTING = True
        SECRET_KEY = "test-secret-key-that-is-at-least-32-bytes"
        JWT_SECRET_KEY = "test-jwt-secret-key-that-is-at-least-32-bytes"
        DATA_ENCRYPTION_KEY = None
        SQLALCHEMY_DATABASE_URI = "sqlite://"
        CORS_ORIGINS = []

    with pytest.raises(RuntimeError, match="DATA_ENCRYPTION_KEY"):
        criar_aplicacao(ConfiguracaoSemChave)
