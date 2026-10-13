from decimal import Decimal
from typing import Optional

import bcrypt
from pydantic import BaseModel, EmailStr, field_validator
from sqlmodel import Session, select

from apps.models import engine, User


class ProductForm(BaseModel):
    title: Optional[str] = None
    price: Optional[Decimal] = None
    photo: Optional[str] = None
    category_id: Optional[int] = None


class ProfileResponse(BaseModel):
    id: int
    name: str
    age: int
    username: str


class RefreshTokenRequest(BaseModel):
    refresh_token: str


class LoginForm(BaseModel):
    """Faqat shakl/validatsiya. Login logikasi (userni topish, parolni
    tekshirish) view funksiyasida (apps/views/auth.py) amalga oshiriladi."""
    username: str
    password: str


class VerifyOTPForm(BaseModel):
    email: EmailStr
    code: str


class Token(BaseModel):
    access_token: str
    token_type: str
    refresh_token: str


class RegisterForm(BaseModel):
    name: str
    email: EmailStr
    age: int
    username: str
    password: str

    @field_validator('username')
    @classmethod
    def validate_username(cls, value: str):
        with Session(engine) as session:
            data = session.exec(select(User).where(User.username == value)).all()
        if data:
            raise ValueError("Bunday username oldin takrorlangan")
        return value

    @field_validator('email')
    @classmethod
    def validate_email(cls, value: str):
        with Session(engine) as session:
            data = session.exec(select(User).where(User.email == value)).all()
        if data:
            raise ValueError("Bu email oldin ro'yxatdan o'tgan")
        return value

    @field_validator('password')
    @classmethod
    def validate_password(cls, value: str):
        return bcrypt.hashpw(value.encode(), salt=bcrypt.gensalt()).decode()