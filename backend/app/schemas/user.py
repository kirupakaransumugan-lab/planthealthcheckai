import re

from pydantic import BaseModel, Field, field_validator

from app.security import check_password_strength


EMAIL_PATTERN = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")


# ---------- Requests ----------

class RegisterRequest(BaseModel):
    name: str = Field(min_length=1, max_length=100)
    email: str = Field(max_length=255)
    password: str = Field(max_length=128)

    @field_validator("name")
    @classmethod
    def clean_name(cls, value: str) -> str:
        value = value.strip()

        if not value:
            raise ValueError("Please enter your name.")

        return value

    @field_validator("email")
    @classmethod
    def clean_email(cls, value: str) -> str:
        value = value.strip().lower()

        if not EMAIL_PATTERN.match(value):
            raise ValueError("Please enter a valid email address.")

        return value

    @field_validator("password")
    @classmethod
    def strong_password(cls, value: str) -> str:
        problem = check_password_strength(value)

        if problem:
            raise ValueError(problem)

        return value


class LoginRequest(BaseModel):
    email: str = Field(max_length=255)
    password: str = Field(min_length=1, max_length=128)

    @field_validator("email")
    @classmethod
    def clean_email(cls, value: str) -> str:
        return value.strip().lower()


# ---------- Responses (the structured JSON the API returns) ----------

class UserOut(BaseModel):
    id: int
    name: str
    email: str


class AuthResponse(BaseModel):
    token: str = Field(description="JWT to send as 'Authorization: Bearer <token>'.")
    user: UserOut


class MeResponse(BaseModel):
    user: UserOut
