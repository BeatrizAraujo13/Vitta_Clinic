"""Domain-level validation helpers."""

import re


def normalize_cpf(value: str) -> str:
    """Return CPF digits only."""
    return re.sub(r"\D", "", value or "")


def is_valid_cpf(value: str) -> bool:
    """Validate the 11 CPF digits using both check digits."""
    cpf = normalize_cpf(value)
    if len(cpf) != 11 or len(set(cpf)) == 1:
        return False

    def check_digit(length: int) -> int:
        total = sum(int(cpf[index]) * (length + 1 - index) for index in range(length))
        remainder = (total * 10) % 11
        return 0 if remainder == 10 else remainder

    return check_digit(9) == int(cpf[9]) and check_digit(10) == int(cpf[10])


def normalize_crm(value: str) -> str:
    """Normalize CRM strings to `UF 123456`."""
    normalized = re.sub(r"\s+", " ", (value or "").strip().upper())
    match = re.fullmatch(r"(?:CRM-)?([A-Z]{2})\s*[-/]?\s*(\d{4,8})", normalized)
    if not match:
        raise ValueError("CRM inválido. Use o formato CRM-UF 123456.")
    return f"{match.group(1)} {match.group(2)}"


def is_valid_crm(value: str) -> bool:
    """Return whether the CRM has a Brazilian state code and 4 to 8 digits."""
    try:
        normalize_crm(value)
    except ValueError:
        return False
    return True
