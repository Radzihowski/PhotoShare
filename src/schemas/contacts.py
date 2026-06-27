import re
from datetime import date, timedelta, datetime
from typing import Optional

from pydantic import BaseModel, Field, field_validator, model_validator


class ContactRequest(BaseModel):  # визначаємо вхідні дані
    first_name: str = Field(max_length=56, min_length=2)
    last_name: str = Field(max_length=56, min_length=2)
    email: str = Field()
    phone: str = Field()
    date_of_birth: date = Field()
    info: str | None = Field(max_length=1024)

    @field_validator('email', mode='before')
    @classmethod
    def email_checker(cls, value: str) -> str:
        regex = re.compile(r'([A-Za-z0-9]+[.-_])*[A-Za-z0-9]+@[A-Za-z0-9-]+(\.[A-Z|a-z]{2,})+')
        if re.fullmatch(regex, value):
            return value
        else:
            raise ValueError('Email not valid')

    @field_validator('date_of_birth', mode='before')
    @classmethod
    def date_of_birth_checker(cls, value: str) -> date:
        birth_day = datetime.strptime(value, "%Y-%m-%d").date()
        date_18 = (datetime.now() - timedelta(days=18 * 365)).date()
        if date_18 < birth_day:
            raise ValueError("User must be 18+")
        else:
            return birth_day


class ContactResponse(BaseModel):  # визначаємо вихідні дані повертає айдішнік інт
    id: int

    class Config:
        from_attributes = True

class ContactInfo(BaseModel):
    id: int
    first_name: str
    last_name: str
    email: str
    phone: str
    date_of_birth: date
    info: str | None

class ContactUpdateRequest(BaseModel):
    first_name: Optional[str] = ""
    last_name: Optional[str] = ""
    email: Optional[str] = ""
    phone: Optional[str] = ""
    date_of_birth: Optional[date] = None
    info: Optional[str] = ""

    @model_validator(mode="after")
    def at_least_one_field(self):
        if all([
            self.first_name == "",
            self.last_name == "",
            self.email == "",
            self.phone == "",
            self.date_of_birth is None,
            self.info == ""
        ]):
            raise ValueError("At least one field must be provided for update.")
        return self