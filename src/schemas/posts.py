import re
from datetime import date, timedelta, datetime
from typing import Optional

from pydantic import BaseModel, Field, field_validator, model_validator


class PostsRequest(BaseModel):  # визначаємо вхідні дані
    description: str|None = Field(max_length=2056)

class PostResponce(BaseModel):  # визначаємо вихідні дані
    id: int