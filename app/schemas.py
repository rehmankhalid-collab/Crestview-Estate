import re

from pydantic import BaseModel, field_validator

PHONE_PATTERN = re.compile(r"^[0-9+\-().\s]{7,20}$")


class LeadCreate(BaseModel):
    name: str
    phone: str

    @field_validator("name")
    @classmethod
    def name_not_blank(cls, value: str) -> str:
        value = value.strip()
        if len(value) < 2:
            raise ValueError("Please enter your full name.")
        if len(value) > 120:
            raise ValueError("Name is too long.")
        return value

    @field_validator("phone")
    @classmethod
    def phone_looks_valid(cls, value: str) -> str:
        value = value.strip()
        if not PHONE_PATTERN.match(value):
            raise ValueError("Please enter a valid phone number.")
        return value


class LeadOut(BaseModel):
    success: bool
    message: str
