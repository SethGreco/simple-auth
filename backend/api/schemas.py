from pydantic import BaseModel, field_validator, EmailStr


class CreateUser(BaseModel):
    first_name: str
    last_name: str
    email: EmailStr
    password: str

    @field_validator("last_name", "first_name")
    @classmethod
    def min_length_name(cls, fname: str) -> str:
        if len(fname) <= 0:
            raise ValueError("name fields cannot be empty")
        return fname.title()

    @field_validator("password")
    @classmethod
    def min_length_password(cls, password: str) -> str:
        if len(password) <= 11:
            raise ValueError("password must be 12 character minimum")
        return password


class UserResponse(BaseModel):
    id: int
    first_name: str
    last_name: str
    email: str


class AdminUserView(BaseModel):
    first_name: str
    last_name: str
    email: str
    hashed_password: str


class Login(BaseModel):
    username: str
    password: str


class Token(BaseModel):
    access_token: str
    token_type: str
