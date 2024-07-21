import re
from enum import Enum
from typing import Optional

from fastapi import HTTPException
from pydantic import BaseModel
from pydantic import ConfigDict
from pydantic import EmailStr
from pydantic import constr
from pydantic import validator

LETTER_MATCH_PATTERN = re.compile(r"^[а-яА-Яa-zA-Z\-]+$")


class TunedModel(BaseModel):
    class Config:
        from_attributes = True


class ShowUser(TunedModel):
    user_id: int
    username: str
    name: str
    surname: str
    email: EmailStr
    is_active: bool


class UserCreate(BaseModel):
    username: str
    name: str
    surname: str
    email: EmailStr
    password: str

    @validator("name")
    def validate_name(cls, value):
        if not LETTER_MATCH_PATTERN.match(value):
            raise HTTPException(
                status_code=422, detail="Name should contains only letters"
            )
        return value

    @validator("surname")
    def validate_surname(cls, value):
        if not LETTER_MATCH_PATTERN.match(value):
            raise HTTPException(
                status_code=422, detail="Surname should contains only letters"
            )
        return value


class DeleteUserResponse(BaseModel):
    deleted_user_id: int


class UpdatedUserResponse(BaseModel):
    updated_user_id: int


class UpdateUserRequest(BaseModel):
    name: Optional[constr(min_length=1)]
    surname: Optional[constr(min_length=1)]
    email: Optional[EmailStr]

    @validator("name")
    def validate_name(cls, value):
        if not LETTER_MATCH_PATTERN.match(value):
            raise HTTPException(
                status_code=422, detail="Name should contains only letters"
            )
        return value

    @validator("surname")
    def validate_surname(cls, value):
        if not LETTER_MATCH_PATTERN.match(value):
            raise HTTPException(
                status_code=422, detail="Surname should contains only letters"
            )
        return value


class UserDTO(TunedModel):
    user_id: int
    username: str
    name: str
    surname: str
    email: EmailStr
    is_active: bool
    role: int

    def is_superadmin(self) -> bool:
        return self.role == UserRole.ROLE_SUPERADMIN

    def is_admin(self) -> bool:
        return self.role == UserRole.ROLE_ADMIN


class UserRole(int, Enum):
    ROLE_SUPERADMIN = 0
    ROLE_ADMIN = 1
    ROLE_USER = 2
