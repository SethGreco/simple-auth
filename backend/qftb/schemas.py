from pydantic import BaseModel, field_validator, EmailStr, Field, ConfigDict
from pydantic.alias_generators import to_camel
import re
from typing import Optional, List


class BaseSchema(BaseModel):
    model_config = ConfigDict(
        alias_generator=to_camel, populate_by_name=True, from_attributes=True
    )


class CreateUser(BaseSchema):
    first_name: str = Field(min_length=1)
    last_name: str = Field(min_length=1)
    email: EmailStr
    password: str

    @field_validator("password")
    @classmethod
    def min_length_password(cls, password: str) -> str:
        has_number = re.search(r"\d", password) is not None
        has_uppercase = re.search(r"[A-Z]", password) is not None
        if len(password) <= 11:
            raise ValueError("password must be twelve character minimum")
        elif has_number is False:
            raise ValueError("password must contain at least one number")
        elif has_uppercase is False:
            raise ValueError("password must contain at least one uppercase letter")
        return password


class UserResponse(BaseSchema):
    id: int
    first_name: str
    last_name: str
    email: str


class AdminUserView(BaseSchema):
    first_name: str
    last_name: str
    email: str
    hashed_password: str


class Login(BaseModel):
    username: str
    password: str


class Token(BaseSchema):
    access_token: str
    token_type: str


class Error(BaseModel):
    loc: Optional[List[str]] = None
    msg: str
    type: str


class ErrorResponse(BaseModel):
    detail: List[Error]


class Message(BaseModel):
    detail: str
