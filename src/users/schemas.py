from typing import Dict
from typing import Self

from pydantic import BaseModel
from pydantic import ConfigDict
from pydantic import EmailStr
from pydantic import ValidationError
from pydantic import model_validator

from src.users.auth import Hasher


class BaseUserDTOSchema(BaseModel):
    """Base User DTO schema"""

    username: str
    first_name: str | None = None
    last_name: str | None = None
    phone_number: str | None = None
    email: EmailStr | None = None


class UserDTOReadSchema(BaseUserDTOSchema):
    """User DTO read schema"""

    id: int

    model_config = ConfigDict(from_attributes=True)


class UserDTOCreateSchema(BaseUserDTOSchema):
    """User DTO create schema"""

    password1: str
    password2: str

    @model_validator(mode="after")
    def check_passwords_match(self) -> Self:
        if not any([self.password1, self.password2]) or self.password1 != self.password2:
            raise ValidationError("passwords do not match")
        return self

    def get_data_to_create(self) -> Dict:
        return {
            "username": self.username,
            "first_name": self.first_name,
            "last_name": self.last_name,
            "phone_number": self.phone_number,
            "email": self.email,
            "password": Hasher.hash_password(self.password1),
        }


class JWTResponseSchema(BaseModel):
    """JWT response schema"""

    access_token: str
    refresh_token: str


class UserDTOSignInSchema(BaseModel):
    """User DTO sign in schema"""

    username: str
    password: str
