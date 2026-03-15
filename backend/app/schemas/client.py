import re

from pydantic import BaseModel, EmailStr, field_validator


class ClientBase(BaseModel):
    name: str
    document_number: str
    status: str = "active"
    primary_contact_name: str | None = None
    primary_contact_role: str | None = None
    primary_contact_email: EmailStr | None = None
    primary_contact_phone: str | None = None

    @field_validator("document_number")
    @classmethod
    def validate_document_number(cls, value: str) -> str:
        digits = re.sub(r"\D", "", value or "")
        if len(digits) != 14:
            raise ValueError("Informe um CNPJ válido com 14 dígitos.")
        if digits == digits[0] * 14 or not cls._is_valid_cnpj(digits):
            raise ValueError("Informe um CNPJ válido.")
        return cls._format_cnpj(digits)

    @staticmethod
    def _format_cnpj(digits: str) -> str:
        return f"{digits[:2]}.{digits[2:5]}.{digits[5:8]}/{digits[8:12]}-{digits[12:]}"

    @staticmethod
    def _is_valid_cnpj(digits: str) -> bool:
        def calculate_digit(base: str, weights: list[int]) -> str:
            total = sum(int(number) * weight for number, weight in zip(base, weights))
            remainder = total % 11
            return "0" if remainder < 2 else str(11 - remainder)

        first_weights = [5, 4, 3, 2, 9, 8, 7, 6, 5, 4, 3, 2]
        second_weights = [6, 5, 4, 3, 2, 9, 8, 7, 6, 5, 4, 3, 2]
        first_digit = calculate_digit(digits[:12], first_weights)
        second_digit = calculate_digit(digits[:12] + first_digit, second_weights)
        return digits[-2:] == first_digit + second_digit


class ClientCreate(ClientBase):
    pass


class ClientUpdate(ClientBase):
    pass


class ClientRead(BaseModel):
    id: int
    name: str
    document_number: str | None
    status: str

    model_config = {"from_attributes": True}
