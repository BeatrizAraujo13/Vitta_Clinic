"""Funções auxiliares de validação do domínio."""

import re


def normalizar_cpf(value: str) -> str:
    """Retorna somente os dígitos do CPF."""
    return re.sub(r"\D", "", value or "")


def cpf_valido(value: str) -> bool:
    """Valida os 11 dígitos do CPF usando os dois dígitos verificadores."""
    cpf = normalizar_cpf(value)
    if len(cpf) != 11 or len(set(cpf)) == 1:
        return False

    def digito_verificador(length: int) -> int:
        total = sum(int(cpf[listar]) * (length + 1 - listar) for listar in range(length))
        remainder = (total * 10) % 11
        return 0 if remainder == 10 else remainder

    return digito_verificador(9) == int(cpf[9]) and digito_verificador(10) == int(cpf[10])


def normalizar_crm(value: str) -> str:
    """Padroniza o CRM no formato `UF 123456`."""
    normalized = re.sub(r"\s+", " ", (value or "").strip().upper())
    match = re.fullmatch(r"(?:CRM-)?([A-Z]{2})\s*[-/]?\s*(\d{4,8})", normalized)
    if not match:
        raise ValueError("CRM inválido. Use o formato CRM-UF 123456.")
    return f"{match.group(1)} {match.group(2)}"


def crm_valido(value: str) -> bool:
    """Informa se o CRM contém a sigla de um estado brasileiro e de 4 a 8 dígitos."""
    try:
        normalizar_crm(value)
    except ValueError:
        return False
    return True
