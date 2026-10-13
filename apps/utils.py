import os
import secrets
import smtplib
from datetime import timedelta, datetime, timezone
from email.message import EmailMessage
from typing import Optional
import jwt
import redis
from fastapi import HTTPException
from starlette import status
from dotenv import load_dotenv

load_dotenv()

SECRET_KEY = os.getenv("SECRET_KEY")
if not SECRET_KEY:
    raise RuntimeError("SECRET_KEY aniqlanmagan! .env faylida SECRET_KEY ni belgilang.")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30
REFRESH_TOKEN_EXPIRE_DAYS = 7

SMTP_HOST = (os.getenv("EMAIL_HOST") or "smtp.gmail.com").strip()
SMTP_PORT = int(os.getenv("EMAIL_PORT") or 587)
SMTP_USER = os.getenv("EMAIL_HOST_USER")
SMTP_PASSWORD = os.getenv("EMAIL_HOST_PASSWORD")

OTP_TTL_SECONDS = 300
redis_client = redis.Redis.from_url(
    os.getenv("REDIS_URL", "redis://localhost:6379/0"), decode_responses=True
)


def save_otp(email: str, code: str) -> None:
    """Kodni Redis'da 5 daqiqaga saqlaydi (eskisi almashtiriladi)"""
    redis_client.set(f"otp:{email}", code, ex=OTP_TTL_SECONDS)


def check_otp(email: str, code: str) -> bool:

    saved = redis_client.get(f"otp:{email}")
    if saved is None or not secrets.compare_digest(saved, code):
        return False
    redis_client.delete(f"otp:{email}")
    return True


def generate_otp() -> str:
    return str(secrets.randbelow(10 ** 6)).zfill(6)


def send_otp_email(email: str, code: str) -> None:
    msg = EmailMessage()
    msg["Subject"] = "Tasdiqlash kodingiz"
    msg["From"] = SMTP_USER
    msg["To"] = email
    msg.set_content(f"Sizning tasdiqlash kodingiz: {code}\n\nKod 5 daqiqa amal qiladi.")

    if SMTP_PORT == 465:
        server = smtplib.SMTP_SSL(SMTP_HOST, SMTP_PORT, timeout=15)
    else:
        server = smtplib.SMTP(SMTP_HOST, SMTP_PORT, timeout=15)
        server.starttls()
    with server:
        server.login(SMTP_USER, SMTP_PASSWORD)
        server.send_message(msg)

def create_token(data: dict, expires_delta: Optional[timedelta] = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(minutes=15)

    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


def create_access_and_refresh_tokens(user_id: str):
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_token(
        data={"sub": user_id, "type": "access"},
        expires_delta=access_token_expires
    )

    refresh_token_expires = timedelta(days=REFRESH_TOKEN_EXPIRE_DAYS)
    refresh_token = create_token(
        data={"sub": user_id, "type": "refresh"},
        expires_delta=refresh_token_expires
    )

    return access_token, refresh_token


def verify_token(token: str, token_type: str = "access"):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        token_type_from_token: str = payload.get("type")

        if username is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token"
            )

        if token_type_from_token != token_type:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail=f"Invalid token type. Expected {token_type}"
            )

        return username
    except jwt.ExpiredSignatureError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token expired"
        )
    except jwt.InvalidTokenError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token"
        )