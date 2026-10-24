"""Criptografia autenticada de campos sensíveis persistidos no banco."""

import base64
import binascii
import os
from datetime import date, datetime

from cryptography.exceptions import InvalidTag
from cryptography.hazmat.primitives.ciphers.aead import AESGCM
from flask import current_app
from sqlalchemy.types import Text, TypeDecorator


_PREFIXO = "v1:"
_TAMANHO_NONCE = 12


def decodificar_chave(chave: str | None) -> bytes:
    if not chave:
        raise RuntimeError(
            "Configure DATA_ENCRYPTION_KEY no arquivo .env com uma chave "
            "aleatória de 32 bytes codificada em Base64 URL-safe."
        )
    try:
        chave_bytes = base64.b64decode(chave.encode("ascii"), altchars=b"-_", validate=True)
    except (UnicodeEncodeError, binascii.Error) as erro:
        raise RuntimeError("DATA_ENCRYPTION_KEY deve ser uma chave Base64 URL-safe válida.") from erro
    if len(chave_bytes) != 32:
        raise RuntimeError("DATA_ENCRYPTION_KEY deve representar exatamente 32 bytes.")
    return chave_bytes


def cifrar_valor(valor: str, chave: bytes, contexto: str) -> str:
    nonce = os.urandom(_TAMANHO_NONCE)
    cifra = AESGCM(chave).encrypt(nonce, valor.encode("utf-8"), contexto.encode("utf-8"))
    conteudo = base64.urlsafe_b64encode(nonce + cifra).decode("ascii")
    return _PREFIXO + conteudo


def decifrar_valor(valor: str, chave: bytes, contexto: str) -> str:
    if not valor.startswith(_PREFIXO):
        raise ValueError("O dado persistido não possui um formato de criptografia reconhecido.")
    try:
        conteudo = base64.b64decode(valor[len(_PREFIXO):].encode("ascii"), altchars=b"-_", validate=True)
    except (UnicodeEncodeError, binascii.Error) as erro:
        raise ValueError("O dado criptografado está malformado.") from erro
    if len(conteudo) < _TAMANHO_NONCE + 16:
        raise ValueError("O dado criptografado está incompleto.")
    nonce, cifra = conteudo[:_TAMANHO_NONCE], conteudo[_TAMANHO_NONCE:]
    try:
        texto = AESGCM(chave).decrypt(nonce, cifra, contexto.encode("utf-8"))
    except InvalidTag as erro:
        raise ValueError("Não foi possível autenticar o dado criptografado.") from erro
    return texto.decode("utf-8")


class TextoCriptografado(TypeDecorator):
    impl = Text
    cache_ok = True

    def __init__(self, contexto: str):
        super().__init__()
        self.contexto = contexto

    def process_bind_param(self, valor, dialect):
        if valor is None:
            return None
        return cifrar_valor(str(valor), current_app.config["CHAVE_CIFRAGEM"], self.contexto)

    def process_result_value(self, valor, dialect):
        if valor is None:
            return None
        return decifrar_valor(valor, current_app.config["CHAVE_CIFRAGEM"], self.contexto)


class DataCriptografada(TextoCriptografado):
    def process_bind_param(self, valor, dialect):
        if valor is None:
            return None
        if isinstance(valor, datetime):
            valor = valor.date()
        if not isinstance(valor, date):
            raise TypeError("O valor de data criptografado deve ser uma data.")
        return cifrar_valor(valor.isoformat(), current_app.config["CHAVE_CIFRAGEM"], self.contexto)

    def process_result_value(self, valor, dialect):
        texto = super().process_result_value(valor, dialect)
        return date.fromisoformat(texto) if texto is not None else None
