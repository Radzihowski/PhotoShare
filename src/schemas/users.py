# Додаємо схеми валідації
import re
from datetime import date, timedelta, datetime
from typing import Optional

from pydantic import BaseModel, Field, field_validator, model_validator

class UserModel(BaseModel): # pydentic class
    email: str
    password: str = Field(min_length=6, max_length=10)


class UserDb(BaseModel):
    avatar: Optional[str]
    id: int
    email: str
    created_at: datetime

    class Config:
        orm_mode = True


class UserResponse(BaseModel):
    user: UserDb
    detail: str = "User successfully created"


class TokenModel(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
