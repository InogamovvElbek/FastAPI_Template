from decimal import Decimal
from typing import Optional

import bcrypt
from pydantic import BaseModel, EmailStr, field_validator, model_validator
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
    username: str
    password: str

    @model_validator(mode='after')
    def validate__entire_model(self):
        with Session(engine) as session:
            user = session.exec(select(User).where(User.username == self.username)).first()
        if not user:
            raise ValueError("User topilmadi !")
        if not bcrypt.checkpw(self.password.encode(), user.password.encode()):
            raise ValueError("Password xato !")
        return self


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