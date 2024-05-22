import re
from typing import List, Optional

from pydantic import BaseModel, ConfigDict, EmailStr, Field, field_validator
from pydantic.alias_generators import to_camel


class BaseSchema(BaseModel):
    model_config = ConfigDict(alias_generator=to_camel, populate_by_name=True, from_attributes=True)


class CreateUser(BaseSchema):
    first_name: str = Field(min_length=1)
    last_name: str = Field(min_length=1)
    email: EmailStr
    password: str

    @field_validator("password")
    @classmethod
    def min_length_password(cls, password: str) -> str:
        password_pattern = r"^(?=.*[A-Z])(?=.*\d)[A-Za-z\d]{12,}$"
        valid_password = re.match(password_pattern, password)

        if valid_password is None:
            raise ValueError("password much contain 12 characters, 1 uppercase and 1 number")
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
