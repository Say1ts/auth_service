import re
from enum import Enum
from typing import Optional

from fastapi import HTTPException
from pydantic import BaseModel
from pydantic import EmailStr
from pydantic import field_validator

LETTER_MATCH_PATTERN = re.compile(r"^[а-яА-Яa-zA-Z\-]+$")


class TunedModel(BaseModel):
    class Config:
        from_attributes = True


class NameMixture(BaseModel):
    name: Optional[str]
    surname: Optional[str]

    @field_validator("name")
    def validate_name(cls, value):
        if not LETTER_MATCH_PATTERN.match(value):
            raise HTTPException(
                status_code=422, detail="Name should contains only letters"
            )
        return value

    @field_validator("surname")
    def validate_surname(cls, value):
        if not LETTER_MATCH_PATTERN.match(value):
            raise HTTPException(
                status_code=422, detail="Surname should contains only letters"
            )
        return value


class ShowUser(TunedModel):
    user_id: int
    username: str
    email: EmailStr


class UserCreate(BaseModel):
    username: str
    email: EmailStr
    password: str


class DeleteUserResponse(BaseModel):
    deleted_user_id: int


class UpdatedUserResponse(BaseModel):
    updated_user_id: int


class UpdateUserRequest(BaseModel):
    email: Optional[EmailStr]


class UserDTO(TunedModel):
    user_id: int
    username: str
    email: EmailStr
    is_active: bool
    role: int

    hashed_password: str

    def is_superadmin(self) -> bool:
        return self.role == UserRole.ROLE_SUPERADMIN

    def is_admin(self) -> bool:
        return self.role == UserRole.ROLE_ADMIN


class UserRole(int, Enum):
    ROLE_SUPERADMIN = 0
    ROLE_ADMIN = 1
    ROLE_USER = 2
