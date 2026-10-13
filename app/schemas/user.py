from datetime import datetime
from typing import Literal

from pydantic import BaseModel, ConfigDict, EmailStr, Field


class UserCreate(BaseModel):
    full_name: str = Field(..., min_length=2, max_length=100)
    email: EmailStr
    phone: str | None = Field(default=None, max_length=20)
    password: str = Field(..., min_length=8, max_length=100)


class UserLogin(BaseModel):
    email: EmailStr
    password: str


class UserUpdate(BaseModel):
    full_name: str | None = Field(default=None, min_length=2, max_length=100)
    phone: str | None = Field(default=None, max_length=20)


class UserResponse(BaseModel):
    id: int
    full_name: str
    email: EmailStr
    phone: str | None
    role: Literal["Admin", "Doctor", "Patient"]
    is_active: bool
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class UserRoleUpdate(BaseModel):
    role: Literal["Admin", "Doctor", "Patient"]